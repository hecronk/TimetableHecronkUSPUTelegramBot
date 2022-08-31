from aiogram import Bot, Dispatcher, executor, types

from config import TelegramBotConfig, ParserConfig
from app.parser.parser import Parser
from app.models import User, session

bot = Bot(token=TelegramBotConfig.TOKEN)
dp = Dispatcher(bot)


def get_start_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    schedule_button = types.KeyboardButton('Расписание')
    settings_button = types.KeyboardButton('Настройки')
    markup.add(schedule_button, settings_button)
    return markup


@dp.message_handler(commands='start')
async def start(message: types.Message):
    groups = Parser.get_groups(ParserConfig.URL)
    markup = types.InlineKeyboardMarkup()
    for i in range(len(groups)):
        button = types.InlineKeyboardButton(groups[i], callback_data=groups[i])
        markup.add(button)
    await message.reply(
        'Привет! Это бот расписания УрГПУ! Выбери свою группу ↓. Позднее ты сможешь ее изменить в настройках',
        reply_markup=markup)
    await message.answer(
        'Привет! Это бот расписания УрГПУ! Выбери свою группу ↑. Позднее ты сможешь ее изменить в настройках')


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    if callback.message:
        if callback.data in Parser.get_groups(ParserConfig.URL):
            if not session.query(User).filter(User.telegram_id == callback.message.from_user.id).first():
                user = User(telegram_id=callback.message.from_user.id, group=callback.data)
                session.add(user)
                session.commit()
            session.query(User).filter(User.telegram_id == callback.message.from_user.id).first().group = callback.data
            session.commit()
            group = session.query(User).filter(User.telegram_id == callback.message.from_user.id).first().group
            # days = Parser.get_available_days(url=ParserConfig.URL, group=group)
            await callback.message.answer('Установлена группа {}.'
                                          ' Для изменения группы перейдите в настройки'.format(group),
                                          reply_markup=get_start_markup())
