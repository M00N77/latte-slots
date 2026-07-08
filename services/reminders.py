import asyncio
import logging

from datetime import datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE
from services import meetings as svc

TZ = ZoneInfo(TIMEZONE)
logger = logging.getLogger(__name__)


async def reminder_loop(bot):
    while True:
        try:
            now = int(datetime.now(TZ).timestamp())
            window = now + 30 * 60
            due = await svc.get_due_reminders(now, window)
            for mid, title, start_ts, link in due:
                mins = max(1, round((start_ts - now) / 60))
                when = datetime.fromtimestamp(start_ts, TZ).strftime("%d.%m %H:%M")
                text = f"⏰ Через ~{mins} мин встреча «{title}» ({when})"
                if link:
                    text += f"\n🔗 {link}"
                for uid in await svc.get_attendee_ids(mid):
                    try:
                        await bot.send_message(uid, text)
                    except Exception as e:
                        logger.warning("reminder send failed for %s: %s", uid, e)
                await svc.mark_reminded(mid)
        except Exception as e:
            logger.warning("reminder loop error: %s", e)
        await asyncio.sleep(60)
