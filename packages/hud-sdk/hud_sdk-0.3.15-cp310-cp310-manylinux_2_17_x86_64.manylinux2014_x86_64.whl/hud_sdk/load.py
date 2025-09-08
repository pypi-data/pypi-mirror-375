import inspect
import os
import re
import sys
import time
from typing import List, Optional

from .config import config
from .logging import internal_logger

did_load = False


def load_hud() -> None:
    global did_load
    if (
        did_load
        or _is_running_exporter()
        or _is_running_sitecustomize()
        or _is_running_entrypoint()
    ):
        return
    did_load = True
    start_time = time.time()
    try:
        frames = inspect.stack()
        trace_importing_module(frames)
    except Exception:
        internal_logger.exception("Error while loading HUD")
    finally:
        internal_logger.info(
            "HUD loaded",
            data={"duration": time.time() - start_time},
        )


def _is_running_exporter() -> bool:
    return os.environ.get("HUD_EXPORTER") == "1"


def _is_running_sitecustomize() -> bool:
    if "sitecustomize" not in sys.modules:
        return False
    if not sys.modules["sitecustomize"].__file__:
        return False
    return (
        os.path.join(config.sdk_name, "auto_init")
        in sys.modules["sitecustomize"].__file__
    )


def _is_running_entrypoint() -> bool:
    if len(sys.argv) < 2:
        return False
    return "hud-run" in sys.argv[1]


def trace_importing_module(frames: List[inspect.FrameInfo]) -> None:
    try:
        importing_module = find_importing_module(frames)
        if not importing_module:
            internal_logger.warning("No importing module found")
            return
        top_level_module = importing_module.split(".")[0]
        if (
            top_level_module in config.modules_to_trace
            or top_level_module
            == "__main__"  # This is a special case, we already add the main module's file to the paths_to_wrap
        ):
            internal_logger.info(
                "Module is already configured in modules_to_trace",
                data={
                    "module": top_level_module,
                    "modules_to_trace": list(config.modules_to_trace),
                },
            )
            return

        config.modules_to_trace.add(top_level_module)
        internal_logger.info(
            "Added module to trace",
            data={
                "module": top_level_module,
                "modules_to_trace": list(config.modules_to_trace),
            },
        )
        if top_level_module != importing_module:
            internal_logger.info(
                "Module is not top level", data={"module": importing_module}
            )
    except Exception:
        internal_logger.exception("Error while tracing importing module")


def find_importing_module(frames: List[inspect.FrameInfo]) -> Optional[str]:
    """
    Iterates through the stack frames and find the code that imports the SDK
    """
    import_statements = re.compile(r"\s*(from|import)\s+{}".format(config.sdk_name))
    for frame in frames:
        if not frame.code_context:
            continue

        for line in frame.code_context:
            if not import_statements.match(line):
                continue
            module_name = frame.frame.f_globals.get("__name__", "")
            if (
                module_name
                and config.sdk_name not in module_name
                and module_name not in config.blacklisted_modules
            ):
                return module_name  # type: ignore[no-any-return]
    return None
