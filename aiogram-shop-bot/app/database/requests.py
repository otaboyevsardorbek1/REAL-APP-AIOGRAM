from typing import Any
import aiosqlite as sql

"""
SQLITE: SELECT
"""
async def select_user_all() -> Any:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM User")
        return await cursor.fetchall()
    
async def select_user_id(id_tg: int) -> Any:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM User WHERE id_tg = ?", (id_tg,))
        return await cursor.fetchone()
    
async def select_category_all() -> Any:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM Category")
        return await cursor.fetchall()
    
async def select_item_all() -> Any:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM Item")
        return await cursor.fetchall()
    
async def select_items_id(number: int) -> Any:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM Item WHERE category_id = ?", (number,))
        return await cursor.fetchall()
    
async def select_item_id(number: int) -> Any:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM Item WHERE id = ?", (number,))
        return await cursor.fetchone()
    
async def select_news_all():
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM News")
        return await cursor.fetchall()

async def select_news_id(number: int):
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM News WHERE id = ?", (number,))
        return await cursor.fetchone()

"""
SQLITE: INSERT
"""
async def insert_user(username: str, id_tg: int) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("INSERT INTO User (username, id_tg, status) VALUES (?, ?, 0)", (username, id_tg))
        await db.commit()
        
async def insert_category(name: str) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("INSERT INTO Category (name) VALUES (?)", (name,))
        await db.commit()
        
async def insert_item(
    name: str,
    desc: str,
    price: int,
    photo: str,
    category: int
) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(
            "INSERT INTO Item (name, description, price, photo, category_id) VALUES (?, ?, ?, ?, ?)",
            (name, desc, price, photo, category)
        )
        await db.commit()
        
async def insert_news(name: str, description: str, photo: str):
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute(
            "INSERT INTO News (name, description, photo) VALUES (?, ?, ?)",
            (name, description, photo)
        )
        await db.commit()
        
"""
SQLITE: UPDATE
"""
async def update_user(username: str, id_tg: int) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE User SET username = ? WHERE id_tg = ?", (username, id_tg))
        await db.commit()
        
async def update_admin(id_tg: int) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE User SET status = 1 WHERE id_tg = ?", (id_tg,))
        await db.commit()
        
async def update_admin_no(id_tg: int) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE User SET status = 0 WHERE id_tg = ?", (id_tg,))
        await db.commit()
        
async def update_category_name(name: int, new_name: str) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE Category SET name = ? WHERE  id = ?", (new_name, name))
        await db.commit()
        
async def update_item(
    number: str,
    change: str,
    new_change: str
) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        if change == 'name':
            await cursor.execute(
                "UPDATE Item SET name = ? WHERE id = ?",
                (new_change, number)
            )
        elif change == 'description':
            await cursor.execute(
                "UPDATE Item SET description = ? WHERE id = ?",
                (new_change, number)
            )
        elif change == 'price':
            await cursor.execute(
                "UPDATE Item SET price = ? WHERE id = ?",
                (new_change, number)
            )
        elif change == 'photo':
            await cursor.execute(
                "UPDATE Item SET photo = ? WHERE id = ?",
                (new_change, number)
            )
        await db.commit()
        
async def update_news(
    number: str,
    change: str,
    new_change: str
) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        if change == 'name':
            await cursor.execute(
                "UPDATE News SET name = ? WHERE id = ?",
                (new_change, number)
            )
        elif change == 'description':
            await cursor.execute(
                "UPDATE News SET description = ? WHERE id = ?",
                (new_change, number)
            )
        elif change == 'photo':
            await cursor.execute(
                "UPDATE News SET photo = ? WHERE id = ?",
                (new_change, number)
            )
        await db.commit()
        
async def update_status(id_user: int) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE User SET status = 2 WHERE id_tg = ?", (id_user,))
        await db.commit()
        
async def update_status_no(id_user: int) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("UPDATE User SET status = 0 WHERE id_tg = ?", (id_user,))
        await db.commit()
        
"""
SQLITE: DELETE
"""
async def delete_category_p(number: str) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM Category WHERE id = ?", (number,))
        await db.commit()
        
async def delete_item_i(number: str) -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM Item WHERE id = ?", (number,))
        await db.commit()
        
async def delete_news_i(number: int):
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM News WHERE id = ?", (number,))
        await db.commit()