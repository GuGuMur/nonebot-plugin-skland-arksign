import hmac
import json
import time
import hashlib
from urllib import parse
from typing import Literal

from httpx import AsyncClient

APP_CODE = "4ca99fa6b56cc2ba"

login_header = {
    "User-Agent": "Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0",
    "Accept-Encoding": "gzip",
    "Connection": "close",
}

temp_header = {
    "cred": "",
    "User-Agent": "Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0",
    "Accept-Encoding": "gzip",
    "Connection": "close",
}

# 签名请求头一定要这个顺序，否则失败
# timestamp是必填的,其它三个随便填,不要为none即可
header_for_sign = {"platform": "1", "timestamp": "", "dId": "de9759a5afaa634f", "vName": "1.0.1"}

sign_url = "https://zonai.skland.com/api/v1/game/attendance"
binding_url = "https://zonai.skland.com/api/v1/game/player/binding"
grant_code_url = "https://as.hypergryph.com/user/oauth2/v2/grant"
cred_code_url = "https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code"


def cleantext(text: str) -> str:
    lines = text.strip().split("\n")
    cleaned_lines = [line.strip() for line in lines]
    result = "\n".join(cleaned_lines)
    return result


async def get_grant_code(token: str) -> str:
    data = {"appCode": APP_CODE, "token": token, "type": 0}

    async with AsyncClient() as client:
        response = await client.post(grant_code_url, headers=login_header, data=data)
        response.raise_for_status()
        return response.json()["data"]["code"]


async def get_cred(grant_code: str) -> dict:
    data = {"code": grant_code, "kind": 1}

    async with AsyncClient() as client:
        response = await client.post(cred_code_url, headers=login_header, data=data)
        response.raise_for_status()
        return response.json()["data"]


async def get_cred_by_token(token: str):
    grant_code = await get_grant_code(token)
    return await get_cred(grant_code)


async def get_binding_list(cred_resp: dict) -> list:
    headers = temp_header.copy()
    headers["cred"] = cred_resp["cred"]
    async with AsyncClient() as client:
        response = await client.get(
            binding_url, headers=get_sign_header(binding_url, "get", None, headers, cred_resp["token"])
        )
        response.raise_for_status()
        response = response.json()
    for i in response["data"]["list"]:
        if i.get("appCode") == "arknights":
            return i["bindingList"]
    return []


async def run_sign(uid: str, token: str):
    cred_resp = await get_cred_by_token(token)
    return await do_sign(uid, cred_resp)


def generate_signature(token: str, path: str, body_or_query: str):
    """
    代码来源自https://gitee.com/FancyCabbage/skyland-auto-sign
    获得签名头
    接口地址+方法为Get请求？用query否则用body+时间戳+ 请求头的四个重要参数（dId，platform，timestamp，vName）.toJSON()
    将此字符串做HMAC加密，算法为SHA-256，密钥token为请求cred接口会返回的一个token值
    再将加密后的字符串做MD5即得到sign
    :param token: 拿cred时候的token
    :param path: 请求路径（不包括网址）
    :param body_or_query: 如果是GET，则是它的query。POST则为它的body
    :return: 计算完毕的sign
    """
    # 总是说请勿修改设备时间，怕不是yj你的服务器有问题吧，所以这里特地-2
    timestamp = str(int(time.time()) - 2)
    token_bytes = token.encode("utf-8")
    header_ca = header_for_sign.copy()
    header_ca["timestamp"] = timestamp
    header_ca_str = json.dumps(header_ca, separators=(",", ":"))
    s = path + body_or_query + timestamp + header_ca_str
    hex_s = hmac.new(token_bytes, s.encode("utf-8"), hashlib.sha256).hexdigest()
    md5 = hashlib.md5(hex_s.encode("utf-8")).hexdigest()
    return md5, header_ca


def get_sign_header(
    url: str, method: Literal["get", "post"], body: dict | None, old_header: dict, sign_token: str
) -> dict:
    header = old_header.copy()
    url_parsed = parse.urlparse(url)
    if method == "get":
        header["sign"], header_ca = generate_signature(sign_token, url_parsed.path, url_parsed.query)
    else:
        header["sign"], header_ca = generate_signature(sign_token, url_parsed.path, json.dumps(body or {}))
    for i in header_ca:
        header[i] = header_ca[i]
    return header


async def do_sign(uid: str, cred_resp: dict):
    headers = temp_header.copy()
    headers["cred"] = cred_resp["cred"]
    data = {"uid": uid, "gameId": "0"}
    drname = "Dr"
    server = ""
    binding = await get_binding_list(cred_resp)
    if not binding:
        return {
            "status": False,
            "text": f"获取账号绑定信息失败，请检查是否正确！\n{binding}",
        }
    for i in binding:
        if i["uid"] == uid:
            data["gameId"] = i["channelMasterId"]
            drname = "Dr." + i["nickName"]
            server = i["channelName"]
            break

    result = {}
    async with AsyncClient() as client:
        sign_response = await client.post(
            sign_url,
            headers=get_sign_header(sign_url, "post", data, headers, cred_resp["token"]),
            data=data,
        )
        sign_response = sign_response.json()

    if sign_response.get("code") == 0:
        result["status"] = True
        result["text"] = f"{server}账号 {drname}(UID{uid})签到成功\n"
        awards = sign_response.get("data").get("awards")
        for award in awards:
            result["text"] += "获得的奖励ID为：" + award.get("resource").get("id") + "\n"
            result["text"] += (
                "此次签到获得了"
                + str(award.get("count"))
                + "单位的"
                + award.get("resource").get("name")
                + "("
                + award.get("resource").get("type")
                + ")\n"
            )
            result["text"] += "奖励类型为：" + award.get("type") + "\n"
    else:
        result["status"] = False
        result["text"] = f"{server}账号 {drname}(UID{uid})签到失败，请检查以下信息：\n{sign_response}"
    return result
