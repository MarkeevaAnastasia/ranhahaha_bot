__all__ = [
    "commands_for_bot",
]

from aiogram import types

bot_commands = (
    ("start", "Старт бота"),
    ("status", "Информация о пользователе"),
    ("help", "Команды бота"),
    ("register", "Инструкция по регистрации на ЯДиске"),
    ("token", "Токен для ЯДиска"),
    ("add", "Добавление папки"),
    ("delete", "Удаление папки")
)

commands_for_bot = []
for cmd in bot_commands:
    commands_for_bot.append(types.BotCommand(command=cmd[0], description=cmd[1]))
