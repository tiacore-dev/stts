import logging

# Настройка логгера
def setup_logger():
    logger = logging.getLogger('chatbot')  # Используем именованный логгер
    logger.setLevel(logging.INFO)

    # Проверяем, был ли уже настроен логгер (чтобы не добавлять обработчики повторно)
    if not logger.handlers:
        # Добавляем обработчик для вывода логов в консоль
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Добавляем обработчик для записи логов в базу данных
        logger.addHandler(DatabaseLogHandler())

    return logger

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from app.database.managers.logs_manager import LogManager

        log_entry = self.format(record)
        db = LogManager()

        # Извлекаем user_id из дополнительных данных
        user_id = getattr(record, 'user_id', 'unknown')  # Если user_id не установлен, использовать 'unknown'

        try:
            # Записываем лог в базу данных
            db.add_logs(user_id=user_id, action=record.levelname, message=log_entry)
        except Exception as e:
            print(f"Ошибка при записи лога в базу данных: {e}")


