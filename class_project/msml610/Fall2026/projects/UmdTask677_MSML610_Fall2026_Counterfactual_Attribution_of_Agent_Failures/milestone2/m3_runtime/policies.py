"""Pinned model policies and integer nanodollar rates, checked 2026-11-20."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from types import MappingProxyType

NANO = 1_000_000_000


class AccountingError(RuntimeError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


@dataclass(frozen=True)
class Rates:
    input: int
    write: int
    read: int
    output: int


@dataclass(frozen=True)
class Policy:
    model: str
    response_models: tuple[str, ...]
    max_input: int
    max_output: int
    thinking: str
    thinking_budget: int | None
    short: Rates
    long: Rates
    long_threshold: int

    def sampling(self):
        thinking = {"type": self.thinking}
        if self.thinking_budget is not None:
            thinking["budget_tokens"] = self.thinking_budget
        return {"drop_params": False, "max_tokens": self.max_output, "thinking": thinking}

    @property
    def maximum(self):
        rates = self.long if self.max_input > self.long_threshold else self.short
        return self.max_input * max(rates.input, rates.write, rates.read) + self.max_output * rates.output

    @property
    def fingerprint(self):
        return sha256(canonical(asdict(self))).hexdigest()


H5 = Policy("anthropic/claude-haiku-5-5", ("claude-haiku-5-5",),
            1_000_000, 16_000, "adaptive", None,
            Rates(100, 125, 10, 500), Rates(500, 625, 50, 2500), 100_000)
H4 = Policy("anthropic/claude-haiku-4-5-20251001", ("claude-haiku-4-5-20251001",),
            200_000, 16_000, "enabled", 4096,
            Rates(1000, 1250, 100, 5000), Rates(1000, 1250, 100, 5000), 200_000)
POLICIES = MappingProxyType({p.model: p for p in (H5, H4)})
PRICING_SOURCE = "https://platform.claude.com/docs/en/about-claude/pricing"
PRICING_CHECKED = "2026-11-20"


def policy_for(model):
    try:
        return POLICIES[model]
    except KeyError:
        raise AccountingError("Model is not in the pinned policy registry") from None


def registry_document():
    return {"schema": "caaf.m3.policies/1", "checked": PRICING_CHECKED,
            "source": PRICING_SOURCE, "policies": [asdict(p) for p in POLICIES.values()]}


def _integer(value, name):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise AccountingError(f"Invalid token count: {name}")
    return value


def _same_counter(*values):
    values = [v for v in values if v is not None]
    if not values:
        return 0
    parsed = [_integer(v, "cache") for v in values]
    if len(set(parsed)) != 1:
        raise AccountingError("Conflicting cache counters")
    return parsed[0]


def normalize_usage(usage, policy):
    if not isinstance(usage, dict):
        raise AccountingError("Missing token usage")
    if usage.get("service_tier") not in (None, "standard") or usage.get("inference_geo") not in (None, "global"):
        raise AccountingError("Unexpected billing tier or geography")
    details = usage.get("prompt_tokens_details") or {}
    cache = usage.get("cache_creation") or {}
    if not isinstance(details, dict) or not isinstance(cache, dict):
        raise AccountingError("Malformed cache details")
    cache_details = details.get("cache_creation_token_details") or {}
    if not all(isinstance(x, dict) for x in (details, cache, cache_details)):
        raise AccountingError("Malformed cache details")
    if any(x.get("ephemeral_1h_input_tokens", 0) for x in (cache, cache_details)):
        raise AccountingError("One-hour cache writes are outside the pinned policy")
    read = _same_counter(usage.get("cache_read_input_tokens"), details.get("cached_tokens"))
    write = _same_counter(usage.get("cache_creation_input_tokens"), details.get("cache_creation_tokens"),
                          details.get("cache_write_tokens"), cache.get("ephemeral_5m_input_tokens"),
                          cache_details.get("ephemeral_5m_input_tokens"))
    if "prompt_tokens" in usage:
        total = _integer(usage["prompt_tokens"], "prompt_tokens")
        if total < read + write:
            raise AccountingError("Inclusive prompt count is smaller than cache counters")
        uncached = total - read - write
        if "input_tokens" in usage and _integer(usage["input_tokens"], "input_tokens") != uncached:
            raise AccountingError("Conflicting raw and normalized input counters")
    elif "input_tokens" in usage:
        uncached = _integer(usage["input_tokens"], "input_tokens")
        total = uncached + read + write
    else:
        raise AccountingError("Missing input token count")
    if "completion_tokens" in usage:
        output = _integer(usage["completion_tokens"], "completion_tokens")
        if "output_tokens" in usage and _integer(usage["output_tokens"], "output_tokens") != output:
            raise AccountingError("Conflicting output counters")
    elif "output_tokens" in usage:
        output = _integer(usage["output_tokens"], "output_tokens")
    else:
        raise AccountingError("Missing output token count")
    reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    if reasoning is not None and _integer(reasoning, "reasoning_tokens") > output:
        raise AccountingError("Reasoning exceeds inclusive output count")
    if total > policy.max_input or output > policy.max_output:
        raise AccountingError("Usage exceeds the pinned model bounds")
    return {"prompt_tokens": total, "uncached_input": uncached,
            "cache_read": read, "cache_write": write, "completion_tokens": output}


def price_usage(model, usage):
    policy = policy_for(model)
    u = normalize_usage(usage, policy)
    rates = policy.long if u["prompt_tokens"] > policy.long_threshold else policy.short
    return (u["uncached_input"] * rates.input + u["cache_read"] * rates.read
            + u["cache_write"] * rates.write + u["completion_tokens"] * rates.output)
