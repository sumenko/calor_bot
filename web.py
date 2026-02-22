import os
import asyncpg
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
}

db_pool = None


@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(**DB_CONFIG)


@app.get("/", response_class=HTMLResponse)
async def show_messages(timezone: str = Query("UTC")):
    """
    Пример запроса:
    http://localhost:8000/?timezone=Europe/Moscow
    """

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT created_at, username, text
            FROM messages
            ORDER BY created_at DESC
            LIMIT 100
        """)

    tz = ZoneInfo(timezone)

    table_rows = ""

    for row in rows:
        local_time = row["created_at"].astimezone(tz)
        table_rows += f"""
        <tr>
            <td>{local_time.strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td>{row['username'] or ''}</td>
            <td>{row['text']}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Calor Messages</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Messages (Timezone: {timezone})</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Username</th>
                <th>Message</th>
            </tr>
            {table_rows}
        </table>
    </body>
    </html>
    """

    return html