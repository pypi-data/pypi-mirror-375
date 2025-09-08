from typing import Any, Union

from .logging import internal_logger

try:
    import orjson as json
except Exception:
    internal_logger.warning("orjson not installed, using json", exc_info=True)
    import json  # type: ignore[no-redef]


JSONDecodeError = json.JSONDecodeError


def dumps(obj: Any) -> bytes:
    result = json.dumps(obj)
    if isinstance(result, str):
        return result.encode("utf-8")
    return result


def loads(s: Union[bytes, str]) -> Any:
    return json.loads(s)
