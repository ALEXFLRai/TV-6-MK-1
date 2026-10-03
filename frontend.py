from __future__ import annotations

import re

from nicegui import app, ui


# ============================================================
# CSS
# ============================================================

CSS = r"""
:root {
    --orange: #f97316;
    --orange-light: #fb923c;
    --amber: #f59e0b;
    --cream: #fff7ed;
    --card: rgba(255,255,255,.055);
}

body {
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(249,115,22,.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(245,158,11,.12),
            transparent 28%
        ),
        #0d0f13;
}

.page {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 18px 18px 70px;
}

.header {
    position: sticky;
    top: 10px;
    z-index: 30;

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;

    padding: 12px 14px;

    border: 1px solid rgba(249,115,22,.18);
    border-radius: 22px;

    background: rgba(18,18,22,.90);
    backdrop-filter: blur(18px);

    box-shadow:
        0 12px 35px rgba(0,0,0,.20);
}

.logo {
    font-size: 28px;
    font-weight: 950;
    letter-spacing: -0.05em;
}

.logo-orange {
    color: var(--orange-light);
}

.muted {
    color: #a1a1aa;
}

.hero {
    padding: 34px;
    margin-top: 20px;
    margin-bottom: 24px;

    border: 1px solid rgba(249,115,22,.16);
    border-radius: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(249,115,22,.17),
            rgba(245,158,11,.07),
            rgba(24,24,28,.88)
        );

    box-shadow:
        0 20px 60px rgba(0,0,0,.18);
}

.hero-title {
    font-size: clamp(42px, 7vw, 76px);
    line-height: .95;
    font-weight: 950;
    letter-spacing: -0.06em;
}

.hero-subtitle {
    max-width: 720px;
    margin-top: 16px;
    color: #d4d4d8;
    font-size: 18px;
    line-height: 1.5;
}

.section {
    width: 100%;
    margin-top: 38px;
    scroll-margin-top: 100px;
}

.section-title {
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin-bottom: 16px;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fill, minmax(245px, 1fr));
    gap: 16px;
}

.card {
    width: 100%;

    border: 1px solid rgba(255,255,255,.08);
    border-radius: 22px;

    background: var(--card);

    box-shadow:
        0 12px 35px rgba(0,0,0,.12);

    transition:
        transform .15s ease,
        border-color .15s ease;
}

.card:hover {
    transform: translateY(-2px);
    border-color: rgba(249,115,22,.28);
}

.stat-number {
    font-size: 34px;
    line-height: 1;
    font-weight: 950;
    color: var(--orange-light);
}

.stat-card {
    min-width: 150px;
}

.student-avatar {
    width: 64px;
    height: 64px;

    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            rgba(249,115,22,.24),
            rgba(245,158,11,.10)
        );

    border: 1px solid rgba(249,115,22,.22);

    font-size: 24px;
    font-weight: 900;
    color: var(--orange-light);
}

.news-image {
    width: 100%;
    height: 185px;

    object-fit: cover;

    border-radius: 17px;
    margin-bottom: 12px;
}

.video-frame {
    display: block;

    width: 100%;
    aspect-ratio: 16 / 9;

    border: 0;
    border-radius: 17px;
}

.assistant-card {
    border: 1px solid rgba(249,115,22,.20);
    background:
        linear-gradient(
            135deg,
            rgba(249,115,22,.13),
            rgba(255,255,255,.035)
        );
}

.assistant-icon {
    width: 46px;
    height: 46px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 15px;

    background: rgba(249,115,22,.16);
    font-size: 24px;
}

.footer {
    margin-top: 55px;
    text-align: center;
    color: #71717a;
}

.admin-row {
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 15px;
    padding: 10px 12px;
    margin-top: 6px;
}

.orange-button {
    background: var(--orange) !important;
}

@media (max-width: 800px) {

    .header {
        position: static;
        flex-direction: column;
        align-items: stretch;
    }

    .hero {
        padding: 25px;
    }

    .hero-title {
        font-size: 54px;
    }

    .header-nav {
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
    }
}
"""


# ============================================================
# UI
# ============================================================

def register_ui(backend):

    @ui.page("/")
    def index_page():

        ui.add_css(CSS)

        # =====================================================
        # ДИАЛОГ ВХОДА
        # =====================================================

        login_dialog = ui.dialog()

        with login_dialog:

            with ui.card().classes(
                "w-full max-w-md"
            ):

                ui.label(
                    "🔐 Вход администратора"
                ).classes(
                    "text-2xl font-black"
                )

                password_input = ui.input(
                    label="Пароль",
                    password=True,
                    password_toggle_button=True,
                ).classes(
                    "w-full mt-4"
                )

                def do_login():

                    password = (
                        password_input.value
                        or ""
                    )

                    if backend.authenticate_admin(
                        password
                    ):

                        app.storage.user[
                            "is_admin"
                        ] = True

                        ui.notify(
                            "Добро пожаловать, администратор! 🛠️",
                            type="positive",
                        )

                        ui.run_javascript(
                            "window.location.reload();"
                        )

                    else:

                        ui.notify(
                            "Неверный пароль.",
                            type="negative",
                        )

                with ui.row().classes(
                    "justify-end gap-2 mt-4"
                ):

                    ui.button(
                        "Отмена",
                        on_click=login_dialog.close,
                    ).props(
                        "flat"
                    )

                    ui.button(
                        "Войти",
                        on_click=do_login,
                    ).classes(
                        "orange-button"
                    )

        # =====================================================
        # ПОМОЩНИК
        # =====================================================

        assistant_dialog = ui.dialog()

        with assistant_dialog:

            with ui.card().classes(
                "w-full max-w-2xl assistant-card"
            ):

                with ui.row().classes(
                    "items-center gap-3"
                ):

                    ui.label(
                        "✨"
                    ).classes(
                        "text-3xl"
                    )

                    with ui.column().classes(
                        "gap-0"
                    ):

                        ui.label(
                            "Помощник 6МК"
                        ).classes(
                            "text-2xl font-black"
                        )

                        ui.label(
                            "Простой локальный помощник"
                        ).classes(
                            "text-sm text-gray-400"
                        )

                ui.label(
                    "Можно спросить про ученика, "
                    "статистику или разделы сайта."
                ).classes(
                    "mt-4 text-gray-300"
                )

                assistant_input = ui.input(
                    label="Что хочешь узнать?",
                    placeholder="Например: Кто такой Кирилл Тен?",
                ).classes(
                    "w-full mt-4"
                )

                assistant_output = ui.label(
                    "Здесь появится ответ 😊"
                ).classes(
                    "w-full whitespace-pre-line mt-4"
                )

                def ask_assistant():

                    try:

                        question = (
                            assistant_input.value
                            or ""
                        )

                        answer = backend.ask_assistant(
                            question
                        )

                        assistant_output.set_text(
                            answer
                        )

                    except Exception as exc:

                        assistant_output.set_text(
                            "Произошла ошибка."
                        )

                        ui.notify(
                            str(exc),
                            type="negative",
                        )

                with ui.row().classes(
                    "gap-2 mt-4 flex-wrap"
                ):

                    quick_questions = [
                        "Кто такой Кирилл Тен?",
                        "Сколько учеников?",
                        "Какие есть разделы?",
                    ]

                    for text in quick_questions:

                        def use_question(
                            value=text
                        ):
                            assistant_input.value = value
                            ask_assistant()

                        ui.button(
                            text,
                            on_click=use_question,
                        ).props(
                            "outline"
                        )

                with ui.row().classes(
                    "justify-end gap-2 mt-5"
                ):

                    ui.button(
                        "Закрыть",
                        on_click=assistant_dialog.close,
                    ).props(
                        "flat"
                    )

                    ui.button(
                        "✨ Спросить",
                        on_click=ask_assistant,
                    ).classes(
                        "orange-button"
                    )

        # =====================================================
        # HEADER
        # =====================================================

        with ui.column().classes(
            "page"
        ):

            with ui.row().classes(
                "header w-full"
            ):

                with ui.row().classes(
                    "items-center gap-3"
                ):

                    ui.label(
                        "6"
                    ).classes(
                        "logo logo-orange"
                    )

                    ui.label(
                        "МК"
                    ).classes(
                        "logo"
                    )

                    ui.label(
                        "классный портал"
                    ).classes(
                        "muted"
                    )

                with ui.row().classes(
                    "header-nav items-center justify-center gap-1"
                ):

                    def scroll_to(
                        section_id: str,
                    ):
                        ui.run_javascript(
                            f"""
                            document
                                .getElementById(
                                    '{section_id}'
                                )
                                ?.scrollIntoView(
                                    {{
                                        behavior: 'smooth'
                                    }}
                                );
                            """
                        )

                    ui.button(
                        "📰 Новости",
                        on_click=lambda: scroll_to(
                            "news"
                        ),
                    ).props(
                        "flat"
                    )

                    ui.button(
                        "👥 Ученики",
                        on_click=lambda: scroll_to(
                            "students"
                        ),
                    ).props(
                        "flat"
                    )

                    ui.button(
                        "🎬 Видео",
                        on_click=lambda: scroll_to(
                            "videos"
                        ),
                    ).props(
                        "flat"
                    )

                    ui.button(
                        "📊 Статистика",
                        on_click=lambda: scroll_to(
                            "stats"
                        ),
                    ).props(
                        "flat"
                    )

                    ui.button(
                        "✨ Помощник",
                        on_click=assistant_dialog.open,
                    ).classes(
                        "orange-button"
                    )

                    if backend.is_admin():

                        def logout():

                            app.storage.user[
                                "is_admin"
                            ] = False

                            ui.run_javascript(
                                "window.location.reload();"
                            )

                        ui.button(
                            "Выйти",
                            on_click=logout,
                        ).props(
                            "outline"
                        )

                    else:

                        ui.button(
                            "🔐 Админ",
                            on_click=login_dialog.open,
                        ).props(
                            "outline"
                        )

            # =================================================
            # HERO
            # =================================================

            stats = backend.get_statistics()

            with ui.element("section").classes(
                "hero w-full"
            ):

                ui.label(
                    "Добро пожаловать! 👋"
                ).classes(
                    "text-sm text-orange-300 font-bold"
                )

                ui.label(
                    "6МК"
                ).classes(
                    "hero-title mt-3"
                )

                ui.label(
                    "Наш маленький уголок в интернете — "
                    "новости, ученики, видео и всё самое важное."
                ).classes(
                    "hero-subtitle"
                )

                with ui.row().classes(
                    "gap-3 mt-7 flex-wrap"
                ):

                    with ui.card().classes(
                        "card stat-card p-5"
                    ):
                        ui.label(
                            str(stats["students"])
                        ).classes(
                            "stat-number"
                        )

                        ui.label(
                            "👥 учеников"
                        ).classes(
                            "font-bold mt-2"
                        )

                    with ui.card().classes(
                        "card stat-card p-5"
                    ):
                        ui.label(
                            str(stats["news"])
                        ).classes(
                            "stat-number"
                        )

                        ui.label(
                            "📰 новостей"
                        ).classes(
                            "font-bold mt-2"
                        )

                    with ui.card().classes(
                        "card stat-card p-5"
                    ):
                        ui.label(
                            str(stats["videos"])
                        ).classes(
                            "stat-number"
                        )

                        ui.label(
                            "🎬 видео"
                        ).classes(
                            "font-bold mt-2"
                        )

            # =================================================
            # NEWS
            # =================================================

            with ui.element("section").classes(
                "section"
            ).props(
                "id=news"
            ):

                ui.label(
                    "📰 Новости"
                ).classes(
                    "section-title"
                )

                news_box = ui.row().classes(
                    "grid w-full"
                )

                news = backend.get_news(24)

                if not news:

                    with news_box:

                        with ui.card().classes(
                            "card p-5"
                        ):

                            ui.label(
                                "Пока новостей нет 🙂"
                            ).classes(
                                "muted"
                            )

                else:

                    for item in news:

                        with news_box:

                            with ui.card().classes(
                                "card p-4"
                            ):

                                image_url = item.get(
                                    "image_url"
                                )

                                if image_url:
                                    ui.image(
                                        image_url
                                    ).classes(
                                        "news-image"
                                    )

                                ui.label(
                                    item["title"]
                                ).classes(
                                    "text-xl font-black"
                                )

                                ui.label(
                                    item["body"]
                                ).classes(
                                    "mt-2 whitespace-pre-line text-gray-300"
                                )

                                ui.label(
                                    item["created_at"]
                                ).classes(
                                    "text-xs text-gray-500 mt-4"
                                )

            # =================================================
            # STUDENTS
            # =================================================

            with ui.element("section").classes(
                "section"
            ).props(
                "id=students"
            ):

                ui.label(
                    "👥 Наш класс"
                ).classes(
                    "section-title"
                )

                with ui.row().classes(
                    "w-full items-center gap-2 mb-5"
                ):

                    student_search = ui.input(
                        label="Поиск ученика",
                        placeholder="Например: Кирилл Тен",
                    ).classes(
                        "flex-1"
                    )

                    search_button = ui.button(
                        "🔎 Найти",
                    ).classes(
                        "orange-button"
                    )

                students_box = ui.row().classes(
                    "grid w-full"
                )

                def render_students(
                    query: str = "",
                ):

                    students_box.clear()

                    query = query.strip().lower()

                    students = backend.get_students(
                        500
                    )

                    if query:

                        students = [
                            student
                            for student in students
                            if (
                                query
                                in student["name"].lower()
                            )
                            or (
                                query
                                in (
                                    student.get(
                                        "description"
                                    )
                                    or ""
                                ).lower()
                            )
                        ]

                    if not students:

                        with students_box:

                            with ui.card().classes(
                                "card p-5"
                            ):

                                ui.label(
                                    "Ничего не найдено 😔"
                                ).classes(
                                    "font-bold"
                                )

                                ui.label(
                                    "Попробуй написать только имя "
                                    "или фамилию."
                                ).classes(
                                    "muted mt-1"
                                )

                        return

                    for student in students:

                        with students_box:

                            with ui.card().classes(
                                "card p-5"
                            ):

                                with ui.row().classes(
                                    "items-center gap-4"
                                ):

                                    avatar_url = (
                                        student.get(
                                            "avatar_url"
                                        )
                                    )

                                    if avatar_url:

                                        ui.image(
                                            avatar_url
                                        ).classes(
                                            "student-avatar"
                                        )

                                    else:

                                        ui.label(
                                            student["name"][0]
                                        ).classes(
                                            "student-avatar"
                                        )

                                    with ui.column().classes(
                                        "gap-1"
                                    ):

                                        ui.label(
                                            student["name"]
                                        ).classes(
                                            "text-lg font-black"
                                        )

                                        ui.label(
                                            student.get(
                                                "description"
                                            )
                                            or "Описание пока не добавлено."
                                        ).classes(
                                            "text-gray-400"
                                        )

                def perform_student_search():

                    render_students(
                        student_search.value or ""
                    )

                search_button.on(
                    "click",
                    perform_student_search,
                )

                # Показываем всех сразу
                render_students()

            # =================================================
            # VIDEOS
            # =================================================

            with ui.element("section").classes(
                "section"
            ).props(
                "id=videos"
            ):

                ui.label(
                    "🎬 Видео"
                ).classes(
                    "section-title"
                )

                videos_box = ui.row().classes(
                    "grid w-full"
                )

                videos = backend.get_videos(50)

                if not videos:

                    with videos_box:

                        with ui.card().classes(
                            "card p-5"
                        ):

                            ui.label(
                                "Видео пока нет 🙂"
                            ).classes(
                                "muted"
                            )

                else:

                    for video in videos:

                        video_id = video.get(
                            "video_id",
                            "",
                        )

                        if not re.fullmatch(
                            r"[A-Za-z0-9_-]{6,32}",
                            video_id,
                        ):
                            continue

                        with videos_box:

                            with ui.card().classes(
                                "card p-4"
                            ):

                                ui.label(
                                    video["title"]
                                ).classes(
                                    "text-xl font-black mb-3"
                                )

                                ui.html(
                                    f"""
                                    <iframe
                                        class="video-frame"
                                        src="https://www.youtube-nocookie.com/embed/{video_id}"
                                        title="YouTube video"
                                        loading="lazy"
                                        referrerpolicy="strict-origin-when-cross-origin"
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                                        allowfullscreen
                                    ></iframe>
                                    """
                                ).classes(
                                    "w-full"
                                )

            # =================================================
            # STATS
            # =================================================

            with ui.element("section").classes(
                "section"
            ).props(
                "id=stats"
            ):

                ui.label(
                    "📊 Статистика"
                ).classes(
                    "section-title"
                )

                current_stats = (
                    backend.get_statistics()
                )

                with ui.row().classes(
                    "grid w-full"
                ):

                    with ui.card().classes(
                        "card p-5"
                    ):

                        ui.label(
                            str(
                                current_stats[
                                    "students"
                                ]
                            )
                        ).classes(
                            "stat-number"
                        )

                        ui.label(
                            "👥 учеников"
                        ).classes(
                            "font-bold mt-2"
                        )

                    with ui.card().classes(
                        "card p-5"
                    ):

                        ui.label(
                            str(
                                current_stats[
                                    "news"
                                ]
                            )
                        ).classes(
                            "stat-number"
                        )

                        ui.label(
                            "📰 новостей"
                        ).classes(
                            "font-bold mt-2"
                        )

                    with ui.card().classes(
                        "card p-5"
                    ):

                        ui.label(
                            str(
                                current_stats[
                                    "videos"
                                ]
                            )
                        ).classes(
                            "stat-number"
                        )

                        ui.label(
                            "🎬 видео"
                        ).classes(
                            "font-bold mt-2"
                        )

            # =================================================
            # ADMIN PANEL
            # =================================================

            if backend.is_admin():

                # ---------------------------------------------
                # EDIT STUDENT DIALOG
                # ---------------------------------------------

                edit_student_dialog = ui.dialog()

                edit_student_id = {
                    "value": None
                }

                with edit_student_dialog:

                    with ui.card().classes(
                        "w-full max-w-lg"
                    ):

                        edit_student_name = ui.label(
                            "Редактирование"
                        ).classes(
                            "text-2xl font-black"
                        )

                        edit_student_description = ui.textarea(
                            label="Описание ученика"
                        ).classes(
                            "w-full mt-4"
                        )

                        def open_edit_student(
                            student: dict
                        ):

                            edit_student_id[
                                "value"
                            ] = student["id"]

                            edit_student_name.set_text(
                                f"✏️ {student['name']}"
                            )

                            edit_student_description.value = (
                                student.get(
                                    "description"
                                )
                                or ""
                            )

                            edit_student_dialog.open()

                        def save_student_description():

                            student_id = (
                                edit_student_id[
                                    "value"
                                ]
                            )

                            if student_id is None:
                                return

                            try:

                                backend.update_student_description(
                                    student_id,
                                    edit_student_description.value
                                    or "",
                                )

                                ui.notify(
                                    "Описание сохранено! ✅",
                                    type="positive",
                                )

                                edit_student_dialog.close()

                                ui.run_javascript(
                                    "window.location.reload();"
                                )

                            except Exception as exc:

                                ui.notify(
                                    str(exc),
                                    type="negative",
                                )

                        with ui.row().classes(
                            "justify-end gap-2 mt-4"
                        ):

                            ui.button(
                                "Отмена",
                                on_click=edit_student_dialog.close,
                            ).props(
                                "flat"
                            )

                            ui.button(
                                "💾 Сохранить",
                                on_click=save_student_description,
                            ).classes(
                                "orange-button"
                            )

                # ---------------------------------------------
                # PANEL
                # ---------------------------------------------

                with ui.expansion(
                    "🛠️ Панель администратора"
                ).classes(
                    "section w-full"
                ):

                    # NEWS

                    ui.label(
                        "📰 Добавить новость"
                    ).classes(
                        "text-xl font-black mt-2"
                    )

                    news_title = ui.input(
                        label="Заголовок"
                    ).classes(
                        "w-full"
                    )

                    news_body = ui.textarea(
                        label="Текст"
                    ).classes(
                        "w-full"
                    )

                    news_image = ui.input(
                        label="HTTPS-ссылка на изображение"
                    ).classes(
                        "w-full"
                    )

                    def create_news():

                        try:

                            backend.add_news(
                                news_title.value or "",
                                news_body.value or "",
                                news_image.value or None,
                            )

                            ui.notify(
                                "Новость добавлена! 🎉",
                                type="positive",
                            )

                            ui.run_javascript(
                                "window.location.reload();"
                            )

                        except Exception as exc:

                            ui.notify(
                                str(exc),
                                type="negative",
                            )

                    ui.button(
                        "➕ Добавить новость",
                        on_click=create_news,
                    ).classes(
                        "orange-button mb-6"
                    )

                    # STUDENT

                    ui.separator()

                    ui.label(
                        "👤 Добавить ученика"
                    ).classes(
                        "text-xl font-black mt-5"
                    )

                    admin_student_name = ui.input(
                        label="Имя"
                    ).classes(
                        "w-full"
                    )

                    admin_student_description = ui.input(
                        label="Описание"
                    ).classes(
                        "w-full"
                    )

                    admin_student_avatar = ui.input(
                        label="HTTPS-ссылка на аватар"
                    ).classes(
                        "w-full"
                    )

                    def create_student():

                        try:

                            backend.add_student(
                                admin_student_name.value
                                or "",
                                admin_student_description.value
                                or None,
                                admin_student_avatar.value
                                or None,
                            )

                            ui.notify(
                                "Ученик добавлен! 🎉",
                                type="positive",
                            )

                            ui.run_javascript(
                                "window.location.reload();"
                            )

                        except Exception as exc:

                            ui.notify(
                                str(exc),
                                type="negative",
                            )

                    ui.button(
                        "➕ Добавить ученика",
                        on_click=create_student,
                    ).classes(
                        "orange-button mb-6"
                    )

                    # EDIT STUDENTS

                    ui.separator()

                    ui.label(
                        "✏️ Изменить описания учеников"
                    ).classes(
                        "text-xl font-black mt-5"
                    )

                    student_rows = backend.get_students(
                        500
                    )

                    for item in student_rows:

                        with ui.row().classes(
                            "admin-row w-full items-center"
                        ):

                            ui.label(
                                item["name"]
                            ).classes(
                                "flex-1 font-bold"
                            )

                            ui.button(
                                "✏️ Изменить",
                                on_click=lambda row=item:
                                    open_edit_student(row),
                            ).props(
                                "outline"
                            )

                    # VIDEO

                    ui.separator()

                    ui.label(
                        "🎬 Добавить YouTube-видео"
                    ).classes(
                        "text-xl font-black mt-6"
                    )

                    admin_video_title = ui.input(
                        label="Название"
                    ).classes(
                        "w-full"
                    )

                    admin_video_id = ui.input(
                        label="YouTube ID"
                    ).classes(
                        "w-full"
                    )

                    ui.label(
                        "Например: dQw4w9WgXcQ"
                    ).classes(
                        "text-sm text-gray-500"
                    )

                    def create_video():

                        try:

                            backend.add_video(
                                admin_video_title.value
                                or "",
                                admin_video_id.value
                                or "",
                            )

                            ui.notify(
                                "Видео добавлено! 🎬",
                                type="positive",
                            )

                            ui.run_javascript(
                                "window.location.reload();"
                            )

                        except Exception as exc:

                            ui.notify(
                                str(exc),
                                type="negative",
                            )

                    ui.button(
                        "➕ Добавить видео",
                        on_click=create_video,
                    ).classes(
                        "orange-button mb-6"
                    )

                    # DELETE

                    ui.separator()

                    ui.label(
                        "🗑️ Удаление"
                    ).classes(
                        "text-xl font-black mt-5"
                    )

                    ui.label(
                        "Новости"
                    ).classes(
                        "font-bold mt-3"
                    )

                    for item in backend.get_news(100):

                        with ui.row().classes(
                            "admin-row w-full items-center"
                        ):

                            ui.label(
                                f"#{item['id']} — "
                                f"{item['title']}"
                            ).classes(
                                "flex-1"
                            )

                            def remove_news(
                                row_id=item["id"]
                            ):

                                try:

                                    backend.delete_row(
                                        "news",
                                        row_id,
                                    )

                                    ui.notify(
                                        "Новость удалена.",
                                        type="positive",
                                    )

                                    ui.run_javascript(
                                        "window.location.reload();"
                                    )

                                except Exception as exc:

                                    ui.notify(
                                        str(exc),
                                        type="negative",
                                    )

                            ui.button(
                                "Удалить",
                                on_click=remove_news,
                            ).props(
                                "flat color=negative"
                            )

                    ui.label(
                        "Ученики"
                    ).classes(
                        "font-bold mt-6"
                    )

                    for item in backend.get_students(500):

                        with ui.row().classes(
                            "admin-row w-full items-center"
                        ):

                            ui.label(
                                f"#{item['id']} — "
                                f"{item['name']}"
                            ).classes(
                                "flex-1"
                            )

                            def remove_student(
                                row_id=item["id"]
                            ):

                                try:

                                    backend.delete_row(
                                        "students",
                                        row_id,
                                    )

                                    ui.notify(
                                        "Ученик удалён.",
                                        type="positive",
                                    )

                                    ui.run_javascript(
                                        "window.location.reload();"
                                    )

                                except Exception as exc:

                                    ui.notify(
                                        str(exc),
                                        type="negative",
                                    )

                            ui.button(
                                "Удалить",
                                on_click=remove_student,
                            ).props(
                                "flat color=negative"
                            )

                    ui.label(
                        "Видео"
                    ).classes(
                        "font-bold mt-6"
                    )

                    for item in backend.get_videos(100):

                        with ui.row().classes(
                            "admin-row w-full items-center"
                        ):

                            ui.label(
                                f"#{item['id']} — "
                                f"{item['title']}"
                            ).classes(
                                "flex-1"
                            )

                            def remove_video(
                                row_id=item["id"]
                            ):

                                try:

                                    backend.delete_row(
                                        "videos",
                                        row_id,
                                    )

                                    ui.notify(
                                        "Видео удалено.",
                                        type="positive",
                                    )

                                    ui.run_javascript(
                                        "window.location.reload();"
                                    )

                                except Exception as exc:

                                    ui.notify(
                                        str(exc),
                                        type="negative",
                                    )

                            ui.button(
                                "Удалить",
                                on_click=remove_video,
                            ).props(
                                "flat color=negative"
                            )

            # =================================================
            # FOOTER
            # =================================================

            with ui.element("div").classes(
                "footer"
            ):

                ui.label(
                    "🧡 6МК · сделано для нашего класса"
                )