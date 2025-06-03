# Win OCR Screen

![python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-%F0%9F%92%96-green)
![Tesseract](https://img.shields.io/badge/tesseract-OCR-red)

**Win OCR Screen** — небольшая утилита для создания снимков экрана и мгновенного оптического распознавания текста.

![screenshot](screenshot.png)

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python ocr_screen.py
```

При необходимости можно указать путь к Tesseract через переменную
`TESSERACT_PATH` и интерпретатор Python через `PYTHON_EXECUTABLE`.

Для быстрого запуска можно основаться на скриптах `ocr.sh` и `ocr.bat`.

## Горячие клавиши

- `Ctrl+Alt+O` — пуск или остановка программы.
- `Ctrl+Alt+P` — выход.

## Файлы

- `ocr_screen.py` — графический интерфейс для выбора области экрана и передачи изображения в Tesseract.
- `starter.py` — слушает горячие клавиши и запускает OCR.
- `ocr.sh` и `ocr.bat` — примеры скриптов для запуска.
- `requirements.txt` — зависимости Python.

## Задачи по улучшению

Для дальнейшего развития проекта можно рассмотреть следующие шаги:

- Отказаться от жёстко заданных путей к Python и Tesseract, перенести их в настройки.
- Промежуточные изображения сохранять временно или обрабатывать в памяти.
- Добавить обработку ошибок и логирование.
- Убрать лишние зависимости ("pyautogui") и создать `.gitignore`.
- Вынести процесс оптического распознавания в отдельный поток, чтобы не замедлять UI.
