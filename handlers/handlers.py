__all__ = [
    "register_message_handler",
]


import logging

from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import Command
from sqlalchemy.ext.asyncio import AsyncSession

from db import async_session_maker, User
from .callbacks import callback_continue
from .keyboards import register_buttons

# настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def help_command(message: types.Message):
    help_str = """Вас приветствует бот <b><i>ranhahaha_bot</i></b>
    💬 Регистрация пользователя <b>/start</b>
    💬 Информацию о пользователе можно вывести с помощью команды <b>/status</b>"""

    logging.info(f"user {message.from_user.id} asked for help")
    await message.reply(text=help_str, parse_mode="HTML")


async def status_command(message: types.Message):
    """Информация о пользователе"""

    async with async_session_maker() as session:
        session: AsyncSession

        current_user = await session.get(User, message.from_user.id)

        await session.close()

        if current_user is None:
            await message.reply(text="Ничего о Вас не знаем! Регистрация /start")
        else:
            str = f"""<b><i>Статус</i></b>
                Ваш ID - {current_user.id}
                Ваше имя - {current_user.name}"""

            await message.reply(text=str, parse_mode="HTML")

        logging.info(f"user {message.from_user.id} requested status")


async def start_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession

        user = await session.get(User, message.from_user.id)

        await session.close()

        if user is None:
            await message.reply("Выберите роль:", reply_markup=register_buttons)
        else:
            await message.reply(f"Вы уже зарегестрированы")

        logging.info(f"user {message.from_user.id} started the bot")


def register_message_handler(router: Router):
    """Маршрутизация"""
    router.message.register(start_command, Command(commands=["start"]))
    router.message.register(status_command, Command(commands=["status"]))
    router.message.register(help_command, Command(commands=["help"]))

    #обработчик ответа при нажатии на кнопку после /start, считываем по первому слову
    router.callback_query.register(callback_continue, F.data.startswith("register_"))
