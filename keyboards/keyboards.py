from aiogram.utils.keyboard import ReplyKeyboardBuilder


def keyboard_reply(buttons):
    keyboard = ReplyKeyboardBuilder()

    for button in buttons:
        keyboard.button(
            text=button,
        )
    return keyboard.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню...',
    )


