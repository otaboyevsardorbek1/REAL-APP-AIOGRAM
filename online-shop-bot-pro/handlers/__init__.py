from aiogram import Dispatcher
from .start import router as start_router
from .nofactins_admins import nofactins_admin
# from .settings import router as settings_router
# from .biznes import router as biznes_router
# from .add_product import router as add_product_router
# from .view_products import router as view_products_router
# from .delete_product import router as delete_product_router
# from .edit_product import router as edit_product_router
# from .admin_category import router as admin_category_router
# from .product import router as product_router
# from .statistics import router as statistics_router
from .owner_log import router_owner

def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    
    # dp.include_router(settings_router)
    # dp.include_router(biznes_router)
    # dp.include_router(add_product_router)
    dp.include_router(router_owner)
    # dp.include_router(view_products_router)
    # dp.include_router(delete_product_router)
    # dp.include_router(edit_product_router)
    # dp.include_router(admin_category_router)
    # dp.include_router(product_router)
    # dp.include_router(statistics_router)
