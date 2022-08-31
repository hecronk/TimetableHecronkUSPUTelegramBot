from aiogram import Bot, Dispatcher, executor, types

from config import TelegramBotConfig, ParserConfig
from app.parser.parser import Parser

bot = Bot(token=TelegramBotConfig.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    groups = Parser.get_groups(ParserConfig.URL)
    markup = types.InlineKeyboardMarkup()
    for i in range(len(groups)):
        button = types.InlineKeyboardButton(groups[i], callback_data=groups[i])
        markup.add(button)
    await message.reply('Привет! Это бот расписания УрГПУ! Выбери свою группу ↓. Позднее ты сможешь ее изменить в настройках',
                        reply_markup=markup)
    await message.answer('Привет! Это бот расписания УрГПУ! Выбери свою группу ↑. Позднее ты сможешь ее изменить в настройках')


# @dp.callback_query_handler