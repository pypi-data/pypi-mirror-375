from transformers import PreTrainedModel, PreTrainedTokenizerBase
from typing import List, Union, Optional, Any, Dict
from synthetic.hooks import Hook, OnTokenHook, OnEOSHook, TokenEvent, EOSEvent
from synthetic.exceptions import EOSException, StopCriteria
from jinja2 import Template, StrictUndefined, Undefined
import torch
from dataclasses import dataclass, field


@dataclass
class GenerationOutput:
    input: Dict[str, Any]
    step: int

    extra: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, input: Dict[str, Any], step: int, **kwargs) -> None:
        self.input = input
        self.step = step
        self.extra = kwargs

    def __getattr__(self, name: str) -> Any:
        if name in self.extra:
            return self.extra[name]
        raise AttributeError(f"{name} not found")


class Transformer:

    model: PreTrainedModel
    tokenizer: PreTrainedTokenizerBase
    device: str

    prompt_template: Template

    max_new_tokens: Optional[int]
    greedy: bool

    _on_token_hooks: List[OnTokenHook]
    _on_eos_hooks: List[OnEOSHook]

    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizerBase,
        eos_token: str,
        device: str = "cpu",
        prompt_template: Optional[str] = None,
        strict: bool = False,
        max_new_tokens: Optional[int] = None,
        greedy: bool = True,
        hooks: List[Hook] = [],
    ) -> None:
        self.model = model.to(device)  # type: ignore
        self.tokenizer = tokenizer
        self.device = device
        self.eos_token = self.tokenizer(eos_token).input_ids

        if prompt_template:
            undefined = StrictUndefined if strict else Undefined
            self.prompt_template = Template(prompt_template, undefined=undefined)
        else:
            self.prompt_template = Template("{{ inputs }}", undefined=StrictUndefined)

        self.max_new_tokens = max_new_tokens
        self.greedy = greedy

        self._on_token_hooks = []
        self._on_eos_hooks = []

        self.add_hooks(hooks)

    def add_hooks(self, hooks: Union[Hook, List[Hook]]) -> None:
        if isinstance(hooks, list):
            for hook in hooks:
                self._add_hook(hook)
        else:
            self._add_hook(hooks)

    def _add_hook(self, hook: Hook) -> None:
        if isinstance(hook, OnTokenHook):
            self._on_token_hooks.append(hook)
        elif isinstance(hook, OnEOSHook):
            self._on_eos_hooks.append(hook)
        else:
            raise ValueError(
                "Hook must adhere to one of the main hook types: 'OnTokenHook' or 'OnEOSHook'."
            )

    def _run_on_token_hooks(self, event: TokenEvent) -> TokenEvent:

        for hook in self._on_token_hooks:
            event = hook(event)

        return event

    def _run_on_eos_hooks(self, event: EOSEvent) -> EOSEvent:
        for hook in self._on_eos_hooks:
            event = hook(event)

        return event

    def generate(self, **kwargs: Any) -> GenerationOutput:

        prompt = self.prompt_template.render(**kwargs)

        input_ids = (
            torch.tensor(self.tokenizer.encode(prompt), dtype=torch.int)
            .unsqueeze(0)
            .to(self.device)
        )
        past_key_values = None

        step = 0

        try:
            while self.max_new_tokens is None or step <= self.max_new_tokens:

                step += 1

                outputs = self.model(
                    input_ids=input_ids,
                    past_key_values=past_key_values,
                    use_cache=True,
                    **kwargs,
                )

                logits = outputs.logits[:, -1, :]
                past_key_values = outputs.past_key_values

                if self.greedy:
                    next_token = torch.argmax(logits, dim=-1)
                else:
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1).squeeze(-1)

                if next_token == self.eos_token:
                    raise EOSException(stop_criteria=StopCriteria.EOS_TOKEN)

                input_ids = torch.cat([input_ids, next_token.unsqueeze(-1)], dim=-1)

                token_event = TokenEvent(
                    input_ids=input_ids, past_key_values=past_key_values, step=step
                )
                token_event = self._run_on_token_hooks(token_event)

                input_ids = token_event.input_ids
                past_key_values = token_event.past_key_values

            raise EOSException(stop_criteria=StopCriteria.TOKEN_LIMIT)

        except EOSException as e:

            eos_event = EOSEvent(
                step=step,
                eos_exception=e,
                input_ids=input_ids,
                past_key_values=past_key_values,  # type: ignore
                output={"output": self.tokenizer.batch_decode(input_ids)[0]},
            )

            eos_event = self._run_on_eos_hooks(eos_event)

        return GenerationOutput(input=kwargs, step=step, extra=eos_event.output)
