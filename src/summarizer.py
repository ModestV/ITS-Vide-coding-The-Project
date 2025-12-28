from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
import nltk

# Загружаем необходимые данные NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Глобальное кэширование моделей для каждого языка
_language_models = {}


class MultilingualSummarizer:
    def __init__(self, language: str):
        """
        Инициализирует суммаризатор для конкретного языка

        Args:
            language (str): Язык суммаризации (en, de, ru)
        """
        if language not in {"en", "de", "ru"}:
            raise ValueError("Поддерживаемые языки: en (английский), de (немецкий), ru (русский)")

        self.language = language

        # Загружаем модель для выбранного языка, если ещё не загружена
        if language not in _language_models:
            self._load_model()

        self.summarizer, self.tokenizer, self.device = _language_models[language]
        print(f"✅ Суммаризатор для {language} готов к работе")

    def _load_model(self):
        """Загружает модель и токенизатор для конкретного языка"""
        # Выбираем модель в зависимости от языка
        if self.language == "en":
            model_name = "facebook/bart-large-cnn"
        elif self.language == "de":
            model_name = "google/mt5-base"
        else:  # ru
            model_name = "IlyaGusev/rut5_base_sum_gazeta"

        print(f"📦 Загружаем модель {model_name} для языка {self.language}")

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            device=0 if device == "cuda" else -1,
            framework="pt"
        )

        # Сохраняем загруженную модель
        _language_models[self.language] = (summarizer, tokenizer, device)

        print(f"✅ Модель {model_name} загружена на {device}")

    def summarize(
            self,
            text: str,
            compression_level: float = 0.3
    ) -> str:
        """
        Генерирует краткое содержание для текста на выбранном языке

        Args:
            text (str): Текст для суммаризации
            compression_level (float): Уровень сжатия (0.1-0.7)

        Returns:
            str: Краткое содержание
        """
        # Для русского языка используем специальный префикс
        if self.language == "ru":
            text = "заголовок\n" + text
        # Для немецкого языка используем специальный префикс
        elif self.language == "de":
            text = "zusammenfassen: " + text

        # Рассчитываем параметры
        max_length, min_length = self._calculate_summary_length(text, compression_level)

        try:
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True,
                clean_up_tokenization_spaces=True,
                early_stopping=True
            )
            result = summary[0]["summary_text"].strip()

            # Пост-обработка в зависимости от языка
            result = self._post_process(result)

            return result
        except Exception as e:
            print(f"⚠️ Ошибка при суммаризации: {e}")
            # Возвращаем сокращённый исходный текст как резервный вариант
            words = text.split()
            target_words = max(10, int(len(words) * compression_level))
            return " ".join(words[:target_words]) + "..."

    def summarize_long_text(self, text: str, compression_level: float = 0.3) -> str:
        """
        Обрабатывает длинные тексты путем разделения на части по 2000 символов

        Args:
            text (str): Длинный текст для суммаризации
            compression_level (float): Уровень сжатия

        Returns:
            str: Краткое содержание всего текста
        """
        # Разделяем текст на части по 2000 символов
        chunk_size = 2000
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size].strip()
            if len(chunk) > 100:  # Пропускаем слишком короткие части
                chunks.append(chunk)

        # Суммаризируем каждую часть
        summaries = []
        for i, chunk in enumerate(chunks[:10]):  # Обрабатываем максимум 10 частей
            try:
                # Для частей используем более высокий уровень сжатия
                part_compression = min(0.6, compression_level + 0.2)
                summary = self.summarize(chunk, part_compression)
                if summary and len(summary) > 20:
                    summaries.append(summary)
            except Exception as e:
                print(f"⚠️ Ошибка при обработке части {i + 1}: {str(e)}")
                continue

        if not summaries:
            print("Не удалось создать суммаризацию по частям. Использую обычный метод для начала текста.")
            return self.summarize(text[:2000], compression_level)

        # Объединяем результаты
        combined_summary = " ".join(summaries)

        # Если получилось слишком длинно, делаем финальную суммаризацию
        if len(combined_summary.split()) > 300:
            return self.summarize(combined_summary, compression_level)

        return combined_summary

    def _calculate_summary_length(self, text: str, compression_level: float) -> tuple[int, int]:
        """
        Рассчитывает длину краткого содержания в токенах

        Args:
            text (str): Текст для суммаризации
            compression_level (float): Уровень сжатия

        Returns:
            tuple: (max_length, min_length)
        """
        # Простой расчёт по количеству слов
        words = text.split()
        num_words = len(words)

        # Определяем целевое количество слов
        target_words = max(20, int(num_words * compression_level))

        # Переводим в токены (примерно 1.3 токена на слово)
        target_tokens = int(target_words * 1.3)

        # Устанавливаем лимиты
        max_length = min(400, target_tokens)
        min_length = max(10, int(max_length * 0.3))

        # Гарантируем, что min_length < max_length
        if min_length >= max_length:
            min_length = max(5, int(max_length * 0.5))

        # Для коротких текстов уменьшаем длину резюме
        if num_words < 30:
            max_length = max(10, min(int(num_words * 0.7), max_length))
            min_length = max(5, int(max_length * 0.5))

        return max_length, min_length

    def _post_process(self, text: str) -> str:
        """
        Улучшает качество результата суммаризации

        Args:
            text (str): Текст для пост-обработки

        Returns:
            str: Улучшенный текст
        """
        # Удаляем артефакты
        text = re.sub(r'<extra_id_\d+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Исправляем пунктуацию
        text = text.replace(" .", ".").replace(" ,", ",").replace(" :", ":").replace(" ;", ";")

        # Для русского языка добавляем точку в конце, если её нет
        if self.language == "ru" and not text.endswith((".", "!", "?")):
            text += "."
        # Для немецкого языка
        elif self.language == "de" and not text.endswith((".", "!", "?")):
            text += "."

        return text
