from enum import Enum


class StopCriteria(Enum):
    EOS_TOKEN = "eos_token"
    FORCED_BY_HOOK = "forced_by_hook"
    TOKEN_LIMIT = "token_limit"


class EOSException(Exception):
    stop_criteria: StopCriteria
