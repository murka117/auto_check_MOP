# auto_check_MOP

Программа для автоматической проверки и агрегации Excel-файлов по этажам с гибкой обработкой заголовков, поддержкой подвалов и мультипликаторов, а также экспортом результата.

## Быстрый старт

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/murka117/auto_check_MOP.git
   cd auto_check_MOP
   ```
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Запустите программу:
   ```
   python run_app.py
   ```

## Упаковка в exe (PyInstaller)

1. Установите pyinstaller:
   ```
   pip install pyinstaller
   ```
2. Соберите exe:
   ```
   pyinstaller --onefile --noconsole run_app.py
   ```
   Если используются гифки/ресурсы:
   ```
   pyinstaller --onefile --noconsole --add-data "your_gif.gif;." run_app.py
   ```

## Структура Excel-файлов
- Каждый лист — отдельный этаж, подвал или сводная.
- В каждом листе: "Марка", "Наименование", "Количество" (или похожие названия).
- Подробнее — см. комментарии в logic.py или обратитесь к автору.

## Контакты
- GitHub: https://github.com/murka117/auto_check_MOP
