from pathlib import Path
from orchagent.config import Settings
from orchagent.auth import TokenStore


def test_token_store_roundtrip(tmp_path: Path):
    s = Settings(base_url="http://test", token_path=tmp_path / "token.json")
    ts = TokenStore(s)
    assert ts.load() is None
    ts.save("abc")
    assert ts.load() == "abc"

