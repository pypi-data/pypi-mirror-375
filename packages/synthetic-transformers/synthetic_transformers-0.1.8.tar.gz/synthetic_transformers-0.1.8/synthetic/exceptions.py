from enum import Enum
from typing import Dict, Any


class StopCriteria(Enum):
    EOS_TOKEN = "eos_token"
    FORCED_BY_HOOK = "forced_by_hook"
    TOKEN_LIMIT = "token_limit"


class EOSException(Exception):
    stop_criteria: StopCriteria
    extra: Dict[str, Any]

    def __init__(self, stop_criteria: StopCriteria, **kwargs: Any) -> None:
        self.stop_criteria = stop_criteria
        self.extra = kwargs

    def __getattr__(self, name: str) -> Any:
        if name in self.extra:
            return self.extra[name]
        raise AttributeError(f"{name} not found")
