from aiogram import Bot, Dispatcher, executor, types
import ast

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
    if not session.query(User).filter(User.telegram_id == message.from_user.id).first():
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
    else:
        await message.answer('С вовзращением!', reply_markup=get_start_markup())


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    if callback.message:
        if callback.data in Parser.get_groups(ParserConfig.URL):
            if not session.query(User).filter(User.telegram_id == callback.from_user.id).first():
                user = User(telegram_id=callback.from_user.id, group=callback.data)
                session.add(user)
                session.commit()
            session.query(User).filter(User.telegram_id == callback.from_user.id).first().group = callback.data
            session.commit()
            group = session.query(User).filter(User.telegram_id == callback.from_user.id).first().group
            await callback.message.answer('Установлена группа {}.'
                                          ' Для изменения группы перейдите в настройки'.format(group),
                                          reply_markup=get_start_markup())
            await callback.message.delete()
        if callback.data in str(Parser.get_available_days(ParserConfig.URL, group=str(
                session.query(User).filter(User.telegram_id == callback.from_user.id).first().group))):
            day = ast.literal_eval(callback.data)
            content = Parser.get_content(url=ParserConfig.URL,
                                         group=str(session.query(User).filter(
                                             User.telegram_id == callback.from_user.id).first().group),
                                         day=day)
            result = content['update'] + '\n' + day['week'] + ' ' + day['date'] + '\n'*2
            for i in range(len(content['content'])):
                result += 'Время: ' + content['content'][i]['time'] + '\n' + 'Предмет: ' + content['content'][i]['lesson_name + auditorium'] + ('\n' + content['content'][i]['subgroup'].title() if content['content'][i]['subgroup'] != '' else '') + '\n' + content['content'][i]['teacher'] + '\n'*2
            await callback.message.answer(result)
        if callback.data == '/start':
            await start(message=callback.message)
        if callback.data == '/menu':
            await callback.message.answer('Добро пожаловать!', reply_markup=get_start_markup())


@dp.message_handler(content_types='text')
async def main(message: types.Message):
    if message.text == 'Расписание':
        group = str(session.query(User).filter(User.telegram_id == message.from_user.id).first().group)
        days = Parser.get_available_days(url=ParserConfig.URL, group=group)
        markup = types.InlineKeyboardMarkup()
        for i in range(len(days)):
            button = types.InlineKeyboardButton(days[i]['date'] + ' - ' + days[i]['week'], callback_data=str(days[i]))
            markup.add(button)
        await message.answer('Выбери день:', reply_markup=markup)
    if message.text == 'Настройки':
        markup = types.InlineKeyboardMarkup()
        change_group_button = types.InlineKeyboardButton('Изменить группу', callback_data='/start')
        back_button = types.InlineKeyboardButton('Назад', callback_data='/menu')
        markup.add(change_group_button, back_button)
        await message.answer('Меню настроек:', reply_markup=markup)

