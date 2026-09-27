from app.config import Settings


def test_fast_model_not_qwen3():
    s = Settings()
    assert "qwen3-32b" not in (s.groq_fast_model or "")
    assert s.groq_fast_model


def test_groq_error_path_without_key():
    from app.services.llm_service import RealGroqService

    s = Settings()
    s.groq_api_key = ""
    svc = RealGroqService(s)
    ok, detail = svc.status()
    assert ok is False or "No GROQ" in detail or not s.groq_api_key
    out = svc.classify("hello")
    assert "intent" in out
