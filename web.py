import os
import asyncpg
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

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
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("index.html")
    lines = []
    for row in rows:
        local_time = row["created_at"].astimezone(tz)
        lines.append(
            {
            'timestamp': local_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': row['text'],
            'username': row['username']
            })
    
    context = {
        'lines' :  lines
    }

    html = template.render(context)

    return html