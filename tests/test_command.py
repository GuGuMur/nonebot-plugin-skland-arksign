from nonebug import App
from nonebot import get_adapter
from pytest_mock import MockerFixture


async def test_list(app: App, mocker: MockerFixture):
    from nonebot_plugin_orm import get_session
    from nonebot_plugin_saa import TargetQQPrivate
    from nonebot.adapters.onebot.v11 import Bot, Adapter, Message

    from nonebot_plugin_skland_arksign.model import SklandSubscribe
    from nonebot_plugin_skland_arksign.command import skland as skland_cmd

    from .fake import fake_private_message_event_v11

    async with app.test_matcher(skland_cmd) as ctx:

        async with get_session(expire_on_commit=False) as session:
            subscribe = SklandSubscribe(
                uid="1234567890",
                user=TargetQQPrivate(user_id=1234567890).dict(),
                cred="",
                token="test-token",
                note="test-note",
            )
            session.add(subscribe)
            await session.commit()

        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_private_message_event_v11(message=Message("/skland list"))

        ctx.receive_event(bot, event)
        ctx.should_call_api("get_group_list", {}, [{"group_id": "1111"}])
        ctx.should_call_api("get_friend_list", {}, [{"user_id": 1122}])
        ctx.should_call_send(
            event,
            "UID：1234567890\nTOKEN：test-token\n备注：test-note",
            True,
        )
        ctx.should_finished(skland_cmd)
