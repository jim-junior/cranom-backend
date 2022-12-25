import httpx
import json
from .gh_token import get_gh_auth_token


def get_installation_token(installation_id: int):
    app_access = get_gh_auth_token()
    resp = httpx.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens", headers={
            "Authorization": f"Bearer {app_access}",
            "Accept": "application/vnd.github+json"
        })
    data = resp.json()
    return data["token"]
