import sys
import argparse
from pathlib import Path
import os
from summarizer import MultilingualSummarizer
# Добавляем путь к src для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    parser = argparse.ArgumentParser(description="Multilingual Learning Material Summarizer")
    parser.add_argument("--file", required=True, help="Путь к текстовому файлу")
    parser.add_argument("--lang", required=True, choices=["en", "de", "ru"],
                        help="Язык текста (en=английский, de=немецкий, ru=русский)")
    parser.add_argument("--compression", type=float, default=0.3, help="Уровень сжатия (0.1-0.7)")
    args = parser.parse_args()

    # Проверяем существование файла
    if not os.path.exists(args.file):
        print(f"❌ Ошибка: файл {args.file} не найден")
        return

    # Читаем текст из файла
    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("❌ Ошибка: файл пустой")
        return

    print(f"🔍 Обработка текста ({len(text)} символов)")
    print(f"📊 Длина исходного текста: {len(text.split())} слов")
    print(f"🌍 Язык: {args.lang}")
    print(f"📈 Уровень сжатия: {int(args.compression * 100)}%")

    try:
        # Создаем суммаризатор
        summarizer = MultilingualSummarizer(args.lang)

        # Генерируем краткое содержание
        if args.lang == "ru" and len(text) > 4000:
            summary = summarizer.summarize_long_text(text, args.compression)
        else:
            summary = summarizer.summarize(text, args.compression)

        # Выводим результат
        print("\n" + "=" * 60)
        print(f"✅ КРАТКОЕ СОДЕРЖАНИЕ ({args.lang.upper()}, {int(args.compression * 100)}% СЖАТИЯ)")
        print("=" * 60)
        print(summary)

        # Статистика
        summary_words = len(summary.split())
        actual_compression = (summary_words / len(text.split())) * 100 if len(text.split()) > 0 else 0

        print(f"\n📊 Длина резюме: {summary_words} слов")
        print(f"🎯 Эффективное сжатие: {actual_compression:.1f}%")

    except Exception as e:
        print(f"\n❌ Ошибка при обработке: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
