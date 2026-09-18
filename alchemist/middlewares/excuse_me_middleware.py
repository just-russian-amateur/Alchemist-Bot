from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InputRichMessage

import classes.all_my_classes as amc
import config
from texts.redis_keys import RedisKeys
from texts.all_my_texts import ExcuseMeTexts
from richmessages.all_my_rich_messages import create_rich_msg, build_excuse_msg


logger = amc.ConfigLogger(__name__)


class ExcuseMeMiddleware(BaseMiddleware):
    '''Middleware для фильтрации пользователей, которые могут пользоваться ботом после каждого их сообщения'''

    async def __call__(self, handler, event, data):

        state = data.get(RedisKeys.STATE)
        user_id = data.get(RedisKeys.EVENT_FROM_USER).id
        user_data = await state.get_data()

        if await config.redis.sismember(RedisKeys.FRIENDS, user_id):
            # Пользователи, сообщения от которых будут обработаны
            return await handler(event, data)
        
        paid_attempts = user_data.get(RedisKeys.PAID_ATTEMPTS)

        if paid_attempts and user_data.get(RedisKeys.PAID_ATTEMPTS) > 0:
            return await handler(event, data)

        logger.log_info(f'Пользователь не может использовать бота')

        if isinstance(event, CallbackQuery):

            await event.message.answer_rich(
                InputRichMessage(
                    blocks=create_rich_msg(
                        ExcuseMeTexts.EXCUSE_MESSAGE,
                        build_excuse_msg()
                    )
                )
            )

            await event.answer()

        else:

            await event.answer_rich(
                InputRichMessage(
                    blocks=create_rich_msg(
                        ExcuseMeTexts.EXCUSE_MESSAGE,
                        build_excuse_msg()
                    )
                )
            )

        return
