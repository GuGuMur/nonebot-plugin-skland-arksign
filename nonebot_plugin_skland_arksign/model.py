from sqlalchemy import JSON, String
from nonebot_plugin_orm import Model
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class SklandSubscribe(Model):
    __tablename__ = "skland_subscribe"
    __table_args__ = {"extend_existing": True}

    uid: Mapped[str] = mapped_column(String, primary_key=True, doc="森空岛账号ID")
    user: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), doc="订阅用户信息")
    cred: Mapped[str] = mapped_column(String, doc="森空岛账号CRED")
    token: Mapped[str] = mapped_column(String, doc="森空岛账号TOKEN", nullable=True)
    note: Mapped[str] = mapped_column(String, doc="备注", nullable=True, unique=True)
