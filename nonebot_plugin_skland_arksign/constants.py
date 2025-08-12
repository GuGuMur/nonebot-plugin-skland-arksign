from dataclasses import dataclass


@dataclass(frozen=True)
class _CONSTANTS:
    APP_CODE = "4ca99fa6b56cc2ba"
    SIGN_URL = "https://zonai.skland.com/api/v1/game/attendance"
    BINDING_URL = "https://zonai.skland.com/api/v1/game/player/binding"
    GRANT_CODE_URL = "https://as.hypergryph.com/user/oauth2/v2/grant"
    CRED_CODE_URL = "https://zonai.skland.com/web/v1/user/auth/generate_cred_by_code"
    DEVICES_PROFILE_URL = "https://fp-it.portal101.cn/deviceprofile/v4"

    @property
    def REQUEST_HEADERS_BASE(self) -> dict[str, str]:
        return {
            "User-Agent": "Skland/1.45.1 (com.hypergryph.skland; build:104501004; Android 34; ) Okhttp/4.11.0",
            "Accept-Encoding": "gzip",
            "Connection": "close",
            "Origin": "https://www.skland.com",
            "Referer": "https://www.skland.com/",
            "Content-Type": "application/json; charset=UTF-8",
            "manufacturer": "Xiaomi",
            "os": "34",
            "vname": "1.45.1",
            "vcode": "104501004",
            "platform": "1",
            "nid": "1",
            "channel": "OF",
            "language": "zh_CN",
            "dId": "",
        }

    @property
    def SIGN_HEADERS_BASE(self) -> dict[str, str]:
        return {"platform": "1", "timestamp": "", "dId": "de9759a5afaa634f", "vName": "1.45.1"}

    @property
    def SM_CONFIG(self) -> dict[str, str]:
        """=>https://help.ishumei.com/docs/tw/sdk/web/developDoc/"""
        return {
            "organization": "UWXspnCCJN4sfYlNfqps",
            "appId": "default",
            "publicKey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmxMNr7n8ZeT0tE1R9j/mPixoinPkeM+k4VGIn/s0k7N5rJAfnZ0eMER+QhwFvshzo0LNmeUkpR8uIlU/GEVr8mN28sKmwd2gpygqj0ePnBmOW4v0ZVwbSYK+izkhVFk2V/doLoMbWy6b+UnA8mkjvg0iYWRByfRsK2gdl7llqCwIDAQAB",
            "protocol": "https",
            "apiHost": "fp-it.portal101.cn",
            "apiPath": "/deviceprofile/v4",
        }


CONSTANTS = _CONSTANTS()
