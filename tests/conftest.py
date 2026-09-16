import os, pytest
@pytest.fixture(autouse=True)
def _offline_guard(monkeypatch):
    os.environ["VECTOR_OFFLINE"] = "1"
    os.environ["VECTOR_LIVE_EXECUTION"] = "0"
    os.environ["VECTOR_PAPER_EXECUTION"] = "0"
    def blocked(*_a, **_k):
        raise RuntimeError("network disabled in VECTOR offline tests")
    monkeypatch.setattr("socket.socket.connect", blocked, raising=False)
    yield
