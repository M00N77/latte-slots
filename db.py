import os

import aiosqlite

DB_PATH = os.getenv("DB_PATH", "meetings.db")
_db_dir = os.path.dirname(DB_PATH)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "telegram_id INTEGER PRIMARY KEY, name TEXT, username TEXT)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS meetings ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, "
            "organizer_id INTEGER NOT NULL, start_ts INTEGER NOT NULL, end_ts INTEGER NOT NULL, "
            "link TEXT, reminded INTEGER DEFAULT 0)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS attendees ("
            "meeting_id INTEGER NOT NULL, user_id INTEGER NOT NULL, "
            "PRIMARY KEY (meeting_id, user_id))"
        )
        for stmt in (
            "ALTER TABLE meetings ADD COLUMN link TEXT",
            "ALTER TABLE meetings ADD COLUMN reminded INTEGER DEFAULT 0",
        ):
            try:
                await db.execute(stmt)
            except Exception:
                pass
        await db.commit()


async def upsert_user(telegram_id, name, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (telegram_id, name, username) VALUES (?, ?, ?) "
            "ON CONFLICT(telegram_id) DO UPDATE SET name=excluded.name, username=excluded.username",
            (telegram_id, name, username),
        )
        await db.commit()
