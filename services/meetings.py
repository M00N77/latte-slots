import aiosqlite

from db import DB_PATH


async def get_registered_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT telegram_id, name FROM users")
        return await cur.fetchall()


async def has_conflict(user_ids, start_ts, end_ts):
    if not user_ids:
        return []
    placeholders = ",".join("?" for _ in user_ids)
    query = (
        "SELECT DISTINCT a.user_id, u.name, m.title, m.start_ts, m.end_ts "
        "FROM meetings m "
        "JOIN attendees a ON a.meeting_id = m.id "
        "JOIN users u ON u.telegram_id = a.user_id "
        f"WHERE a.user_id IN ({placeholders}) AND m.start_ts < ? AND m.end_ts > ?"
    )
    params = list(user_ids) + [end_ts, start_ts]
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(query, params)
        return await cur.fetchall()


async def create_meeting(title, organizer_id, user_ids, start_ts, end_ts):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO meetings (title, organizer_id, start_ts, end_ts) VALUES (?, ?, ?, ?)",
            (title, organizer_id, start_ts, end_ts),
        )
        meeting_id = cur.lastrowid
        for uid in user_ids:
            await db.execute(
                "INSERT OR IGNORE INTO attendees (meeting_id, user_id) VALUES (?, ?)",
                (meeting_id, uid),
            )
        await db.commit()
    return meeting_id
