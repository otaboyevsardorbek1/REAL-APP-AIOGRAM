# from sqlalchemy.orm import Session
# from models import User, Product, Category, ProductImage, Characteristic
# from storage import increase_storage, decrease_storage

# # USER
# def create_user(session: Session, tg_id: int, name: str, **kwargs):
#     user = User(tg_id=tg_id, name=name, **kwargs)
#     session.add(user)
#     session.commit()
#     return user

# def get_user(session: Session, tg_id: int):
#     return session.query(User).filter_by(tg_id=tg_id).first()

# def update_user(session: Session, tg_id: int, **kwargs):
#     user = get_user(session, tg_id)
#     if user:
#         for key, value in kwargs.items():
#             setattr(user, key, value)
#         session.commit()
#     return user

# def delete_user(session: Session, tg_id: int):
#     user = get_user(session, tg_id)
#     if user:
#         session.delete(user)
#         session.commit()

# def count_users(session: Session):
#     return session.query(User).count()
# # CATEGORY
# def create_category(session: Session, tg_id: int, name: str, icon_url=None):
#     category = Category(tg_id=tg_id, name=name, icon_url=icon_url)
#     session.add(category)
#     session.commit()
#     return category
# def get_category(session: Session, category_id: int):
#     return session.query(Category).filter_by(id=category_id).first()
# def update_category(session: Session, category_id: int, **kwargs):
#     category = get_category(session, category_id)
#     if category:
#         for key, value in kwargs.items():
#             setattr(category, key, value)
#         session.commit()
#     return category
# def delete_category(session: Session, category_id: int):
#     category = get_category(session, category_id)
#     if category:
#         session.delete(category)
#         session.commit()
#         return category
# def count_categories(session: Session, tg_id: int):
#     return session.query(Category).filter_by(tg_id=tg_id).count()
# # PRODUCT
# def create_product(session: Session, tg_id: int, name: str, price: float, category_id=None):
#     product = Product(tg_id=tg_id, name=name, price=price, category_id=category_id)
#     session.add(product)
#     session.commit()
#     return product

# def get_product(session: Session, product_id: int):
#     return session.query(Product).filter_by(id=product_id).first()
# def update_product(session: Session, product_id: int, **kwargs):
#     product = get_product(session, product_id)
#     if product:
#         for key, value in kwargs.items():
#             setattr(product, key, value)
#         session.commit()
#     return product
# def delete_product(session: Session, product_id: int):
#     product = get_product(session, product_id)
#     if product:
#         session.delete(product)
#         session.commit()
#         decrease_storage(session, product_id, product.price)  # Assuming price is used as size for storage
#         return product
# def count_products(session: Session, tg_id: int):
#     return session.query(Product).filter_by(tg_id=tg_id).count()
# # PRODUCT IMAGE
# def add_product_image(session: Session, product_id: int, url: str, size: int):
#     image = ProductImage(product_id=product_id, url=url, size=size)
#     session.add(image)
#     session.commit()
#     increase_storage(session, product_id, size)
#     return image
# def get_product_image(session: Session, image_id: int):
#     return session.query(ProductImage).filter_by(id=image_id).first()
# def update_product_image(session: Session, image_id: int, **kwargs):
#     image = get_product_image(session, image_id)
#     if image:
#         for key, value in kwargs.items():
#             setattr(image, key, value)
#         session.commit()
#     return image

# def delete_product_image(session: Session, image_id: int):
#     image = get_product_image(session, image_id)
#     if image:
#         size = image.size
#         product_id = image.product_id
#         session.delete(image)
#         session.commit()
#         decrease_storage(session, product_id, size)
# def count_product_images(session: Session, product_id: int):
#     return session.query(ProductImage).filter_by(product_id=product_id).count()
# # CHARACTERISTIC
# def add_characteristic(session: Session, product_id: int, title: str, value: str):
#     char = Characteristic(product_id=product_id, character_title=title, character_value=value)
#     session.add(char)
#     session.commit()
#     return char
# def get_characteristic(session: Session, char_id: int):
#     return session.query(Characteristic).filter_by(id=char_id).first()
# def update_characteristic(session: Session, char_id: int, **kwargs):
#     char = get_characteristic(session, char_id)
#     if char:
#         for key, value in kwargs.items():
#             setattr(char, key, value)
#         session.commit()
#     return char
# def delete_characteristic(session: Session, char_id: int):
#     char = get_characteristic(session, char_id)
#     if char:
#         session.delete(char)
#         session.commit()
#         return char
# def count_products_in_category(session: Session, category_id: int):
#     return session.query(Product).filter_by(category_id=category_id).count()


from sqlalchemy.orm import Session
from models import User, Product, Category, ProductImage, Characteristic
from storage import increase_storage, decrease_storage


# ========================
# USER SERVICES
# ========================
def create_user(session: Session, tg_id: int, name: str, **kwargs):
    user = User(tg_id=tg_id, name=name, **kwargs)
    session.add(user)
    session.commit()
    return user

def get_user(session: Session, tg_id: int):
    return session.query(User).filter_by(tg_id=tg_id).first()

def update_user(session: Session, tg_id: int, **kwargs):
    user = get_user(session, tg_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        session.commit()
    return user

def delete_user(session: Session, tg_id: int):
    user = get_user(session, tg_id)
    if user:
        session.delete(user)
        session.commit()

def count_users(session: Session):
    return session.query(User).count()


# ========================
# CATEGORY SERVICES
# ========================
def create_category(session: Session, tg_id: int, name: str, icon_url: str = None):
    category = Category(tg_id=tg_id, name=name, icon_url=icon_url)
    session.add(category)
    session.commit()
    return category

def get_category(session: Session, category_id: int):
    return session.query(Category).filter_by(id=category_id).first()

def update_category(session: Session, category_id: int, **kwargs):
    category = get_category(session, category_id)
    if category:
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)
        session.commit()
    return category

def delete_category(session: Session, category_id: int):
    category = get_category(session, category_id)
    if category:
        session.delete(category)
        session.commit()
        return category

def count_categories(session: Session, tg_id: int):
    return session.query(Category).filter_by(tg_id=tg_id).count()


# ========================
# PRODUCT SERVICES
# ========================
def create_product(session: Session, tg_id: int, name: str, price: float, category_id: int = None):
    product = Product(tg_id=tg_id, name=name, price=price, category_id=category_id)
    session.add(product)
    session.commit()
    return product

def get_product(session: Session, product_id: int):
    return session.query(Product).filter_by(id=product_id).first()

def update_product(session: Session, product_id: int, **kwargs):
    product = get_product(session, product_id)
    if product:
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        session.commit()
    return product

def delete_product(session: Session, product_id: int):
    product = get_product(session, product_id)
    if product:
        session.delete(product)
        session.commit()
        # If price is considered as storage, decrease it
        decrease_storage(session, product.tg_id, product.price)
        return product

def count_products(session: Session, tg_id: int):
    return session.query(Product).filter_by(tg_id=tg_id).count()


# ========================
# PRODUCT IMAGE SERVICES
# ========================
def add_product_image(session: Session, product_id: int, url: str, size: int):
    image = ProductImage(product_id=product_id, url=url, size=size)
    session.add(image)
    session.commit()
    product = get_product(session, product_id)
    if product:
        increase_storage(session, product.tg_id, size)
    return image

def get_product_image(session: Session, image_id: int):
    return session.query(ProductImage).filter_by(id=image_id).first()

def update_product_image(session: Session, image_id: int, **kwargs):
    image = get_product_image(session, image_id)
    if image:
        for key, value in kwargs.items():
            if hasattr(image, key):
                setattr(image, key, value)
        session.commit()
    return image

def delete_product_image(session: Session, image_id: int):
    image = get_product_image(session, image_id)
    if image:
        size = image.size
        product = get_product(session, image.product_id)
        session.delete(image)
        session.commit()
        if product:
            decrease_storage(session, product.tg_id, size)
        return image

def count_product_images(session: Session, product_id: int):
    return session.query(ProductImage).filter_by(product_id=product_id).count()


# ========================
# CHARACTERISTIC SERVICES
# ========================
def add_characteristic(session: Session, product_id: int, title: str, value: str):
    char = Characteristic(product_id=product_id, character_title=title, character_value=value)
    session.add(char)
    session.commit()
    return char

def get_characteristic(session: Session, char_id: int):
    return session.query(Characteristic).filter_by(id=char_id).first()

def update_characteristic(session: Session, char_id: int, **kwargs):
    char = get_characteristic(session, char_id)
    if char:
        for key, value in kwargs.items():
            if hasattr(char, key):
                setattr(char, key, value)
        session.commit()
    return char

def delete_characteristic(session: Session, char_id: int):
    char = get_characteristic(session, char_id)
    if char:
        session.delete(char)
        session.commit()
        return char

def count_products_in_category(session: Session, category_id: int):
    return session.query(Product).filter_by(category_id=category_id).count()
