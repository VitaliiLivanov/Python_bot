from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .handlers_state import CelebrityTalk, ChatGPTRequests

from classes import gpt_client
from classes.chat_gpt import GPTMessage, GPTRole, BotPhoto
from keyboards import kb_end_talk
from .command import com_start
from misc import bot_thinking

message_router = Router()


@message_router.message(CelebrityTalk.wait_for_answer, F.text == 'Попрощаться!')
async def end_talk_handler(message: Message, state: FSMContext):
    await state.clear()
    await com_start(message)


@message_router.message(ChatGPTRequests.wait_for_request)
async def wait_for_gpt_handler(message: Message, bot: Bot, state: FSMContext):
    await bot_thinking(message, bot)
    gpt_message = GPTMessage('gpt')
    gpt_message.update(GPTRole.USER, message.text)
    gpt_response = await gpt_client.request(gpt_message)
    photo = BotPhoto('gpt').photo
    await message.answer_photo(
        photo=photo,
        caption=gpt_response,
    )
    await state.clear()


@message_router.message(CelebrityTalk.wait_for_answer)
async def talk_handler(message: Message, bot: Bot, state: FSMContext):
    await bot_thinking(message, bot)
    data: dict[str, GPTMessage | str] = await state.get_data()
    data['messages'].update(GPTRole.USER, message.text)
    response = await gpt_client.request(data['messages'])
    await message.answer_photo(
        photo=data['photo'],
        caption=response,
        reply_markup=kb_end_talk(),
    )
    data['messages'].update(GPTRole.ASSISTANT, response)
    await state.update_data(data)