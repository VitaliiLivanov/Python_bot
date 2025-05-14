from aiogram import Bot, Dispatcher


import asyncio
import os

import misc

from handlers import main_router

# Создаем объект Bot с токеном, загруженным из переменной окружения TOKEN.
bot = Bot(token=os.getenv('BOT_TOKEN'))
# Создаем Dispatcher - это основной объект, отвечающий за обработку входящих сообщений и обновлений, от Telegram.
dp = Dispatcher()



# Определяем основную асинхронную функцию, Настраиваем и запускаем бота в режиме постоянного опроса(polling)
# Фиксируем время запуска и окончания работы бота on_start/on_shutdown
async def start_bot():
    dp.startup.register(misc.on_start)
    dp.shutdown.register(misc.on_shutdown)
    #Добавляем главный роутер в Диспетчер
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass