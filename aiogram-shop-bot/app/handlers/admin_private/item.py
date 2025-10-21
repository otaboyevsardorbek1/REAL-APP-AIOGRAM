import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.requests import insert_item, update_item, delete_item_i
from app.common.filters import IsAdminFilter, ChatTypeFilter
import app.keyboards.builder as bd
import app.keyboards.reply as rp

router_item = Router()
router_item.message.filter(IsAdminFilter(), ChatTypeFilter(['private']))

logger = logging.getLogger(__name__)

class ItemState(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()
    category = State()
    
class ChangeItemState(StatesGroup):
    category = State()
    name = State()
    change = State()
    new_change = State()
    
class DeleteItemState(StatesGroup):
    category = State()
    name = State()


# НАЧАЛО ДОБАВЛЕНИЯ ТОВАРА
@router_item.message(StateFilter(None), F.text == 'Добавить товар')
async def cmd_addItem(message: Message, state: FSMContext):
    """
    Add item
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "добавляет товар"
    )
    await message.answer(
        "Процесс создания товара запущен. Введите название товара",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ItemState.name)
    
@router_item.message(ItemState.name, F.text)
async def cmd_addItemName(message: Message, state: FSMContext):
    """
    Add item - name
    """
    await state.update_data(name=message.text)
    await message.answer(
        "Название товара сохранено. Введите описание товара"
    )
    await state.set_state(ItemState.description)
    
@router_item.message(ItemState.description, F.text)
async def cmd_addItemDesc(message: Message, state: FSMContext):
    """
    Add item - desc
    """
    await state.update_data(description=message.text)
    await message.answer(
        "Описание товара сохранено. Введите цену товара"
    )
    await state.set_state(ItemState.price)
    
@router_item.message(ItemState.price, F.text)
async def cmd_addItemPrice(message: Message, state: FSMContext):
    """
    Add item - price
    """
    try:
        await state.update_data(price=int(message.text))
    except:
        await message.answer(
            "Ошибка: передан не правильный аргумент"
        )
        return
    await message.answer(
        "Цена товара сохранено. Отправьте фото товара"
    )
    await state.set_state(ItemState.image)
    
@router_item.message(ItemState.image, F.photo)
async def cmd_addItemImage(message: Message, state: FSMContext):
    """
    Add item - image
    """
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer(
        "Фото товара сохранено. Выберите категорию товара",
        reply_markup=await bd.add_item()
    )
    await state.set_state(ItemState.category)
    
@router_item.callback_query(ItemState.category, F.data)
async def cmd_addItemCategory(callback: CallbackQuery, state: FSMContext):
    """
    Add item - category
    """
    logger.debug(
        f"Пользователь {callback.from_user.username} ({callback.from_user.id}) - "
        "добавил товар"
    )
    await state.update_data(category=callback.data.split('_')[-1])
    await callback.answer('')
    await callback.message.answer(
        "Фото товара сохранено. Данные сохранены",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    photo = data["photo"]
    category = data["category"]
    
    await insert_item(
        name,
        description,
        price,
        photo,
        category
    )
    await state.clear()
    
# НАЧАЛО ИЗМЕНЕНИЯ ТОВАРА
@router_item.message(StateFilter(None), F.text == 'Изменить товар')
async def cmd_changeItem(message: Message, state: FSMContext):
    """
    Change item
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "изменяет товар"
    )
    await message.answer(
        "Процесс изменения товара запущен. Выберите категорию товара",
        reply_markup=await bd.change_category()
    )
    await state.set_state(ChangeItemState.category)
    
@router_item.callback_query(ChangeItemState.category, F.data)
async def cmd_changeItemCategory(callback: CallbackQuery, state: FSMContext):
    """
    Change item - category
    """
    await callback.answer('')
    await callback.message.answer(
        "Категория товара выбрана. Выберите товар",
        reply_markup=await bd.change_item(callback.data.split('_')[-1])
    )
    await state.set_state(ChangeItemState.name)
    
@router_item.callback_query(ChangeItemState.name, F.data)
async def cmd_changeItemName(callback: CallbackQuery, state: FSMContext):
    """
    Change item - name
    """
    await state.update_data(name=callback.data.split('_')[-1])
    await callback.answer('')
    await callback.message.answer(
        "Товар выбран. Выберите, что хотите изменить",
        reply_markup=rp.change_item_kb
    )
    await state.set_state(ChangeItemState.change)
    
@router_item.message(ChangeItemState.change, F.text.in_([
    'Название товара',
    'Описание товара',
    'Цена товара',
    'Изображение товара'
]))
async def cmd_changeItemOld(message: Message, state: FSMContext):
    """
    Change item - change
    """
    item_2 = {
        'Название товара': "name",
        'Описание товара': "description",
        'Цена товара': "price",
        'Изображение товара': "photo"
    }
    await state.update_data(change=item_2[message.text])
    await message.answer(
        f'Вы выбрали изменение. Напишите новое изменение',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ChangeItemState.new_change)
    
@router_item.message(ChangeItemState.new_change, F.text)
async def cmd_changeItemNew(message: Message, state: FSMContext):
    """
    Change item - new_change (text)
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "изменил товар"
    )
    await state.update_data(new_change=message.text)
    await message.answer(
        'Вы добавили изменения. Данные сохранены',
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data['name']
    change = data['change']
    new_change = data['new_change']
    
    await update_item(name, change, new_change)
    await state.clear()
    
@router_item.message(ChangeItemState.new_change, F.photo)
async def cmd_changeItemNew(message: Message, state: FSMContext):
    """
    Change item - new_change (photo)
    """
    await state.update_data(new_change=message.photo[-1].file_id)
    await message.answer(
        'Вы добавили изменения. Данные сохранены',
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data['name']
    change = data['change']
    new_change = data['new_change']
    
    await update_item(name, change, new_change)
    await state.clear()
    
# НАЧАЛО УДАЛЕНИЯ ТОВАРА
@router_item.message(F.text == 'Удалить товар')
async def cmd_removeItem(message: Message, state: FSMContext):
    """
    Remove item
    """
    logger.debug(
        f"Пользователь {message.from_user.username} ({message.from_user.id}) - "
        "удаляет товар"
    )
    await message.answer('', reply_markup=ReplyKeyboardRemove())
    await message.answer(
        "Процесс удаления товара запущен. Выберите в какой категории товар",
        reply_markup=await bd.delete_item_ct()
    )
    await state.set_state(DeleteItemState.category)
    
@router_item.callback_query(DeleteItemState.category, F.data)
async def cmd_removeItemCategory(callback: CallbackQuery, state: FSMContext):
    """
    Remove item - category
    """
    await callback.answer()
    await callback.message.answer(
        "Категория товара выбрана. Выберите товар",
        reply_markup=await bd.delete_item_it(callback.data.split('_')[-1])
    )
    await state.set_state(DeleteItemState.name)
    
@router_item.callback_query(DeleteItemState.name, F.data)
async def cmd_removeItemName(callback: CallbackQuery, state: FSMContext):
    """
    Remove item - name
    """
    await state.update_data(name=callback.data.split('_')[-1])
    await callback.answer('')
    await callback.message.answer(
        "Товар успешно удален",
        reply_markup=rp.admin_panel
    )
    data = await state.get_data()
    name = data["name"]
    
    await delete_item_i(name)
    await state.clear()