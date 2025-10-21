from aiogram import Bot
from aiogram.types import Message
from aiogram.filters import Filter

from app.database.requests import select_user_id


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types
    

class IsAdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        status = await select_user_id(message.from_user.id)
        if int(status[3]) == 1:
            return True
        else:
            return False