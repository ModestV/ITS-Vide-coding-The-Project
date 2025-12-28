from src.summarizer import MultilingualSummarizer


def test_english_summarization():
    """Тест суммаризации английского текста"""
    summarizer = MultilingualSummarizer("en")
    text = """
    This is a longer test text that should be properly summarized. It contains multiple sentences and paragraphs to
    ensure the summarization functionality works correctly. The text discusses various topics including science,
    history, and technology. Machine learning has become an important field in artificial intelligence, enabling
    computers to learn from data without being explicitly programmed. Natural language processing allows machines
    to understand human language, making applications like translation and sentiment analysis possible. This text
    is designed to be long enough to test the summarization capabilities effectively.
    """
    summary = summarizer.summarize(text, 0.5)

    # Проверяем, что суммаризация работает
    assert isinstance(summary, str)
    assert len(summary) > 0

    # Проверяем, что текст уменьшился
    assert len(summary) < len(text)
    assert len(summary.split()) < len(text.split())


def test_russian_summarization():
    """Тест суммаризации русского текста"""
    summarizer = MultilingualSummarizer("ru")
    text = ("Это тестовый текст, который должен быть корректно суммаризирован. Он содержит несколько предложений "
            "для проверки функциональности. Текст достаточно длинный, чтобы проверить работу алгоритма суммаризации"
            " на русском языке.")
    summary = summarizer.summarize(text, 0.5)

    # Проверяем, что суммаризация работает
    assert isinstance(summary, str)
    assert len(summary) > 0

    # Проверяем, что текст уменьшился
    assert len(summary) < len(text)
    assert len(summary.split()) < len(text.split())


def test_german_summarization():
    """Тест суммаризации немецкого текста"""
    summarizer = MultilingualSummarizer("de")
    text = """
    Maschinelles Lernen ist ein wichtiger Bereich der künstlichen Intelligenz. Es ermöglicht Computern, aus
    Daten zu lernen, ohne explizit programmiert zu werden. Moderne Anwendungen umfassen Sprachübersetzung,
    Bilderkennung und medizinische Diagnose. Die Technologie entwickelt sich schnell und hat großen Einfluss auf
    viele Industrien.
    """
    summary = summarizer.summarize(text, 0.5)

    # Проверяем, что суммаризация работает
    assert isinstance(summary, str)
    assert len(summary) > 0

    # Проверяем, что текст уменьшился
    assert len(summary) < len(text)
    assert len(summary.split()) < len(text.split())

    # Проверяем, что результат не содержит артефактов
    assert "<extra_id_" not in summary


def test_long_text_summarization():
    """Тест обработки длинного текста"""
    summarizer = MultilingualSummarizer("en")
    long_text = "Test sentence. " * 500  # Очень длинный текст
    summary = summarizer.summarize_long_text(long_text, 0.3)

    # Проверяем, что суммаризация работает
    assert isinstance(summary, str)
    assert len(summary) > 0

    # Проверяем, что текст уменьшился
    assert len(summary) < len(long_text)
    assert len(summary.split()) < len(long_text.split())
