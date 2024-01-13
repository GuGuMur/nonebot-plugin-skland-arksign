import hmac
import json
import hashlib
from time import time
from typing import Any, Literal
from dataclasses import dataclass
from collections import defaultdict
from urllib import parse as URLParse

from nonebot import logger
from httpx import AsyncClient

from .constants import CONSTANTS
from .config import plugin_config


@dataclass(frozen=True)
class SignResult:
    status: bool
    text: str


async def get_timestamp() -> str:
    if plugin_config.skland_use_web_timestamp:
        async with AsyncClient() as client:
            response = await client.get(CONSTANTS.BINDING_URL)
            response = response.json()
            return response["timestamp"]
    else:
        return str(int(time()) - plugin_config.skland_timestamp_delay)


def generate_signature(token: str, path: str, body_or_query: str, timestamp: str):
    """
    代码来源自https://gitee.com/FancyCabbage/skyland-auto-sign
    获得签名头
    接口地址+方法为Get请求？用query否则用body+时间戳+ 请求头的四个重要参数（dId，platform，timestamp，vName）.toJSON()
    将此字符串做HMAC加密，算法为SHA-256，密钥token为请求cred接口会返回的一个token值
    再将加密后的字符串做MD5即得到sign
    :param token: 拿cred时候的token
    :param path: 请求路径（不包括网址）
    :param body_or_query: 如果是GET，则是它的query。POST则为它的body
    :param timestamp: await get_timestamp() 生成的timestamp
    :return: 计算完毕的sign
    """
    token_bytes = token.encode("utf-8")
    header_ca = CONSTANTS.SIGN_HEADERS_BASE
    header_ca["timestamp"] = timestamp
    header_ca_str = json.dumps(header_ca, separators=(",", ":"))
    s = path + body_or_query + timestamp + header_ca_str
    hex_s = hmac.new(token_bytes, s.encode("utf-8"), hashlib.sha256).hexdigest()
    md5 = hashlib.md5(hex_s.encode("utf-8")).hexdigest()
    return md5, header_ca


def get_sign_header(
    url: str,
    method: Literal["get", "post"],
    body: dict | None,
    old_header: dict[str, Any],
    sign_token: str,
    timestamp: str,
) -> dict:
    header = old_header.copy()
    url_parsed = URLParse.urlparse(url)
    if method == "get":
        header["sign"], header_ca = generate_signature(sign_token, url_parsed.path, url_parsed.query, timestamp)
    else:
        header["sign"], header_ca = generate_signature(sign_token, url_parsed.path, json.dumps(body), timestamp)

    return header | header_ca


async def get_grant_code(token: str) -> str:
    data = {"appCode": CONSTANTS.APP_CODE, "token": token, "type": 0}

    async with AsyncClient() as client:
        response = await client.post(CONSTANTS.GRANT_CODE_URL, headers=CONSTANTS.REQUEST_HEADERS_BASE, json=data)
        response.raise_for_status()
        resp = response.json()
        if resp["status"] != 0:
            raise RuntimeError(f"获取认证码失败: {resp}")
        return resp["data"]["code"]


async def get_cred_resp(grant_code: str) -> dict[str, Any]:
    data = {"code": grant_code, "kind": 1}

    async with AsyncClient() as client:
        response = await client.post(CONSTANTS.CRED_CODE_URL, headers=CONSTANTS.REQUEST_HEADERS_BASE, json=data)
        response.raise_for_status()
        resp = response.json()
        if resp["code"] != 0:
            raise RuntimeError(f"获取cred失败：{resp}")
        return resp["data"]


async def get_binding_list(cred_resp: dict[str, Any]) -> list[dict[str, Any]]:
    headers = CONSTANTS.REQUEST_HEADERS_BASE
    headers["cred"] = cred_resp["cred"]
    timestamp = await get_timestamp()
    async with AsyncClient() as client:
        response = await client.get(
            CONSTANTS.BINDING_URL,
            headers=get_sign_header(CONSTANTS.BINDING_URL, "get", None, headers, cred_resp["token"], timestamp),
        )
        response.raise_for_status()
        response = response.json()
    for i in response["data"]["list"]:
        if i.get("appCode") == "arknights":
            return i["bindingList"]
    raise RuntimeError("未绑定明日方舟账号")


async def do_signin(uid: str, cred_resp: dict[str, Any], binding_list: list[dict[str, Any]]) -> SignResult:
    headers = CONSTANTS.REQUEST_HEADERS_BASE
    headers["cred"] = cred_resp["cred"]
    data = {"uid": uid, "gameId": "0"}
    timestamp = await get_timestamp()
    if not binding_list:
        raise RuntimeError("未绑定明日方舟账号")
    for i in binding_list:
        if i["uid"] == uid:
            data["gameId"] = i["channelMasterId"]
            drname: str = "Dr." + i["nickName"]
            server: str = i["channelName"]
            break
    else:
        raise RuntimeError("未找到对应uid的明日方舟账号")

    def parse(sign_response: dict[str, Any]) -> SignResult:
        if sign_response.get("code") == 0:
            status = True
            text = f"[{server}] {drname} UID:{uid} 签到成功\n"
            awards: list[dict] = sign_response.get("data", {}).get("awards", [])
            if not awards:
                raise ValueError(f"未能获取奖励列表，{sign_response=}")
            for award in awards:
                resource = defaultdict(lambda: "<Err>")
                resource.update(award.get("resource", {}))
                text += f"奖励ID：{resource['id']}\n"
                text += f"签到奖励：{resource['name']} × {award.get('count')}\n"
                text += f"类型：{resource['type']} {award.get('type', '<Err>')}\n"
        else:
            status = False
            text = f"[{server}] {drname} UID:{uid} 签到失败\n请检查以下信息：\n{sign_response}"
        return SignResult(status, text)

    async with AsyncClient() as client:
        sign_response = await client.post(
            CONSTANTS.SIGN_URL,
            headers=get_sign_header(CONSTANTS.SIGN_URL, "post", data, headers, cred_resp["token"], timestamp),
            json=data,
        )
        sign_response = sign_response.json()
    return parse(sign_response)


async def _run_signin(uid: str, token: str):
    grand_code = await get_grant_code(token)
    cred_resp = await get_cred_resp(grand_code)
    binding_list = await get_binding_list(cred_resp)
    return await do_signin(uid, cred_resp, binding_list)


async def run_signin(uid: str, token: str):
    try:
        return await _run_signin(uid, token)
    except Exception as e:
        logger.exception(f"签到失败：{e}")
        return SignResult(False, f"签到失败：{e}")
