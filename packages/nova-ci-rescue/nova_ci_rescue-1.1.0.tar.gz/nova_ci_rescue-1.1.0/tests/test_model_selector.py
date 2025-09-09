import os
from nova.tools.model_selector import select_model, build_fallback_chain


def test_build_fallback_chain_default():
    os.environ.pop("NOVA_SECONDARY_MODEL", None)
    chain = build_fallback_chain("gpt-5-fast")
    assert chain[:2] == ["gpt-5-fast", "gpt-4o"]
    assert chain[-2:] == ["enhanced", "mock"]


def test_select_prefers_gpt5_with_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-xxx")
    sel = select_model("gpt-5-fast")
    assert sel.chosen == "gpt-5-fast"
    assert ("gpt-5-fast", "api_key_present") in sel.tried


def test_select_falls_back_to_mock_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    sel = select_model("gpt-5-fast")
    assert sel.chosen in {"enhanced", "mock"}
    # since enhanced is always available in our stub, chosen may be enhanced
    assert sel.tried[-1][0] in {"enhanced", "mock"}


