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


async def create_meeting(title, organizer_id, user_ids, start_ts, end_ts, link=None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO meetings (title, organizer_id, start_ts, end_ts, link, reminded) "
            "VALUES (?, ?, ?, ?, ?, 0)",
            (title, organizer_id, start_ts, end_ts, link),
        )
        meeting_id = cur.lastrowid
        for uid in user_ids:
            await db.execute(
                "INSERT OR IGNORE INTO attendees (meeting_id, user_id) VALUES (?, ?)",
                (meeting_id, uid),
            )
        await db.commit()
    return meeting_id


async def get_attendee_names(meeting_id):
    query = (
        "SELECT u.name FROM attendees a "
        "JOIN users u ON u.telegram_id = a.user_id WHERE a.meeting_id = ?"
    )
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(query, (meeting_id,))
        rows = await cur.fetchall()
    return [r[0] for r in rows]


async def get_meetings_between(start_ts, end_ts):
    query = (
        "SELECT id, title, start_ts, end_ts, link FROM meetings "
        "WHERE start_ts < ? AND end_ts > ? ORDER BY start_ts"
    )
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(query, (end_ts, start_ts))
        return await cur.fetchall()


async def get_user_meetings(user_id):
    query = (
        "SELECT m.id, m.title, m.start_ts, m.end_ts, m.link FROM meetings m "
        "JOIN attendees a ON a.meeting_id = m.id WHERE a.user_id = ? "
        "ORDER BY m.start_ts"
    )
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(query, (user_id,))
        return await cur.fetchall()


async def get_due_reminders(now_ts, window_ts):
    query = (
        "SELECT id, title, start_ts, link FROM meetings "
        "WHERE reminded = 0 AND start_ts > ? AND start_ts <= ? ORDER BY start_ts"
    )
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(query, (now_ts, window_ts))
        return await cur.fetchall()


async def mark_reminded(meeting_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE meetings SET reminded = 1 WHERE id = ?", (meeting_id,))
        await db.commit()


async def get_attendee_ids(meeting_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM attendees WHERE meeting_id = ?", (meeting_id,))
        rows = await cur.fetchall()
    return [r[0] for r in rows]
