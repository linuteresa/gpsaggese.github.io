"""Transport injection only: no credential reads, provider default, or live CLI."""
import hashlib
import time

from minisweagent.exceptions import FormatError

from .budget import BudgetBusy
from .policies import AccountingError, NANO, canonical, policy_for


def _text_only(prepared):
    for message in prepared:
        content = message.get("content")
        if isinstance(content, str):
            continue
        if not isinstance(content, list) or any(b.get("type") != "text" or not isinstance(b.get("text"), str) for b in content):
            raise ValueError("Only recorded text history is supported; no silent conversion")
        for block in content:
            cache = block.get("cache_control")
            if cache and (cache.get("type") != "ephemeral" or cache.get("ttl", "5m") != "5m"):
                raise ValueError("Unsupported prompt-cache policy")


def make_guarded_query(budget, model_id, job_id, stopped, *, completion):
    """Caller must supply a transport explicitly; offline tests supply mocks only."""
    policy = policy_for(model_id)
    if not callable(completion):
        raise ValueError("An explicitly injected transport is required")

    def query(self, messages, **kwargs):
        if kwargs or self.config.model_name != policy.model or self.config.model_kwargs != policy.sampling():
            raise ValueError("Undeclared model, policy, or per-request override")
        if self.config.set_cache_control != "default_end":
            raise ValueError("Undeclared cache configuration")
        prepared = self._prepare_messages_for_api(messages)
        _text_only(prepared)
        encoded = canonical(prepared)
        # Deliberately conservative byte screen, not a claimed exact tokenizer.
        upper_screen = len(encoded) + 4096 + 64 * len(prepared)
        if upper_screen + policy.max_output > policy.max_input:
            raise ValueError("History fails the conservative context screen; truncation is prohibited")
        request_hash = hashlib.sha256(encoded).hexdigest()
        while True:
            if stopped.is_set():
                raise RuntimeError("Run stopped before dispatch")
            try:
                token = budget.reserve(job_id, policy.model, request_hash)
                break
            except BudgetBusy:
                stopped.wait(.05)
        if stopped.is_set():
            budget.settle(token, rejection_status=400, error_type="StoppedBeforeDispatch")
            raise RuntimeError("Run stopped before dispatch")
        try:
            response = completion(model=policy.model, messages=prepared, **policy.sampling(),
                api_base="https://api.anthropic.com", service_tier="standard", inference_geo="global",
                num_retries=0, max_retries=0, timeout=180)
        except BaseException as exc:
            status = getattr(exc, "status_code", None)
            rejection = status if status in {400,401,403,404,413,422,429} else None
            budget.settle(token, rejection_status=rejection, error_type=type(exc).__name__)
            stopped.set()
            raise RuntimeError(f"Transport failed ({type(exc).__name__}); no retry") from None
        try:
            raw = response.model_dump(mode="json")
            if raw.get("service_tier") not in (None, "standard") or raw.get("inference_geo") not in (None, "global"):
                raise AccountingError("Response billing policy differs from request")
            if raw.get("usage") is None:
                raise AccountingError("Provider returned no usage")
        except BaseException:
            budget.settle(token, error_type="MalformedResponse")
            stopped.set()
            raise
        try:
            cost = budget.settle(token, usage=raw["usage"], response_model=raw.get("model"), response_id=raw.get("id")) / NANO
        except BaseException:
            stopped.set()
            raise
        try:
            actions = self._parse_actions(response)
        except FormatError as exc:
            exc.messages[0]["extra"].update({"cost":cost, "response":raw})
            raise
        message = response.choices[0].message.model_dump()
        message["extra"] = {"actions":actions, "response":raw, "cost":cost, "timestamp":time.time()}
        return message

    return query
