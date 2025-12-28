import streamlit as st
import sys
from pathlib import Path
import pdfplumber

# Добавляем путь к корню проекта для импортов
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.summarizer import MultilingualSummarizer

    IMPORT_SUCCESS = True
except Exception as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)

# Настройки страницы
st.set_page_config(
    page_title="📚 Multilingual Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили CSS для улучшения внешнего вида
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
    }
    .stDownloadButton>button {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
    }
    .summary-box {
        background-color: #ffffff;
        color: #333333;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-top: 20px;
        border: 1px solid #e0e0e0;
    }
    .stats-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        color: #1a365d;
    }
    .error-box {
        background-color: #ffebee;
        color: #c62828;
        border-left: 4px solid #f44336;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    .info-box {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff8e1;
        color: #ff8f00;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Проверка импортов
if not IMPORT_SUCCESS:
    st.markdown(f"""
    <div class="error-box">
        ❌ <b>Критическая ошибка при запуске приложения:</b><br>
        Не удалось загрузить модули из папки src:<br>
        <pre>{IMPORT_ERROR}</pre><br>
        <b>Рекомендуемые действия:</b>
        <ul>
            <li>Проверьте структуру проекта (должна быть папка src с файлами)</li>
            <li>Убедитесь, что вы запускаете приложение из корневой директории проекта</li>
            <li>Проверьте наличие всех зависимостей в requirements.txt</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Заголовок приложения
st.title("📚 Multilingual Document Summarizer")
st.markdown("### Автоматическое создание кратких содержаний для текстов и PDF на 3 языках")

# Боковая панель с настройками
with st.sidebar:
    st.header("⚙️ Настройки суммаризации")

    # Выбор языка (только 3 языка)
    language_options = {
        "Английский (English)": "en",
        "Русский (Russian)": "ru",
        "Немецкий (German)": "de"
    }
    selected_language = st.selectbox(
        "🌍 Язык документа",
        list(language_options.keys()),
        index=1  # По умолчанию русский
    )
    lang_code = language_options[selected_language]

    # Уровень сжатия
    compression_level = st.slider(
        "📊 Уровень сжатия (%)",
        min_value=10,
        max_value=70,
        value=40,
        step=5,
        format="%d%%"
    )
    compression_ratio = compression_level / 100

    # Дополнительные настройки
    st.divider()
    st.subheader("ℹ️ Информация")
    st.info("""
    **Поддерживаемые форматы:**
    - Текстовые файлы (.txt)
    - PDF документы (.pdf)

    **Языки:**
    - Английский
    - Русский
    - Немецкий

    **Важно:**
    - Теперь поддерживаются тексты любой длины
    - Длинные тексты разделяются на части по 2000 символов
    - Для немецкого языка используется специализированная модель
    """)

# Инициализация переменных состояния
if 'file_content' not in st.session_state:
    st.session_state.file_content = ""
if 'manual_text' not in st.session_state:
    st.session_state.manual_text = ""

# Основная область приложения
tab1, tab2 = st.tabs(["📤 Загрузить документ", "✍️ Вставить текст"])

with tab1:
    st.header("📄 Загрузите ваш документ")
    uploaded_file = st.file_uploader(
        "Выберите файл (TXT или PDF)",
        type=["txt", "pdf"],
        accept_multiple_files=False,
        help="Поддерживаются файлы любого размера"
    )

    if uploaded_file:
        st.success(f"Файл загружен: {uploaded_file.name}")

        # Чтение файла
        file_content = ""
        file_size = uploaded_file.size / 1024  # в КБ

        try:
            if uploaded_file.type == "application/pdf":
                with st.spinner("Чтение PDF файла..."):
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                file_content += text + "\n"
            else:  # TXT файл
                file_content = uploaded_file.read().decode("utf-8")

            if file_content:
                # Сохраняем в состоянии
                st.session_state.file_content = file_content

                # Показываем только начало текста для длинных документов
                preview_text = file_content[:1000] + "..." if len(file_content) > 1000 else file_content
                st.text_area("Предпросмотр содержимого файла", preview_text, height=300)
                st.info(f"Размер файла: {file_size:.1f} КБ | Общее количество символов: {len(file_content)}")
            else:
                st.warning("Не удалось извлечь текст из файла")
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                ❌ <b>Ошибка при обработке файла:</b><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.header("✏️ Введите текст вручную")
    manual_text = st.text_area(
        "Введите или вставьте ваш текст здесь",
        height=400,
        placeholder="Вставьте ваш текст для суммаризации...",
        value=st.session_state.manual_text
    )
    # Сохраняем в состоянии
    st.session_state.manual_text = manual_text

    if manual_text.strip():
        st.session_state.file_content = manual_text

# Определяем текст для обработки
text_to_process = st.session_state.file_content.strip()

# Обработка текста только если он есть
if text_to_process:
    # Кнопка для запуска суммаризации
    if st.button("🚀 Сгенерировать краткое содержание", type="primary", use_container_width=True):
        with st.spinner("🧠 Обработка текста и генерация краткого содержания..."):
            try:
                # Создаем суммаризатор для выбранного языка
                summarizer = MultilingualSummarizer(lang_code)

                # Выбираем метод в зависимости от длины текста
                if lang_code == "de":
                    # Для немецкого языка используем специальную обработку
                    if len(text_to_process) > 2000:
                        st.info(
                            f"🔄 Обрабатываю длинный немецкий текст ({len(text_to_process)} символов). "
                            f"Текст разделен на части по 2000 символов.")
                        summary = summarizer.summarize_long_text(text_to_process, compression_ratio)
                    else:
                        summary = summarizer.summarize(text_to_process, compression_ratio)
                else:
                    # Для других языков
                    if len(text_to_process) > 2000:
                        st.info(
                            f"🔄 Обрабатываю длинный текст ({len(text_to_process)} символов). "
                            f"Текст разделен на части по 2000 символов.")
                        summary = summarizer.summarize_long_text(text_to_process, compression_ratio)
                    else:
                        summary = summarizer.summarize(text_to_process, compression_ratio)

                # Статистика
                original_words = len(text_to_process.split())
                summary_words = len(summary.split())
                actual_compression = (summary_words / original_words) * 100 if original_words > 0 else 0

                # Показываем результат
                st.success("✅ Краткое содержание успешно сгенерировано!")

                # Отображение результата
                st.markdown("### 📝 Результат суммаризации")
                with st.container():
                    st.markdown(f"""
                    <div class="summary-box">
                        <h4>Краткое содержание ({lang_code.upper()}, {compression_level}% сжатия)</h4>
                        <p style="font-size: 18px; line-height: 1.6; color: #333333;">{summary}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Статистика
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Исходный текст", f"{original_words} слов")
                with col2:
                    st.metric("Краткое содержание", f"{summary_words} слов")
                with col3:
                    st.metric("Фактическое сжатие", f"{actual_compression:.1f}%")

                # Кнопка для скачивания
                st.download_button(
                    label="📥 Скачать результат как TXT",
                    data=summary,
                    file_name=f"summary_{lang_code}_{compression_level}pct.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                    ❌ <b>Ошибка при генерации краткого содержания:</b><br>
                    {str(e)}
                </div>
                """, unsafe_allow_html=True)
                st.exception(e)
else:
    st.markdown("""
    <div class="info-box">
        ℹ️ <b>Инструкция:</b><br>
        1. Перейдите на вкладку "Загрузить документ" и выберите файл, ИЛИ<br>
        2. Перейдите на вкладку "Вставить текст" и введите текст вручную<br>
        3. Настройте параметры в боковой панели<br>
        4. Нажмите кнопку "Сгенерировать краткое содержание"
    </div>
    """, unsafe_allow_html=True)

# Примеры использования
st.divider()
st.header("💡 Примеры использования")
st.markdown("""
- **Студенты** могут быстро получать краткое содержание лекций и учебных материалов
- **Исследователи** могут обрабатывать научные статьи на разных языках
- **Бизнес-аналитики** могут быстро анализировать отчеты и документы
- **Переводчики** могут получать основные идеи текста перед началом перевода
""")

# Футер
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Создано с ❤️ для образовательных целей | Multilingual Learning Material Summarizer</p>
    <p>Версия 2.3 | Поддержка: EN, RU, DE | Обработка текстов любой длины</p>
</div>
""", unsafe_allow_html=True)
