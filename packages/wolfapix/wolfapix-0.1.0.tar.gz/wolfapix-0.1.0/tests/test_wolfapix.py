import pytest
import asyncio
from wolfapix.client import WOLF
from wolfapix.command import Command, CommandContext

@pytest.mark.asyncio
async def test_me_command():
    client = WOLF()
    # تسجيل الأمر me
    from wolfapix.me import me_command
    client.command_register([me_command])

    # محاكاة رسالة أمر
    context = CommandContext(client, source_subscriber_id=123, body="!me", is_command=True)

    # اختبار تنفيذ الأمر
    await me_command.handle(context, 'default')
    # لا استثناء يعني نجاح
    assert True
