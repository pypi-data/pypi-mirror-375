from orchagent.client import OrchClient


def test_headers_with_token(tmp_path):
    c = OrchClient(base_url="http://test")
    c.auth.set_token("tok", save=False)
    h = c._headers()
    assert h.get("Authorization") == "Bearer tok"

