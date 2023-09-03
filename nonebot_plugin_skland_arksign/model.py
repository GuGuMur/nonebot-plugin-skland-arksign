from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class SKLANDACCOUNT(Model):
    __table_args__ = {"extend_existing": True}
    
    uid: Mapped[str] = mapped_column(String, primary_key=True)
    qid: Mapped[int] = mapped_column(Integer)
    cred: Mapped[str] = mapped_column(String)