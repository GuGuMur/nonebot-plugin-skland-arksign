from httpx import AsyncClient


def cleantext(text: str):
    lines = text.strip().split("\n")
    cleaned_lines = [line.strip() for line in lines]
    result = "\n".join(cleaned_lines)
    return result


async def get_binding_list(cred: str):
    headers = {
        "cred": cred,
        "User-Agent": "Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0",
        "Accept-Encoding": "gzip",
        "Connection": "close",
    }
    async with AsyncClient() as client:
        response = await client.get("https://zonai.skland.com/api/v1/game/player/binding", headers=headers)
        response = response.json()
    for i in response["data"]["list"]:
        if i.get("appCode") == "arknights":
            return i["bindingList"]


async def run_sign(uid: str, cred: str):
    headers = {
        "cred": cred,
        "User-Agent": "Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0",
        "Accept-Encoding": "gzip",
        "Connection": "close",
    }
    data = {"uid": str(uid), "gameId": "0"}
    drname = "Dr"
    server = ""
    binding = await get_binding_list(cred=cred)
    if not binding:
        return {
            "status": False,
            "text": f"获取账号绑定信息失败，请检查是否正确！\n{binding}",
        }
    for i in binding:
        if i["uid"] == uid:
            data["gameId"] = i["channelMasterId"]
            drname = i["nickName"]
            server = i["channelName"]
            break

    result = {}
    async with AsyncClient() as client:
        sign_response = await client.post(
            "https://zonai.skland.com/api/v1/game/attendance",
            headers=headers,
            data=data,
        )
        sign_response = sign_response.json()

    if sign_response.get("code") == 0:
        result["status"] = True
        result["text"] = f"{server}账号{drname}(UID{uid})签到成功\n"
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
        result["text"] = f"{server}账号 Dr.{drname}(UID{uid})签到失败，请检查以下信息：\n{sign_response}"
    return result
