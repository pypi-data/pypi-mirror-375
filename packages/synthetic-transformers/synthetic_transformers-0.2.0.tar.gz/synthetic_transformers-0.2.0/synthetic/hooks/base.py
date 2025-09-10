from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
import torch
from synthetic.exceptions import EOSException
from typing import Dict, Any


class HookType(Enum):
    ON_TOKEN = "on_token"
    ON_EOS = "on_eos"


@dataclass
class Event:
    step: int


class Hook(ABC):
    hook_type: HookType

    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, event) -> Event:
        pass


## --- ON_TOKEN --------


@dataclass
class TokenEvent(Event):
    input_ids: torch.Tensor
    past_key_values: torch.Tensor


class OnTokenHook(Hook):
    hook_type = HookType.ON_EOS

    @abstractmethod
    def __call__(self, event: TokenEvent) -> TokenEvent:
        pass


## --- ON_EOS ---------


@dataclass
class EOSEvent(Event):
    eos_exception: EOSException
    input_ids: torch.Tensor
    past_key_values: torch.Tensor
    output: Dict[str, Any]


class OnEOSHook(Hook):
    hook_type = HookType.ON_TOKEN

    @abstractmethod
    def __call__(self, event: EOSEvent) -> EOSEvent:
        pass
