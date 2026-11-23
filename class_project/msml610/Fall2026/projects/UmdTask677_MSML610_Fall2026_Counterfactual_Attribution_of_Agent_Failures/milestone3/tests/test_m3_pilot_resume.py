"""Resume bookkeeping of the M3 pilot executor; no network, no credentials."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_m3_pilot as pilot  # noqa: E402  (needs scripts/ on the path)


def test_preflight_records_do_not_mark_live_jobs_done(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "STAGE", tmp_path)
    pilot.save(
        pilot.results_name(live=False),
        [{"job_id": "a", "status": "preflight_ok"}],
    )
    assert pilot.load_results(live=True) == {}
    assert set(pilot.load_results(live=False)) == {"a"}


def test_live_records_are_resumed_in_live_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "STAGE", tmp_path)
    pilot.save(
        pilot.results_name(live=True), [{"job_id": "b", "status": "completed"}]
    )
    assert set(pilot.load_results(live=True)) == {"b"}
    assert pilot.load_results(live=False) == {}


def test_live_mode_restores_the_real_socket_functions():
    import socket

    import m3_offline_common as offline

    assert socket.socket.connect is offline.deny_network
    try:
        pilot.allow_network()
        assert socket.socket.connect is offline.REAL_CONNECT
        assert socket.create_connection is offline.REAL_CREATE_CONNECTION
        assert socket.socket.connect is not offline.deny_network
    finally:
        socket.socket.connect = offline.deny_network
        socket.create_connection = offline.deny_network


def test_litellm_accepts_the_declared_haiku_45_request():
    # Network stays blocked: the call must fail at the connection, not at
    # litellm's client-side parameter validation (drop_params is False).
    import litellm
    import pytest
    from m3_runtime.policies import H4
    from m3_runtime.transport import request_options

    with pytest.raises(Exception) as info:
        litellm.completion(
            model=H4.model,
            messages=[{"role": "user", "content": "hi"}],
            api_key="offline-test",
            **H4.sampling(),
            **request_options(H4.model),
        )
    assert not isinstance(info.value, litellm.UnsupportedParamsError)


def test_inference_geo_is_sent_only_to_models_that_accept_it():
    # Live check 2026-11-22: the API answers 400 "claude-haiku-4-5-20251001
    # does not support inference_geo". M2 sent it to Haiku 5.5.
    from m3_runtime.policies import H4, H5
    from m3_runtime.transport import request_options

    assert "inference_geo" not in request_options(H4.model)
    assert request_options(H5.model)["inference_geo"] == "global"
    assert "service_tier" not in request_options(H5.model)


# Usage returned by the live API for claude-haiku-4-5-20251001 on 2026-11-22.
H45_LIVE_USAGE = {
    "completion_tokens": 40,
    "prompt_tokens": 42,
    "total_tokens": 82,
    "completion_tokens_details": {"reasoning_tokens": 34, "text_tokens": 6},
    "prompt_tokens_details": {
        "cache_write_tokens": 0,
        "cached_tokens": 0,
        "text_tokens": 42,
        "cache_creation_tokens": 0,
        "cache_creation_token_details": {
            "ephemeral_5m_input_tokens": 0,
            "ephemeral_1h_input_tokens": 0,
        },
    },
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "iterations": None,
    "inference_geo": "not_available",
    "speed": "standard",
    "service_tier": "standard",
}


def test_live_haiku_45_usage_is_priced_and_geo_stays_strict():
    import pytest
    from m3_runtime.policies import H4, H5, AccountingError, price_usage

    assert price_usage(H4.model, H45_LIVE_USAGE) == 42 * 1000 + 40 * 5000
    for model, geo in (
        (H4.model, "us"),
        (H4.model, "global"),
        (H5.model, "not_available"),
    ):
        with pytest.raises(AccountingError):
            price_usage(model, {**H45_LIVE_USAGE, "inference_geo": geo})
