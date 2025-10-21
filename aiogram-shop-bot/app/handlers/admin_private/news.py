import logging

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.requests import insert_news, update_news, delete_news_i
from app.common.filters import IsAdminFilter, ChatTypeFilter
import app.keyboards.builder as bd
import app.keyboards.reply as rp

router_news = Router()
router_news.message.filter(IsAdminFilter(), ChatTypeFilter(['private']))

logger = logging.getLogger(__name__)

class NewsState(StatesGroup):
    name = State()
    description = State()
    photo = State()
    
class ChangeNewsState(StatesGroup):
    name = State()
    change = State()
    new_change = State()
    
class DeleteNewsState(StatesGroup):
    name = State()


# НАЧАЛО ДОБАВЛЕНИЯ НОВОСТЕЙ
@router_news.message(StateFilter(None), F.text == "Добавить новости")
async def cmd_addNews(message: Message, state: FSMContext):
    """
    Add news
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "добавляет новости"
    )
    await message.answer(
        "Процесс добавления новости запущен. Напишите название новости",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(NewsState.name)
    
@router_news.message(NewsState.name, F.text)
async def cmd_addNewsName(message: Message, state: FSMContext):
    """
    Add news - name
    """
    await state.update_data(name=message.text)
    await message.answer(
        "Название новости сохранен. Напишити описание новости"
    )
    await state.set_state(NewsState.description)
    
@router_news.message(NewsState.description, F.text)
async def cmd_addNewsDesc(message: Message, state: FSMContext):
    """
    Add news - desc
    """
    await state.update_data(description=message.text)
    await message.answer(
        "Описание новостей сохранено. Отправьте фото новости"
    )
    await state.set_state(NewsState.photo)
    
@router_news.message(NewsState.photo, F.photo)
async def cmd_addNewsPhoto(message: Message, state: FSMContext):
    """
    Add news - photo
    """
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer(
        "Процесс добавления новости запущен. Напишите название новостей",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    photo = data["photo"]
    
    await insert_news(name, description, photo)
    await state.clear()
    
    
# НАЧАЛО ИЗМЕНЕНИЯ НОВОСТЕЙ
@router_news.message(StateFilter(None), F.text == "Изменить новости")
async def cmd_changeNews(message: Message, state: FSMContext):
    """
    Change news
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "изменяет новости"
    )
    await message.answer(
        "Процесс изменения новости запущен. Выберите новость",
        reply_markup=await bd.change_news()
    )
    await state.set_state(ChangeNewsState.name)
    
@router_news.callback_query(ChangeNewsState.name, F.data)
async def cmd_changeNewsName(callback: CallbackQuery, state: FSMContext):
    """
    Change news - name
    """
    await state.update_data(name=callback.data.split('_')[-1])
    await callback.answer('')
    await callback.message.answer(
        "Вы выбрали новость. Выберите что хотите изменить",
        reply_markup=rp.change_news_kb
    )
    await state.set_state(ChangeNewsState.change)
    
@router_news.message(ChangeNewsState.change, F.text.in_([
    'Название новости',
    'Описание новости',
    'Изображение новости'
]))
async def cmd_changeNewsOld(message: Message, state: FSMContext):
    """
    Change news - change
    """
    item = {
        'Название новости': 'name',
        'Описание новости': 'description',
        'Изображение новости': 'photo'
    }
    await state.update_data(change=item[message.text])
    if message.text == 'Изображение новости':
        await message.answer(
            "Вы выбрали, то что хотите изменить. Отправьте изображению товара"
        )
    else:
        await message.answer(
            "Вы выбрали, то что хотите изменить. Напишите новое изменение"
        )
    await state.set_state(ChangeNewsState.new_change)
    
@router_news.message(ChangeNewsState.new_change, F.text)
async def cmd_changeNewsNew(message: Message, state: FSMContext):
    """
    Change news - new_change (text)
    """
    await state.update_data(new_change=message.text)
    await message.answer(
        "Данные сохранены"
    )
    data = await state.get_data()
    name = data["name"]
    change = data["change"]
    new_change = data["new_change"]
    
    await update_news(name, change, new_change)
    await state.clear()
    
@router_news.message(ChangeNewsState.new_change, F.photo)
async def cmd_changeNewsNew(message: Message, state: FSMContext):
    """
    Change news - new_change (photo)
    """
    await state.update_data(new_change=message.photo[-1].file_id)
    await message.answer(
        "Данные сохранены",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    change = data["change"]
    new_change = data["new_change"]
    
    await update_news(name, change, new_change)
    await state.clear()
    
# НАЧАЛО УДАЛЕНИЕ НОВОСТЕЙ
@router_news.message(F.text == 'Удалить новости')
async def cmd_deleteNews(message: Message, state: FSMContext):
    """
    Delete news
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "удаляет новости"
    )
    await message.answer(
        "Процесс удаление новости запущен. Выберите новость",
        reply_markup=await bd.delete_news_b()
    )
    await state.set_state(DeleteNewsState.name)
    
@router_news.callback_query(DeleteNewsState.name, F.data.startswith('delete_news_'))
async def cmd_deleteNewsName(callback: CallbackQuery, state: FSMContext):
    """
    Delete news - name
    """
    await state.update_data(name=callback.data.split('_')[-1])
    await callback.answer('')
    await callback.message.answer(
        "Новости удалены",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data['name']
    
    await delete_news_i(name)
    await state.clear()