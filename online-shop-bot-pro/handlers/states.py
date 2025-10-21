from aiogram.fsm.state import State, StatesGroup

class CategoryAddState(StatesGroup):
    name = State()
    icon = State()
    

class ProductAddState(StatesGroup):
    name = State()
    price = State()
    category = State()

class ProductImageState(StatesGroup):
    product_id = State()
    image = State()
    
class AddProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_image = State()
    waiting_for_characteristics = State()
    
class ProductState(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_image = State()
    waiting_for_characteristics = State()