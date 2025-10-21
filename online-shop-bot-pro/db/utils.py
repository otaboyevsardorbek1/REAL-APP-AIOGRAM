from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from db.models import session

def safe_db_call(default=None, log=True):
    """
    Bazaviy xatolikni ushlovchi dekorator.
    - default: Xatolik bo'lsa qaytariladigan qiymat
    - log: True bo‘lsa xatoliklarni print qiladi
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                session.commit()
                return result
            except SQLAlchemyError as e:
                session.rollback()
                if log:
                    print(f"[SQLAlchemy XATO] {func.__name__}: {e}")
                return default
            except Exception as e:
                if log:
                    print(f"[Umumiy XATO] {func.__name__}: {e}")
                return default
        return wrapper
    return decorator
