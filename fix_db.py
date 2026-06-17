content = r'''
import aiosqlite
from datetime import datetime

DB_PATH = "data/database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                unique_id TEXT,
                language TEXT DEFAULT 'ru',
                premium INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0,
                balance INTEGER DEFAULT 0,
                subscription_until TEXT,
                notifications_enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                prompt_id TEXT,
                PRIMARY KEY (user_id, prompt_id)
            );
            CREATE TABLE IF NOT EXISTS purchased_prompts (
                user_id INTEGER,
                prompt_id TEXT,
                PRIMARY KEY (user_id, prompt_id)
            );
            CREATE TABLE IF NOT EXISTS referrals (
                referrer_id INTEGER,
                referred_id INTEGER,
                date TEXT,
                bonus_given INTEGER DEFAULT 0,
                PRIMARY KEY (referrer_id, referred_id)
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            );
        """)
        await db.commit()

async def upsert_user(user_id, username=None):
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        if await existing.fetchone():
            if username:
                await db.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
        else:
            now = datetime.now()
            unique = f"{str(user_id)[:2]}{now.strftime('%y')}{now.strftime('%d%m')}{str(user_id)[-4:]}"
            await db.execute("INSERT INTO users(user_id,username,unique_id) VALUES(?,?,?)",
                             (user_id, username or "", unique))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cursor.fetchone()

async def set_user_language(user_id, lang):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
        await db.commit()

async def update_user_balance(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def add_favorite(user_id, prompt_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO favorites(user_id,prompt_id) VALUES(?,?)", (user_id, prompt_id))
        await db.commit()

async def remove_favorite(user_id, prompt_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM favorites WHERE user_id=? AND prompt_id=?", (user_id, prompt_id))
        await db.commit()

async def get_favorites(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT prompt_id FROM favorites WHERE user_id=?", (user_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def has_purchased(user_id, prompt_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM purchased_prompts WHERE user_id=? AND prompt_id=?", (user_id, prompt_id))
        return await cursor.fetchone() is not None

async def add_purchased(user_id, prompt_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO purchased_prompts(user_id,prompt_id) VALUES(?,?)", (user_id, prompt_id))
        await db.commit()

async def ban_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET banned=1 WHERE user_id=?", (user_id,))
        await db.commit()

async def unban_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET banned=0 WHERE user_id=?", (user_id,))
        await db.commit()

async def add_referral(referrer_id, referred_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO referrals(referrer_id,referred_id,date) VALUES(?,?,?)",
                         (referrer_id, referred_id, datetime.now().isoformat()))
        await db.commit()

async def get_referral_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT referred_id FROM referrals WHERE referrer_id=?", (user_id,))
        referred = await cursor.fetchall()
        invited_count = len(referred)
        active = 0
        subscribed = 0
        for (ref_id,) in referred:
            ref_user = await get_user(ref_id)
            if ref_user:
                if ref_user[6] > 0:
                    active += 1
                if ref_user[8]:
                    subscribed += 1
        total_earned = invited_count * 69
        available = int(total_earned * 0.4)
        return invited_count, active, subscribed, total_earned, available, 0
'''

with open("utils/db.py", "w", encoding="utf-8") as f:
    f.write(content.strip())

print("✅ utils/db.py успешно перезаписан!")