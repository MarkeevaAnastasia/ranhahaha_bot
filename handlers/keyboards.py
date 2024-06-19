from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

register_teacher_single_button = InlineKeyboardButton(
    text="Учитель",
    callback_data="register_teacher",
)

register_listener_single_button = InlineKeyboardButton(
    text="Студент",
    callback_data="register_listener",
)

register_buttons = InlineKeyboardMarkup(inline_keyboard=[[register_teacher_single_button, register_listener_single_button]])