import aiosqlite as sql

async def create_table() -> None:
    async with sql.connect('database.db') as db:
        cursor = await db.cursor()
        await cursor.execute("""CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY,
            username TEXT,
            id_tg INTEGER,
            status INTEGER)""")
        await db.commit()
        
        await cursor.execute("""CREATE TABLE IF NOT EXISTS Category (
            id INTEGER PRIMARY KEY,
            name TEXT)""")
        await db.commit()
        
        await cursor.execute("""CREATE TABLE IF NOT EXISTS Item (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            price INTEGER,
            photo TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES Category (id))""")
        await db.commit()
        
        await cursor.execute("""CREATE TABLE IF NOT EXISTS News (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            photo TEXT)""")
        await db.commit()