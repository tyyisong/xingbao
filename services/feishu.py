"""飞书集成 — 写电子表格"""
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_SPREADSHEET_TOKEN, FEISHU_SHEET_ID

# 全局缓存 token + 过期时间
_token_cache = {"token": None, "expires_at": 0}


def get_tenant_token() -> Optional[str]:
    """获取飞书 tenant_access_token，自动缓存复用"""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET,
    }).encode()
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.URLError:
        return None

    if result.get("code") != 0:
        return None

    _token_cache["token"] = result["tenant_access_token"]
    _token_cache["expires_at"] = now + result.get("expire", 1800)
    return _token_cache["token"]


def _feishu_post(path: str, body: Dict, token: str) -> Optional[Dict[str, Any]]:
    """向飞书 API 发 POST 请求"""
    url = f"https://open.feishu.cn{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read())
        except Exception:
            detail = {"msg": str(e)}
        return {"code": e.code, "msg": detail.get("msg", str(e))}
    except urllib.error.URLError:
        return None


def append_row(age: str, city: str, gender: str, phone: str) -> dict:
    """向飞书表格追加一行报名数据，返回 {ok: bool, error: str|None}"""
    token = get_tenant_token()
    if not token:
        return {"ok": False, "error": "飞书认证失败"}

    from datetime import datetime
    submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = _feishu_post(
        f"/open-apis/sheets/v2/spreadsheets/{FEISHU_SPREADSHEET_TOKEN}/values_append",
        {
            "valueRange": {
                "range": f"{FEISHU_SHEET_ID}!A:E",
                "values": [[age, city, gender, phone, submit_time]],
            }
        },
        token,
    )

    if result and result.get("code") == 0:
        return {"ok": True, "error": None}
    msg = result.get("msg", "无响应") if result else "网络错误"
    return {"ok": False, "error": msg}
