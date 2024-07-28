from sqlalchemy import JSON, String
from typing import Any
from nonebot_plugin_orm import Model
from nonebot.compat import ConfigDict, PYDANTIC_V2
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

if PYDANTIC_V2:
    from pydantic_core import core_schema


class Identity:
    def __init__(self, _l):
        self.l = _l

    def __eq__(self, value: object) -> bool:
        return value in self.l

class SklandSubscribe(Model):
    __tablename__ = "skland_subscribe"
    __table_args__ = {"extend_existing": True}
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String, primary_key=True, doc="森空岛账号ID")
    user: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), doc="订阅用户信息")
    address: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), doc="发送位置", nullable=True)
    token: Mapped[str] = mapped_column(String, doc="森空岛账号TOKEN", nullable=True)
    note: Mapped[str] = mapped_column(String, doc="备注", nullable=True)
    status: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), doc="用户的使用状况", nullable=True)

    @property
    def user_feature(self) -> dict[str, any]:
        return {
            "bot_type": self.user.get("bot_type"),
            "platform": self.user.get("platform"),
            "id1": self.user.get("id1"),
        }
    @property
    def user_identity(self) -> Identity:
        return Identity([self.uid, self.note])

    if PYDANTIC_V2:

        @classmethod
        def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
            return core_schema.with_info_plain_validator_function(lambda value, _: cls._validate(value))

    else:

        @classmethod
        def __get_validators__(cls):
            yield cls._validate


