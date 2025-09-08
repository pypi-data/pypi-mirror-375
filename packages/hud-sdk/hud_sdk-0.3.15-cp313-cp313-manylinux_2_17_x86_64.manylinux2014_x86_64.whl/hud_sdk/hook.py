import ast
import importlib
import os
import random
import re
import sys
import time
import traceback
import types
from functools import wraps
from importlib.machinery import ModuleSpec, SourceFileLoader
from site import ENABLE_USER_SITE, getsitepackages, getusersitepackages
from threading import Timer
from types import CodeType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    TypeVar,
    Union,
    cast,
)
from zlib import crc32

from ._internal import worker_queue
from .collectors.modules import get_pre_init_loaded_modules
from .config import config
from .declarations import Declaration, FileToParse
from .exception_handler import install_exception_handler
from .forkable import register_fork_callbacks
from .instrumentation import instrument_frameworks
from .logging import internal_logger, user_logger
from .run_mode import disable_hud, should_run_hud
from .users_logs import UsersLogs
from .utils import calculate_uuid

FunctionDef = TypeVar("FunctionDef", ast.FunctionDef, ast.AsyncFunctionDef)

paths_blacklist: List[str] = [
    *getsitepackages(),  # All site packages directories (venv and system if each applicable)
]

if random.__spec__.origin is not None:
    paths_blacklist.append(
        os.path.dirname(random.__spec__.origin)
    )  # Python standard library directory

if __spec__.origin is not None:
    paths_blacklist.append(
        os.path.dirname(__spec__.origin)
    )  # The directory of the hud_sdk package

if ENABLE_USER_SITE:
    paths_blacklist.append(getusersitepackages())

# The whitelist overrides the blacklist, so if a path (or subpath) is in both, it will not be blacklisted
paths_whitelist: List[str] = []


def is_path_disallowed(path: str) -> bool:
    """
    Check if the given path is blacklisted.
    """
    abs_path = os.path.abspath(path)
    for blacklisted in paths_blacklist:
        if abs_path.startswith(blacklisted + os.path.sep):
            return not is_path_in_whitelist(abs_path)
    return False


def is_path_in_whitelist(path: str) -> bool:
    """
    Check if the given path is whitelisted.
    """
    abs_path = os.path.abspath(path)
    for whitelisted in paths_whitelist:
        if abs_path.startswith(whitelisted + os.path.sep):
            return True
    return False


class ASTTransformer(ast.NodeTransformer):
    def __init__(self, path: str, code: bytes, file_hash: int) -> None:
        self.path = path
        self.file_hash = file_hash
        self.compiler_flags = 0
        self.instrumented_functions = 0

    @staticmethod
    def get_and_remove_docstring(
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Optional[ast.stmt]:
        """
        If the first expression in the function is a literal string (docstring), remove it and return it
        """

        AstStrType = ast.Constant if sys.version_info >= (3, 8) else ast.Str

        if not node.body:
            return None
        if (
            isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, AstStrType)
            and (
                isinstance(node.body[0].value.value, str)
                if sys.version_info >= (3, 8)
                else isinstance(node.body[0].value.s, str)
            )
        ):
            return node.body.pop(0)
        return None

    @staticmethod
    def get_with_location_from_node(node: FunctionDef) -> Dict[str, int]:
        if len(node.body) == 0:
            return {
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            }

        return {
            "lineno": node.body[0].lineno,
            "col_offset": node.body[0].col_offset,
            "end_lineno": getattr(node.body[0], "end_lineno", node.body[0].lineno),
            "end_col_offset": getattr(
                node.body[0], "end_col_offset", node.body[0].col_offset
            ),
        }

    def get_with_stmt(self, function_id: str, node: FunctionDef) -> ast.With:
        locations = self.get_with_location_from_node(node)

        args = [
            ast.Constant(value=function_id, kind=None, **locations)
        ]  # type: List[ast.expr]
        return ast.With(
            items=[
                ast.withitem(
                    context_expr=ast.Call(
                        func=ast.Name(id="HudMonitor", ctx=ast.Load(), **locations),
                        args=args,
                        keywords=[],
                        **locations,
                    ),
                )
            ],
            body=[],
            type_comment=None,
            **locations,
        )

    def _visit_generic_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        self.instrumented_functions += 1
        function_id = calculate_uuid(
            "|".join(
                (
                    node.name,
                    self.path,
                    str(Declaration.get_lineno(node)),
                    str(self.file_hash),
                )
            )
        )

        docstring = self.get_and_remove_docstring(node)

        with_stmt = self.get_with_stmt(str(function_id), node)
        with_stmt.body = node.body

        if not with_stmt.body:
            with_stmt.body = [ast.Pass(**self.get_with_location_from_node(node))]

        if docstring is not None:
            node.body = [docstring, with_stmt]
        else:
            node.body = [with_stmt]

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Optional[ast.ImportFrom]:
        # When passing an AST to the `compile` function, the `__future__` imports are not parsed
        # and the compiler flags are not set. This is a workaround to set the compiler flags,
        # and removing the invalid imports.
        if node.module == "__future__":
            import __future__

            for name in node.names:
                feature = getattr(__future__, name.name)
                self.compiler_flags |= feature.compiler_flag
            return None

        self.generic_visit(node)
        return node


def should_wrap_file(path: str) -> bool:
    return not is_path_disallowed(path)


def create_plain_module_checker(module: str) -> Callable[[str], bool]:
    def checker(fullname: str) -> bool:
        if fullname == module:
            return True

        if fullname.startswith("{}.".format(module)):
            return True

        return False

    return checker


def create_wildcard_module_checker(module: str) -> Callable[[str], bool]:
    escaped_module = module.replace("*", r".*?")
    base_search_regex = re.compile(f"^{escaped_module}$")
    dot_search_regex = re.compile(f"^{escaped_module}\\.")

    def checker(fullname: str) -> bool:
        if base_search_regex.match(fullname) is not None:
            return True

        if dot_search_regex.match(fullname) is not None:
            return True

        return False

    return checker


def create_module_to_trace_checkers(
    modules_to_trace: Set[str],
) -> List[Callable[[str], bool]]:
    # Python package name allowed characters: https://stackoverflow.com/questions/75697725/i-want-to-use-special-characters-for-naming-my-module-in-pypi
    checkers = []
    for module in modules_to_trace:
        if "*" in module:
            checkers.append(create_wildcard_module_checker(module))
        else:
            checkers.append(create_plain_module_checker(module))

    return checkers


def should_wrap_module(
    fullname: str,
    checkers: List[Callable[[str], bool]],
    negative_checkers: List[Callable[[str], bool]],
) -> bool:
    for checker in checkers:
        if checker(fullname):
            for nchecker in negative_checkers:
                if nchecker(fullname):
                    return False
            return True
    return False


def hud_pathify(path: str) -> str:
    if config.use_hud_pyc and path.endswith(".py"):
        return path.replace(".py", ".hud.py")
    return path


def hud_unpathify(path: str) -> str:
    if config.use_hud_pyc and path.endswith(".hud.py"):
        return path.replace(".hud.py", ".py")
    return path


total_instrumented_functions = 0


class MySourceLoader(SourceFileLoader):
    def path_stats(self, path: str) -> Mapping[str, Any]:
        if config.use_hud_pyc:
            return super().path_stats(hud_unpathify(path))
        else:
            if not path.endswith(".py"):
                return super().path_stats(path)
            stats = super().path_stats(path)
            # This manipulation allows bytecode caching to work for the edited module, without conflicting with the original module
            stats["mtime"] = time.time() * 2 + random.randint(1, 500)  # type: ignore[index]
            return stats

    def get_filename(self, name: Optional[str] = None) -> str:
        path = super().get_filename(name)
        if config.use_hud_pyc:
            return hud_pathify(path)
        return path

    def get_data(self, path: str) -> bytes:
        return super().get_data(hud_unpathify(path))

    def source_to_code(  # type: ignore[override]
        self, data: bytes, path: str, *, _optimize: int = -1
    ) -> CodeType:
        if path and config.use_hud_pyc:
            path = hud_unpathify(path)
        try:
            if len(data) > config.max_file_size:
                internal_logger.warning(
                    "File is too large to be monitored, skipping",
                    data={"path": path, "size": len(data)},
                )

                user_logger.log(
                    UsersLogs.FILE_TOO_LARGE_TO_MONITOR[0],
                    UsersLogs.FILE_TOO_LARGE_TO_MONITOR[1]
                    + f" Path: {path}. File size: {len(data)} bytes",
                )
                return super().source_to_code(data, path)

            internal_logger.debug("Monitoring file: {}".format(path))
            tree = cast(
                ast.Module,
                compile(
                    data,
                    path,
                    "exec",
                    flags=ast.PyCF_ONLY_AST,
                    dont_inherit=True,
                    optimize=_optimize,
                ),
            )  # type: ast.Module
            file_hash = crc32(data)
            transformer = ASTTransformer(path, data, file_hash)
            worker_queue.append(FileToParse(path, self.name, file_hash))
            tree = transformer.visit(tree)
            tree.body = [
                *ast.parse("from hud_sdk.native import Monitor as HudMonitor\n").body,
                *tree.body,
            ]

            global total_instrumented_functions  # this limit is per process and not per service
            total_instrumented_functions += transformer.instrumented_functions
            if total_instrumented_functions > config.max_instrumented_functions:
                user_logger.log(
                    *UsersLogs.MAX_INSTRUMENTED_FUNCTIONS_REACHED,
                )
                disable_hud(True)
                return super().source_to_code(data, path)

            return cast(
                CodeType,
                compile(
                    tree,
                    path,
                    "exec",
                    flags=transformer.compiler_flags,
                    dont_inherit=True,
                    optimize=_optimize,
                ),
            )
        except Exception:
            internal_logger.error(
                "Error while transforming AST on file",
                data={"path": path},
                exc_info=True,
            )
            return super().source_to_code(data, path)


def _hook_compile_bytecode() -> None:
    if not config.use_hud_pyc:
        return
    from importlib import _bootstrap_external

    original_compile_bytecode = _bootstrap_external._compile_bytecode  # type: ignore[attr-defined]

    @wraps(original_compile_bytecode)
    def hud_compile_bytecode(
        data: Any,
        name: Optional[str] = None,
        bytecode_path: Optional[str] = None,
        source_path: Optional[str] = None,
    ) -> Any:
        if source_path and config.use_hud_pyc:
            source_path = hud_unpathify(source_path)
        return original_compile_bytecode(data, name, bytecode_path, source_path)

    _bootstrap_external._compile_bytecode = hud_compile_bytecode  # type: ignore[attr-defined]


class InstrumentingPathFinder(importlib.abc.MetaPathFinder):
    def __init__(
        self,
        module_checkers: List[Callable[[str], bool]],
        blacklist_checkers: List[Callable[[str], bool]],
    ) -> None:
        self._module_checkers = module_checkers
        self._blacklist_checkers = blacklist_checkers
        self._currently_loading: Set[str] = set()

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]],
        target: Optional[types.ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        if fullname in self._currently_loading:
            # Prevent infinite recursion in case of circular imports
            return None
        self._currently_loading.add(fullname)
        try:
            spec = importlib.util.find_spec(fullname)
            if spec is None or not isinstance(spec.loader, SourceFileLoader):
                return None
            if spec.origin and (
                should_wrap_module(
                    fullname, self._module_checkers, self._blacklist_checkers
                )
                or should_wrap_file(spec.origin)
            ):
                spec.loader = MySourceLoader(fullname, spec.origin)
                return spec
        finally:
            self._currently_loading.remove(fullname)
        return None


hook_set = False

init_timer_thread: Optional[Timer] = None


def create_init_timeout() -> None:
    """
    This isn't the best implementation, but it's good enough as long we have only single timer.
    In case someone read this comment and want to add another timer we might want to implement our own timer thread instread of creating multiple timer threads.
    """

    def init_timeout() -> None:
        user_logger.log(*UsersLogs.HUD_INIT_TIMEOUT)

    global init_timer_thread
    init_timer_thread = Timer(config.init_timeout, init_timeout)
    init_timer_thread.daemon = True
    init_timer_thread.start()


def cancel_init_timeout() -> None:
    global init_timer_thread
    if init_timer_thread:
        try:
            init_timer_thread.cancel()
            init_timer_thread = None
        except Exception:
            internal_logger.error("Error while canceling init timeout", exc_info=True)


def set_hook(**kwargs: Any) -> None:
    try:
        internal_logger.set_component("main")
        with internal_logger.stage_context("set_hook"):
            global hook_set
            if hook_set:
                return

            should_run_hud_result = should_run_hud()
            if not should_run_hud_result.should_run:
                if should_run_hud_result.reason:
                    user_logger.log(*should_run_hud_result.reason)

                return
            hook_set = True

            start_time = time.time()
            try:
                _set_hook(**kwargs)
            finally:
                internal_logger.info(
                    "Hook set",
                    data={"duration": time.time() - start_time},
                )
    except Exception:
        internal_logger.critical("Error while setting hook", exc_info=True)


def _set_hook(should_create_init_timeout: bool = True) -> None:
    if not config.disable_exception_handler:
        install_exception_handler()
    internal_logger.info(
        "Hook stacktrace", data={"stacktrace": traceback.format_stack()}
    )
    worker_queue.append(get_pre_init_loaded_modules())
    _hook_compile_bytecode()
    sys.meta_path.insert(
        0,
        InstrumentingPathFinder(
            create_module_to_trace_checkers(config.modules_to_trace),
            create_module_to_trace_checkers(config.hud_dependency_blacklist),
        ),
    )

    register_fork_callbacks()
    instrument_frameworks()
    if should_create_init_timeout:
        create_init_timeout()
