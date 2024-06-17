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

    await message.reply(text=help_str, parse_mode="HTML")
    logging.info(f"user {message.from_user.id} asked for help")


async def status_command(message: types.Message):
    """Информация о пользователе"""

    async with async_session_maker() as session:
        session: AsyncSession

        current_user = await session.get(User, message.from_user.id)

        if current_user:
            str = f"""<b><i>Статус</i></b>
                            Ваш ID - {current_user.id}
                            Ваше имя - {current_user.name}
                            Дата регистрации - {current_user.reg_date}"""

            if current_user.token:
                str += f"\nТокен - {current_user.token}"

            if current_user.teacher_id:
                teacher = await session.get(User, current_user.teacher_id)

                str += f"\nВы слушатель у - {teacher.name}"

            await message.reply(text=str, parse_mode="HTML")
        else:
            await message.reply(text="Ничего о Вас не знаем! Регистрация /start")

        await session.close()

        logging.info(f"user {message.from_user.id} requested status")


async def start_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession

        user = await session.get(User, message.from_user.id)

        if user is None:
            await message.reply("Выберите желаемую роль:", reply_markup=register_buttons)
        else:
            if user.teacher_id:
                user_teacher = await session.get(User, user.teacher_id)
                await message.reply(f"Вы уже зарегестрированы как слушатель у {user_teacher.name}")
            else:
                await message.reply(f"Вы уже зарегестрированы как преподаватель. Для регистрации юзеров пришлите им свой Id /status")

        await session.close()
        logging.info(f"user {message.from_user.id} started the bot")


def register_message_handler(router: Router):
    """Маршрутизация"""
    router.message.register(start_command, Command(commands=["start"]))
    router.message.register(status_command, Command(commands=["status"]))
    router.message.register(help_command, Command(commands=["help"]))

    #обработчик ответа при нажатии на кнопку после /start, считываем по первому слову
    router.callback_query.register(callback_continue, F.data.startswith("register_"))
