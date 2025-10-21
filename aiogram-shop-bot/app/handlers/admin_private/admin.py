import logging

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject

from config import ADMIN_ID

from app.database.requests import (
    update_admin,
    update_admin_no,
    select_user_id,
    update_status, update_status_no
)
from app.common.filters import IsAdminFilter, ChatTypeFilter
from app.keyboards.reply import admin_panel, admin_news, admin_category, admin_item

router_admin = Router()
router_admin.message.filter(IsAdminFilter(), ChatTypeFilter(['private']))

logger = logging.getLogger(__name__)

@router_admin.callback_query(F.data == "callback_back")
async def call_admin(callback: CallbackQuery):
    """
    Return to admin panel
    """
    logging.debug(
        f"Пользователь {callback.from_user.username} ({callback.from_user.id}) "
        "- вернулся в админ панель"
    )
    await callback.answer('{}')
    await callback.message.answer(
        'Вы вернулись в админ панель',
        reply_markup=admin_panel
    )

@router_admin.message(Command('admin'))
async def cmd_admin(message: Message):
    """
    Launching the admin panel
    """
    logging.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "включил админ панель"
    )
    await message.answer(
        'Ваш статус - <b>Админ</b>, вам разрешен доступ в админ панель',
        reply_markup=admin_panel
    )
    
@router_admin.message(Command('ban'))
async def cmd_ban(message: Message, command: CommandObject):
    """
    Ban is user
    """
    if command.args is None:
        return
    try:
        user = int(command.args)
        user_is_bd = int(await select_user_id(user))
        
        if user == user_is_bd:
            await message.answer(
                f"Пользователь {user} был добавлен в черный список"
            )
            await update_status(user)
        else:
            await message.answer(
                "Такого пользователя не существует в базе данных"
            )
            logger.debug(
                f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
                f"банит пользователя {user}"
            )
    except:
        await message.answer("Неправильный ввод")
        return
    
    
@router_admin.message(Command('unban'))
async def cmd_unban(message: Message, command: CommandObject):
    """
    Unban is user
    """
    if command.args is None:
        return
    try:
        user = int(command.args)
        user_is_bd = int(await select_user_id(user))
        
        if user == user_is_bd:
            await message.answer(
                f"Пользователь {user} был убран из черного списка"
            )
            await update_status_no(user)
            logger.debug(
                f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
                f"разбанивает пользователя {user}"
            )
        else:
            await message.answer(
                "Такого пользователя не существует в базе данных"
            )
    except:
        await message.answer("Неправильный ввод")
        return
    
@router_admin.message(F.text.in_(['Категории', 'Товары', 'Новости']))
async def cmd_panel(message: Message):
    """
    Changes panel
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "запустил одну из панелей"
    )
    if message.text == 'Категории':
        await message.answer(
            'Выберите действие категории',
            reply_markup=admin_category
        )
    elif message.text == 'Товары':
        await message.answer(
            'Выберите действие товаров',
            reply_markup=admin_item
        )
    elif message.text == 'Новости':
        await message.answer(
            'Выберите действие новостей',
            reply_markup=admin_news
        )
    
@router_admin.message(Command('addadmin'))
async def cmd_addAdmin(message: Message, command: CommandObject):
    """
    Add admin
    """
    logging.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "пытается выдать админку"
    )
    if message.from_user.id != int(ADMIN_ID):
        return
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    new_user = int(command.args)
    if new_user == int(ADMIN_ID):
        await message.answer(
            'Вы не можете редактировать свой статус!'
        )
        return
    user = await select_user_id(new_user)
    if user is None:
        await message.answer(
            'Такого пользователя не найдено в базе данных бота'
        )
    logging.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "успешно прошел проверку"
    )

    await update_admin(new_user)
    await message.answer(
        f'{new_user} - был удален из списка администраторов'
    )
    logging.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "выдал админку пользователю {command.args}"
    )
    
@router_admin.message(Command('readmin'))
async def cmd_reAdmin(message: Message, command: CommandObject):
    """
    Remove admin
    """
    logging.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "пытается забрать админку"
    )
    if message.from_user.id != ADMIN_ID:
        return
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    new_user = int(command.args)
    if new_user == ADMIN_ID:
        await message.answer(
            'Вы не можете редактировать свой статус!'
        )
        return
    user = await select_user_id(new_user)
    if user is None:
        await message.answer(
            'Такого пользователя не найдено в базе данных бота'
        )
        logging.debug(
            f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
            "успешно прошел проверку"
        )

    await update_admin_no(new_user)
    await message.answer(
        f'{new_user} - был удален из списка администраторов'
    )
    logging.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "отнял админку пользователя ({command.args})"
    )
    
