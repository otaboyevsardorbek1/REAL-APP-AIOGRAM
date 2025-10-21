import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from app.database.requests import select_user_id, insert_user, update_user

logger = logging.getLogger(__name__)
        
        
class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if event.event_type in ['message', 'callback_query']:
            if event.event_type == 'message':
                user = event.message.from_user
            else:
                user = event.callback_query.from_user
                
            id_tg, username = user.id, user.username
            item = await select_user_id(id_tg)

            if item is None:
                logger.debug(f"Новый пользователь: {username} ({id_tg})")
                await insert_user(username, id_tg)
            elif item[1] != username:
                logger.debug(f"Имя пользователя изменено: {item[1]} - {username} ({id_tg})")
                await update_user(username, id_tg)
            elif item[3] == 2:
                logger.debug(f"Пользователь в черном списке: {username} ({id_tg})")
                return False
            else:
                logger.debug(f"Пользователь прошел проверку: {username} ({id_tg})")
        else:
            logger.debug(f'НЕОПОЗНАННЫЙ ТИП {event.event_type}')

        return await handler(event, data)