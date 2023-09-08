from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class SklandSubscribe(Model):
    __tablename__ = "skland_subscribe"
    __table_args__ = {"extend_existing": True}

    uid: Mapped[str] = mapped_column(String, primary_key=True, doc="森空岛账号ID")
    user: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), doc="订阅用户信息")
    cred: Mapped[str] = mapped_column(String, doc="森空岛账号CRED")
    token: Mapped[str] = mapped_column(String, doc="森空岛账号TOKEN", nullable=True)
