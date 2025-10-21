import logging

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.requests import insert_category, update_category_name, delete_category_p
from app.common.filters import IsAdminFilter, ChatTypeFilter
import app.keyboards.builder as bd
import app.keyboards.reply as rp

router_category = Router()
router_category.message.filter(IsAdminFilter(), ChatTypeFilter(['private']))

logger = logging.getLogger(__name__)

class CategoryState(StatesGroup):
    name = State()

class ChangeCategoryState(StatesGroup):
    name = State()
    new_name = State()
    
class DeleteCategory(StatesGroup):
    name = State()

# НАЧАЛО СОЗДАНИЕ КАТЕГОРИИ
@router_category.message(StateFilter(None), F.text == 'Добавить категорию')
async def cmd_addCategory(message: Message, state: FSMContext):
    """
    Add categories
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "добавляет категорию"
    )
    await message.answer(
        'Процесс добавления категории запущена. Введите название категории',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CategoryState.name)

# Отмена действия
@router_category.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Cancel action
    """
    current_state = await state.get_state()
    if current_state is None:
        await state.set_data({})
        await message.answer(
            text="Нечего отменять",
            reply_markup=ReplyKeyboardRemove()
        )
        logger.debug(
            f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
            "не смог отменить действие"
        )
    else:
        await state.clear()
        await message.answer(
            text="Действие отменено",
            reply_markup=ReplyKeyboardRemove()
        )
        logger.debug(
            f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
            "отменил действие"
        )
    
@router_category.message(CategoryState.name, F.text)
async def cmd_addCategoryName(message: Message, state: FSMContext):
    """
    Add categories - name
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "добавил категорию"
    )
    await state.update_data(name=message.text)
    await message.answer(
        f'Данные категории сохранены',
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    
    await insert_category(name)
    await state.clear()
    
# НАЧАЛА ИЗМЕНЕНИЕ КАТЕГОРИИ
@router_category.message(StateFilter(None), F.text == 'Изменить категорию')
async def cmd_changeCategory(message: Message, state: FSMContext):
    """
    Change categories
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "изменяет категорию"
    )
    await message.answer(
        'Процесс изменения категории запущена. Выберите категорию',
        reply_markup=await bd.change_category()
    )
    await state.set_state(ChangeCategoryState.name)
    
@router_category.callback_query(ChangeCategoryState.name, F.data.startswith('change_category_'))
async def change_category_name(callback: CallbackQuery, state: FSMContext):
    """
    Change categories - name
    """
    await state.update_data(name=callback.data.split('_')[-1])
    await callback.answer()
    await callback.message.answer(
        "Название категории сохранено. Введите новое название",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ChangeCategoryState.new_name)
    
@router_category.message(ChangeCategoryState.new_name, F.text)
async def cmd_changeCategoryName(message: Message, state: FSMContext):
    """
    Change categories - new_name
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "изменил категорию"
    )
    await state.update_data(new_name=message.text)
    await message.answer(
        "Название новой категории сохранено. Данные сохранены",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    new_name = data["new_name"]
    
    await update_category_name(name, new_name)
    await state.clear()
    
    
# НАЧАЛО УДАЛЕНИЕ КАТЕГОРИИ
@router_category.message(StateFilter(None), F.text == 'Удалить категорию')
async def cmd_deleteCategory(message: Message, state: FSMContext):
    """
    Remove categories
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "удаляет категорию"
    )
    await message.answer(
        "Вы запустили процесс удаление категории. Выберите категорию",
        reply_markup=await bd.delete_category()
    )
    await state.set_state(DeleteCategory.name)
    
@router_category.callback_query(DeleteCategory.name, F.data.startswith('delete_category_'))
async def cmd_deleteCategoryName(callback: CallbackQuery, state: FSMContext):
    """
    Remove categories - name
    """
    logger.debug(
        f"Пользователь {callback.from_user.username} ({callback.from_user.id}) - "
        "удалил категорию"
    )
    await state.update_data(name=int(callback.data.split('_')[-1]))
    await callback.answer()
    await callback.message.answer(
        "Вы удалили категорию успешно",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    
    await delete_category_p(name)
    await state.clear()