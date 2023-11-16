from dataclasses import dataclass


@dataclass(frozen=True)
class _CONSTANTS:
    APP_CODE = "4ca99fa6b56cc2ba"
    SIGN_URL = "https://zonai.skland.com/api/v1/game/attendance"
    BINDING_URL = "https://zonai.skland.com/api/v1/game/player/binding"
    GRANT_CODE_URL = "https://as.hypergryph.com/user/oauth2/v2/grant"
    CRED_CODE_URL = "https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code"

    @property
    def REQUEST_HEADERS_BASE(self) -> dict[str, str]:
        return {
            "User-Agent": "Skland/1.4.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0",
            "Accept-Encoding": "gzip",
            "Connection": "close",
        }

    @property
    def SIGN_HEADERS_BASE(self) -> dict[str, str]:
        return {"platform": "1", "timestamp": "", "dId": "de9759a5afaa634f", "vName": "1.4.1"}


CONSTANTS = _CONSTANTS()
