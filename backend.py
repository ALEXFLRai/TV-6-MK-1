from __future__ import annotations

import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from nicegui import app as ng_app
from nicegui import ui


# ============================================================
# НАСТРОЙКИ
# ============================================================

ADMIN_PASSWORD = "hffooA9GTMnpIZH1k0i!8^AHVqZ!L5l7"  # ПАРОЛЬ АДМИНИСТРАТОРА

PORT = int(
    os.getenv(
        "TV6MK_PORT",
        "8000",
    )
)


# ============================================================
# БАЗА ДАННЫХ
# ============================================================

if os.name == "nt":
    DATA_DIR = (
        Path(
            os.getenv(
                "LOCALAPPDATA",
                str(Path.home()),
            )
        )
        / "TV6MK-1"
    )
else:
    DATA_DIR = Path.home() / ".tv6mk-1"


DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DB_PATH = DATA_DIR / "tv6mk.sqlite3"

STORAGE_SECRET = os.getenv(
    "TV6MK_STORAGE_SECRET",
    secrets.token_urlsafe(32),
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="6МК",
    version="1.0.0",
)


# ============================================================
# SQLITE
# ============================================================

@contextmanager
def database():
    connection = sqlite3.connect(
        DB_PATH,
        timeout=5,
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    connection.execute(
        "PRAGMA busy_timeout = 5000"
    )

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def init_database():
    with database() as connection:

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
                    CHECK(length(name) BETWEEN 1 AND 120),
                description TEXT,
                avatar_url TEXT,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
                    CHECK(length(title) BETWEEN 1 AND 160),
                body TEXT NOT NULL
                    CHECK(length(body) BETWEEN 1 AND 5000),
                image_url TEXT,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
                    CHECK(length(title) BETWEEN 1 AND 160),
                provider TEXT NOT NULL
                    DEFAULT 'youtube'
                    CHECK(provider = 'youtube'),
                video_id TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_news_created_at
                ON news(created_at DESC);

            CREATE INDEX IF NOT EXISTS idx_students_name
                ON students(name);

            CREATE INDEX IF NOT EXISTS idx_videos_created_at
                ON videos(created_at DESC);
            """
        )

        existing_students = connection.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if existing_students == 0:

            students = [
                ("Алиев Исмаил", "Люблю футбол."),
                ("Баскаков Фёдор", "Маткласс, рисую, путешествую."),
                ("Белоусова Дарья", "Художка, психология, кофе."),
                ("Боева Пелагея", "Загадочная."),
                ("Гусева Ксения", "Музыка, танцы."),
                ("Ермилов Михаил", "Загадочный."),
                ("Ефремов Михаил", "Загадочный."),
                ("Знаменская Вероника", "Гитара, рисование."),
                (
                    "Карлова Ярослава",
                    "Веду канал и приложение, мечтаю о ЛЕТОВО.",
                ),
                ("Клименко Глеб", "Загадочный."),
                ("Коврижкин Кирилл", "Загадочный."),
                ("Куликов Герман", "Загадочный."),
                ("Лобанов Глеб", "Футбол, дружу со всеми."),
                ("Лысенко Анастасия", "Чтение, бисер, фортепиано."),
                ("Минасян Марк", "Загадочный."),
                ("Мовсумов Мурад", "Футбол, шахматы, каратэ."),
                ("Пигальцина Анна", "Сладкое, Гарри Поттер."),
                ("Рахимов Даниэль", "Дзюдо, футбол, фигурки."),
                ("Рогов Денис", "Загадочный."),
                ("Середенко Алексей", "Загадочный."),
                ("Сергеев Григорий", "Чтение, математика, игры."),
                ("Соболева Анна", "Загадочная."),
                (
                    "Соковикова Виктория",
                    "Хоккей, ракетостроение, литература.",
                ),
                ("Тен Кирилл", "История, программирование."),
                (
                    "Тимошина Виктория",
                    "Танцы, волейбол, рисование.",
                ),
                ("Тютюгин Александр", "Загадочный."),
                ("Фатуллаева Диана", "Загадочная."),
                ("Филатова Ксения", "Вокал, танцы."),
                ("Харитонов Родион", "Люблю странности."),
                ("Шкода Артём", "Информатика."),
            ]

            connection.executemany(
                """
                INSERT INTO students (
                    name,
                    description
                )
                VALUES (?, ?)
                """,
                students,
            )


init_database()


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def normalize_text(value: str) -> str:
    value = value.lower()
    value = value.replace("ё", "е")
    value = re.sub(r"[^а-яa-z0-9\s-]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def is_admin() -> bool:
    return bool(
        ng_app.storage.user.get(
            "is_admin",
            False,
        )
    )


def require_admin():
    if not is_admin():
        raise PermissionError(
            "Недостаточно прав администратора."
        )


def valid_https_url(
    value: str | None,
) -> str | None:

    if not value:
        return None

    value = value.strip()

    if not value:
        return None

    if len(value) > 2048:
        raise ValueError(
            "URL слишком длинный."
        )

    if not value.lower().startswith("https://"):
        raise ValueError(
            "Разрешены только HTTPS-ссылки."
        )

    return value


def validate_youtube_id(
    value: str,
) -> str:

    value = value.strip()

    if not re.fullmatch(
        r"[A-Za-z0-9_-]{6,32}",
        value,
    ):
        raise ValueError(
            "Некорректный YouTube ID."
        )

    return value


def authenticate_admin(
    password: str,
) -> bool:

    if not ADMIN_PASSWORD:
        return False

    return secrets.compare_digest(
        password,
        ADMIN_PASSWORD,
    )


# ============================================================
# ПОЛУЧЕНИЕ ДАННЫХ
# ============================================================

def get_news(
    limit: int = 24,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 100),
    )

    with database() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                title,
                body,
                image_url,
                created_at
            FROM news
            ORDER BY
                created_at DESC,
                id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_students(
    limit: int = 500,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 500),
    )

    with database() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                name,
                description,
                avatar_url,
                created_at
            FROM students
            ORDER BY
                name COLLATE NOCASE,
                id
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_videos(
    limit: int = 50,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(int(limit), 100),
    )

    with database() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                title,
                provider,
                video_id,
                created_at
            FROM videos
            ORDER BY
                created_at DESC,
                id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_statistics() -> dict[str, int]:

    with database() as connection:

        students = connection.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        news = connection.execute(
            "SELECT COUNT(*) FROM news"
        ).fetchone()[0]

        videos = connection.execute(
            "SELECT COUNT(*) FROM videos"
        ).fetchone()[0]

    return {
        "students": int(students),
        "news": int(news),
        "videos": int(videos),
    }


# ============================================================
# АДМИНСКИЕ ОПЕРАЦИИ
# ============================================================

def add_news(
    title: str,
    body: str,
    image_url: str | None = None,
) -> int:

    require_admin()

    title = title.strip()
    body = body.strip()

    if not 1 <= len(title) <= 160:
        raise ValueError(
            "Заголовок должен быть 1–160 символов."
        )

    if not 1 <= len(body) <= 5000:
        raise ValueError(
            "Текст должен быть 1–5000 символов."
        )

    image_url = valid_https_url(
        image_url
    )

    with database() as connection:

        cursor = connection.execute(
            """
            INSERT INTO news (
                title,
                body,
                image_url
            )
            VALUES (?, ?, ?)
            """,
            (
                title,
                body,
                image_url,
            ),
        )

        return int(cursor.lastrowid)


def add_student(
    name: str,
    description: str | None = None,
    avatar_url: str | None = None,
) -> int:

    require_admin()

    name = name.strip()

    if not 1 <= len(name) <= 120:
        raise ValueError(
            "Имя должно быть 1–120 символов."
        )

    description = (
        description.strip()
        if description
        else None
    )

    if description and len(description) > 1000:
        raise ValueError(
            "Описание слишком длинное."
        )

    avatar_url = valid_https_url(
        avatar_url
    )

    with database() as connection:

        cursor = connection.execute(
            """
            INSERT INTO students (
                name,
                description,
                avatar_url
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                description,
                avatar_url,
            ),
        )

        return int(cursor.lastrowid)


def update_student_description(
    student_id: int,
    description: str | None,
) -> None:

    require_admin()

    student_id = int(student_id)

    description = (
        description.strip()
        if description
        else None
    )

    if description and len(description) > 1000:
        raise ValueError(
            "Описание слишком длинное."
        )

    with database() as connection:

        cursor = connection.execute(
            """
            UPDATE students
            SET description = ?
            WHERE id = ?
            """,
            (
                description,
                student_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "Ученик не найден."
            )


def add_video(
    title: str,
    video_id: str,
) -> int:

    require_admin()

    title = title.strip()

    if not 1 <= len(title) <= 160:
        raise ValueError(
            "Название должно быть 1–160 символов."
        )

    video_id = validate_youtube_id(
        video_id
    )

    with database() as connection:

        cursor = connection.execute(
            """
            INSERT INTO videos (
                title,
                provider,
                video_id
            )
            VALUES (
                ?,
                'youtube',
                ?
            )
            """,
            (
                title,
                video_id,
            ),
        )

        return int(cursor.lastrowid)


def delete_row(
    table: str,
    row_id: int,
):
    require_admin()

    allowed_tables = {
        "news",
        "students",
        "videos",
    }

    if table not in allowed_tables:
        raise ValueError(
            "Недопустимый раздел."
        )

    row_id = int(row_id)

    with database() as connection:

        cursor = connection.execute(
            f"""
            DELETE FROM {table}
            WHERE id = ?
            """,
            (row_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "Запись не найдена."
            )


# ============================================================
# ПОИСК УЧЕНИКОВ
# ============================================================

STOP_WORDS = {
    "кто",
    "что",
    "это",
    "такой",
    "такая",
    "такое",
    "расскажи",
    "покажи",
    "найди",
    "про",
    "нужен",
    "нужна",
    "мне",
    "пожалуйста",
    "есть",
    "у",
    "в",
    "на",
    "из",
    "и",
    "или",
    "как",
    "где",
    "какой",
    "какая",
    "какие",
    "человек",
    "человека",
    "ученик",
    "ученика",
    "ученики",
    "ученице",
    "ученица",
    "одноклассник",
    "одноклассники",
    "одноклассница",
}


def student_score(
    question: str,
    student: dict[str, Any],
) -> int:

    q = normalize_text(question)

    name = normalize_text(
        student["name"]
    )

    description = normalize_text(
        student.get("description") or ""
    )

    score = 0

    if name in q:
        score += 200

    name_parts = name.split()

    for part in name_parts:
        if len(part) >= 3 and part in q:
            score += 70

    # Обратный порядок:
    # "Кирилл Тен" и "Тен Кирилл"
    if len(name_parts) >= 2:

        reversed_name = " ".join(
            reversed(name_parts)
        )

        if reversed_name in q:
            score += 180

    # Совпадения слов с описанием
    for word in q.split():

        if (
            len(word) >= 4
            and word not in STOP_WORDS
            and word in description
        ):
            score += 10

    # Небольшая защита от опечаток
    for part in name_parts:

        if len(part) >= 4:

            for word in q.split():

                if word in STOP_WORDS:
                    continue

                ratio = SequenceMatcher(
                    None,
                    part,
                    word,
                ).ratio()

                if ratio >= 0.80:
                    score += 20

    return score


def find_students(
    question: str,
) -> list[dict[str, Any]]:

    students = get_students(500)

    scored = []

    for student in students:

        score = student_score(
            question,
            student,
        )

        if score > 0:
            scored.append(
                (
                    score,
                    student,
                )
            )

    scored.sort(
        key=lambda item: (
            -item[0],
            normalize_text(
                item[1]["name"]
            ),
        )
    )

    return [
        student
        for _, student in scored[:5]
    ]


# ============================================================
# ЛОКАЛЬНЫЙ ПОМОЩНИК
# ============================================================

def ask_assistant(
    question: str,
) -> str:

    question = question.strip()

    if not question:
        return "Напиши вопрос 😊"

    if len(question) > 1000:
        return "Вопрос получился слишком длинным."

    q = normalize_text(question)

    # --------------------------------------------------------
    # ПРИВЕТСТВИЕ
    # --------------------------------------------------------

    if re.search(
        r"\b(привет|здравствуй|здрасьте|даров|хай)\b",
        q,
    ):
        return (
            "Привет! 👋 Я помощник 6МК.\n\n"
            "Могу найти ученика, рассказать о сайте "
            "или показать статистику."
        )

    # --------------------------------------------------------
    # СТАТИСТИКА
    # --------------------------------------------------------

    if (
        "сколько учеников" in q
        or "сколько нас" in q
        or re.search(
            r"\bстатист\w*",
            q,
        )
    ):
        stats = get_statistics()

        return (
            f"Сейчас в классе {stats['students']} учеников. 👥\n"
            f"Новостей: {stats['news']}. 📰\n"
            f"Видео: {stats['videos']}. 🎬"
        )

    # --------------------------------------------------------
    # НАВИГАЦИЯ
    # --------------------------------------------------------

    if re.search(
        r"\b(новост\w*|событи\w*)\b",
        q,
    ):
        return (
            "Раздел «Новости» находится на странице ниже. 📰"
        )

    if re.search(
        r"\b(видео|ролик|ютуб|youtube)\b",
        q,
    ):
        return (
            "Раздел «Видео» находится ниже. 🎬"
        )

    if re.search(
        r"\b(раздел\w*|страниц\w*|сайт)\b",
        q,
    ):
        return (
            "На сайте есть четыре основных раздела:\n"
            "📰 Новости\n"
            "👥 Ученики\n"
            "🎬 Видео\n"
            "📊 Статистика"
        )

    # --------------------------------------------------------
    # ПОИСК УЧЕНИКА
    #
    # Ищем ДО общих ответов, чтобы:
    # "Кто такой Кирилл Тен?"
    # сразу находил ученика.
    # --------------------------------------------------------

    found = find_students(question)

    if found:

        top = found[0]

        # Если есть очень сильное совпадение,
        # отвечаем про одного человека.
        if student_score(question, top) >= 100:

            description = (
                top.get("description")
                or "Описание пока не добавлено."
            )

            return (
                f"👤 {top['name']}\n"
                f"{description}"
            )

        # Если запрос неоднозначный
        lines = []

        for student in found[:5]:

            description = (
                student.get("description")
                or "Описание пока не добавлено."
            )

            lines.append(
                f"• {student['name']} — {description}"
            )

        return "\n".join(lines)

    # --------------------------------------------------------
    # ПОМОЩЬ
    # --------------------------------------------------------

    if re.search(
        r"\b(помощ\w*|умеешь|можешь)\b",
        q,
    ):
        return (
            "Попробуй спросить:\n\n"
            "• «Кто такой Кирилл Тен?»\n"
            "• «Кто любит футбол?»\n"
            "• «Сколько учеников?»\n"
            "• «Какие есть разделы?»"
        )

    # --------------------------------------------------------
    # НИЧЕГО НЕ НАШЛИ
    # --------------------------------------------------------

    return (
        "Хмм, я пока не смог это найти 🤔\n\n"
        "Попробуй написать имя или фамилию ученика, "
        "например: «Кто такой Кирилл Тен?»"
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    stats = get_statistics()

    return {
        "status": "ok",
        "assistant": "local-rule-based",
        "students": stats["students"],
        "news": stats["news"],
        "videos": stats["videos"],
        "database": str(DB_PATH),
    }


# ============================================================
# FRONTEND
# ============================================================

import sys
import frontend


frontend.register_ui(
    sys.modules[__name__]
)


# ============================================================
# NICEGUI
# ============================================================

ui.run_with(
    app,
    mount_path="/",
    storage_secret=STORAGE_SECRET,
    title="6МК — классный портал",
    dark=True,
)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        reload=False,
    )