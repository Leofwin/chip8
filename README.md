# CHIP-8 Emulator
Версия 0.5
Автор: Чуприлин Андрей <leofwin98@yandex.ru>

## Описание
Данное приложение является эмулятором CHIP-8, интерпретируего языка программирования, разработанного Джозефом Уэйсбекером.


## Требования
* Python версии 3.6.0
* PyQt версии 5


## Состав
* Класс Emulator: `emulator.py`
* Класс Memory: `memory.py`
* Класс Screen: `screen.py`
* Графическая версия приложения: `gui.py`
* Файл настроек `settings.py`
* Папка с играми: `games/`
* Папка с музыкальными файлами: `sounds/`
* Тесты: `tests/`

Для запуска нужного блока тестов запустите `[block_name].py` через интерпретатор python

Пример запуска для тестов класса Game: `path\to\project> python tests/test_emulator.py`

## Графическая версия
Пример запуска: `python ./gui.py`

## Подробности реализации
Модуль `emulator` содержит класс управления эмулятором. 
Для хранения основной памяти используется модуль `memory`. 
Для хранения экрана используется модуль `screen`.
Модуль `settings` содержит константы.

## Последние изменения
* Исправлен баг с зажатием клавиши, управление теперь работает корректно
* Заблокирована возможность изменения размера окна