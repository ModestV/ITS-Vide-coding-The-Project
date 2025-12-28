import pytest


def pytest_configure(config):
    """Добавляем маркеры для тестов"""
    config.addinivalue_line(
        "markers", "slow: помечает тест как медленный (пропускается при запуске без --runslow)"
    )


def pytest_addoption(parser):
    """Добавляем опцию для запуска медленных тестов"""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="запускать медленные тесты"
    )


def pytest_collection_modifyitems(config, items):
    """Пропускаем медленные тесты если нет флага --runslow"""
    if config.getoption("--runslow"):
        return
    skip_slow = pytest.mark.skip(reason="нужен флаг --runslow для запуска")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
