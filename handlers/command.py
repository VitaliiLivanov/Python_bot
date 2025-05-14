from aiogram import Bot, Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

import openai
import httpx
import os

from keyboards import keyboard_reply
from .handlers_state import ChatGPTRequests


command_router = Router()
@command_router.message(ChatGPTRequests.wait_for_request)
async def wait_for_gpt_handler(message: Message):
    await message.answer(
        text=f'Вы прислали запрос:\n{message.text}'
    )
    # gpt_response = await gpt_client.text_request('gpt')

# Асинхронный handler для /START
@command_router.message(F.text == 'Закончить')
@command_router.message(Command('start'))
async def command_start(message: Message):
    photo_path = os.path.join('resources', 'images', 'main.jpg')
    text_path = os.path.join('resources', 'messages', 'main.txt')
    photo = FSInputFile(photo_path)
    buttons = [
        '/random',
        '/gpt',
        '/talk',
        '/quiz',
    ]
    with open(text_path, 'r', encoding='UTF-8') as file:
        msg_text = file.read()
    await message.answer_photo(
        photo= photo,
        caption= msg_text,
        reply_markup=keyboard_reply(buttons),
    )

# Асинхронный handler для /RANDOM
@command_router.message(F.text == 'Хочу еще факт')
@command_router.message(Command('random'))
async def command_random(message: Message, bot: Bot):
    photo_path = os.path.join('resources', 'images', 'random.jpg')
    prompt_path = os.path.join('resources', 'prompts', 'random.txt')
    with open(prompt_path, 'r', encoding='UTF-8') as file:
        prompt = file.read()
    gpt_client = openai.AsyncOpenAI(
        api_key=os.getenv('GPT_TOKEN'),
        http_client=httpx.AsyncClient(
            proxy=os.getenv('PROXY'),
        )
    )

    msg_text = await gpt_client.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': prompt,
            }
        ],
        model='gpt-3.5-turbo',
    )

    # text_path = os.path.join('resources', 'messages', 'random.txt')
    photo = FSInputFile(photo_path)
    buttons = [
        'Хочу еще факт',
        'Закончить',
    ]

    # await message.answer_photo(
    #     photo= photo,
    #     caption= msg_text,
    #     reply_markup=keyboard_reply(buttons),
    # )


# @command_router.message(F.text == 'Хочу еще факт')
@command_router.message(Command('gpt'))
async def command_gpt(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(ChatGPTRequests.wait_for_request)
    await bot.send_chat_action(
        chat_id=message.from_user.id,
        action=ChatAction.TYPING,
    )
    photo_path = os.path.join('resources', 'images', 'random.jpg')
    msg_path = os.path.join('resources', 'messages', 'gpt.txt')
    photo = FSInputFile(photo_path)
    with open(msg_path, 'r', encoding='UTF-8') as file:
        message_text = file.read()
    await message.answer_photo(
        photo=photo,
        caption=message_text,
    )

