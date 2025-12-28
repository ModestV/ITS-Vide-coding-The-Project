# Multilingual Learning Material Summarizer
[![CI](https://github.com/ModestV/ITS-Vide-coding-The-Project/actions/workflows/test.yml/badge.svg)](https://github.com/ModestV/ITS-Vide-coding-The-Project/actions/workflows/test.yml)

## Description
This project provides an automated tool for creating abstractive summaries of educational materials in three languages: English, Russian, and German. It supports both short texts and long documents (PDF or TXT format), intelligently splits lengthy content into manageable chunks, and generates high-quality summaries while preserving key information and context. The project includes both a web interface (Streamlit) and a command-line interface for flexible usage.

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup
    ```bash
    git clone https://github.com/ModestV/ITS-Vide-coding-The-Project.git
    cd ITS-Vide-coding-The-Project
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

## Usage

### Basic Example
    ```bash
    # Summarize a text file with 40% compression in Russian
    streamlit run app.py
    # Then upload your file through the web interface
    ```

### Advanced Usage
For CLI usage (if implemented in the future):
    ```python
    from src.summarizer import MultilingualSummarizer
    
    # Create summarizer for English
    summarizer = MultilingualSummarizer("en")
    text = "Your educational material text here..."
    summary = summarizer.summarize(text, compression_level=0.4)
    print(summary)
    ```

To process long documents programmatically:
    ```python
    # For documents longer than 2000 characters
    long_summary = summarizer.summarize_long_text(long_text, compression_level=0.3)
    ```

## Project Structure
    ```
    .
    ├── src/                 # Source code
    │   ├── __init__.py
    │   └── summarizer.py    # Main summarization logic
    ├── tests/              # Unit tests
    │   ├── __init__.py
    │   └── test_summarizer.py
    ├── data/               # Sample data files
    │   ├── sample_en.txt
    │   ├── sample_ru.txt
    │   └── sample_de.txt
    ├── docs/               # Documentation
    ├── scripts/            # Utility scripts (future use)
    ├── .github/workflows/  # CI/ CD pipeline configuration
    │   └── ci.yml
    ├── app.py              # Streamlit web application
    ├── README.md
    ├── requirements.txt    # Project dependencies
    └── .gitignore
    ```

## Requirements
- transformers >= 4.30.0
- torch >= 2.0.1
- sentencepiece >= 0.1.99
- protobuf >= 3.20.3
- numpy >= 1.26.4
- nltk >= 3.8.1
- streamlit >= 1.32.0
- PyPDF2 >= 3.0.1
- pdfplumber >= 0.11.1
- pytest >= 7.4.0
- flake8 >= 6.1.0
- safety >= 2.3.5

## Testing

Run tests with:
    ```bash
    pytest
    ```

Run with coverage:
    ```bash
    pytest --cov=src tests/
    ```

The test suite includes:
- Unit tests for all three supported languages
- Integration tests that verify summarization actually reduces text length
- Quality assurance checks for proper text compression

## Contributing
Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code passes all existing tests and follows PEP 8 style guidelines.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
ModestV
