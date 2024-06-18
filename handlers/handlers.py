__all__ = [
    "register_message_handler",
]

import logging

from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import Command
from sqlalchemy.ext.asyncio import AsyncSession

from db import async_session_maker, User
from db.models import YandexFolder
from yandex import YandexDisk
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


async def register_command(message: types.Message):
    text = (f"Для регистрации токена следуйте шагам:\n"
            f"1. Нажмите на: <a href=\"\"></a>\n"
            f"2. Авторизируйтесь в ЯДиске через свой личный аккаунт\n"
            f"3. Вставьте результат в /token ТОКЕН")
    await message.reply(text=text, parse_mode="HTML")

    logging.info(f"user {message.from_user.id} instructions")


async def token_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession
        teacher_model = await session.get(User, message.from_user.id)
        if teacher_model.teacher_id is not None:
            await message.reply("Доступно только преподавателю!")
        else:
            tokentext = message.text.split()

            if len(tokentext) == 2:
                token = tokentext[1].strip()

                client = YandexDisk(token=token)
                valid = await client.valid()

                if valid:
                    await message.reply(f"Успешно! Вы добавили / обновили токен")

                    # save
                    teacher_model.token = token
                else:
                    await message.reply(f"Ошибка проверки!")

            else:
                await message.reply("Узнать Ваш ТОКЕН - /status. Добавить ТОКЕН с помощью /token ВАШ_ТОКЕН")

        logging.info(f"user {message.from_user.id} pressed token")
        await session.commit()


async def add_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession
        arr = message.text.split()

        if len(arr) is 2:
            foldername = arr[1].strip()
            teachermodel = await session.get(User, message.from_user.id)

            if teachermodel.teacher_id:
                await message.reply("Доступно только преподавателю!")
            elif not teachermodel.token:
                await message.reply("Добавьте токен /token")
            else:
                new = YandexFolder(teacher_id=teachermodel.id, name=foldername)
                session.add(new)

                await message.reply(f"Добавьте папку с помощью /add НАЗВАНИЕ_ПАПКИ")
        else:
            await message.reply("Укажите название или путь к папке через пробел после /add")
        logging.info(f"user {message.from_user.id} add folder pressed")

        await session.commit()
        await session.close()


def register_message_handler(router: Router):
    """Маршрутизация"""
    router.message.register(start_command, Command(commands=["start"]))
    router.message.register(register_command, Command(commands=["register"]))
    router.message.register(status_command, Command(commands=["status"]))
    router.message.register(token_command, Command(commands=["token"]))
    router.message.register(help_command, Command(commands=["help"]))
    router.message.register(add_command, Command(commands=["add"]))
    router.message.register(delete_command, Command(commands=["delete"]))

    #обработчик ответа при нажатии на кнопку после /start, считываем по первому слову
    router.callback_query.register(callback_continue, F.data.startswith("register_"))
