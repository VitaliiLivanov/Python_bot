from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import os

from classes import gpt_client
from classes.chat_gpt import BotPhoto, BotPath, GPTMessage, GPTRole
from keyboards.callback_data import CelebrityData, QuizData
from .handlers_state import CelebrityTalk, Quiz

callback_router = Router()


@callback_router.callback_query(CelebrityData.filter(F.button == 'select_celebrity'))
async def celebrity_callbacks(callback: CallbackQuery, callback_data: CelebrityData, bot: Bot, state: FSMContext):
    photo = BotPhoto(callback_data.file_name).photo
    file_name = callback_data.file_name
    with open(os.path.join(BotPath.PROMPTS.value, file_name + '.txt'), 'r', encoding='UTF-8') as file:
        celebrity_name = file.readline().split(', ')[0][5:]
    await callback.answer(
        text=f'С тобой говорит {celebrity_name}',
    )
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=photo,
        caption='Задайте свой вопрос:',
    )
    request_message = GPTMessage(file_name)
    await state.set_state(CelebrityTalk.wait_for_answer)
    await state.set_data({'messages': request_message, 'photo': photo})


@callback_router.callback_query(QuizData.filter(F.button == 'select_topic'))
async def celebrity_callbacks(callback: CallbackQuery, callback_data: QuizData, bot: Bot, state: FSMContext):
    photo = BotPhoto('quiz').photo
    await callback.answer(
        text=f'Вы выбрали тему {callback_data.topic_name}!',
    )
    request_message = GPTMessage('quiz')
    request_message.update(GPTRole.USER, callback_data.topic)
    response = await gpt_client.request(request_message)
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=photo,
        caption=response,
    )
    await state.set_state(Quiz.wait_for_answer)
    await state.set_data({'messages': request_message, 'photo': photo, 'score': 0, 'callback': callback_data})


@callback_router.callback_query(QuizData.filter(F.button == 'next_question'))
async def quiz_next_question(callback: CallbackQuery, callback_data: QuizData, state: FSMContext):
    data: dict[str, GPTMessage | str] = await state.get_data()
    data['messages'].update(GPTRole.USER, 'quiz_more')
    response = await gpt_client.request(data['messages'])
    data['messages'].update(GPTRole.ASSISTANT, response)
    await callback.bot.send_photo(
        chat_id=callback.from_user.id,
        photo=data['photo'],
        caption=response,
    )
    await callback.answer(
        text=f'Продолжаем тему {data['callback'].topic_name}'
    )
    await state.update_data(data)
