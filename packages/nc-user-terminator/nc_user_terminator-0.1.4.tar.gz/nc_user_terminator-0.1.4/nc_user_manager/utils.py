import json
import urllib.parse
import urllib.request
import urllib.error

from exceptions import OAuthError


def request(method: str, url: str, params=None, headers=None, json_body=None) -> dict:
    # 拼接 GET 参数
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, method=method.upper(), data=data)

    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                raise OAuthError("Invalid JSON response", resp.getcode(), body)
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else None
        raise OAuthError("HTTP request failed", e.code, body)
    except urllib.error.URLError as e:
        raise OAuthError(f"Network error: {e.reason}")
