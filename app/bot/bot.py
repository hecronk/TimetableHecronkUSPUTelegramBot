import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
import ast
import itertools

from config import TelegramBotConfig, ParserConfig
from app.parser.parser import Parser
from app.models import User, session

bot = Bot(token=TelegramBotConfig.TOKEN)
dp = Dispatcher(bot)


def get_start_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    schedule_button = types.KeyboardButton('Расписание')
    settings_button = types.KeyboardButton('Настройки')
    markup.add(schedule_button, settings_button)
    return markup


def get_current_markups(page: int) -> list:
    groups = Parser.get_groups(ParserConfig.URL)
    list_of_groups = itertools.zip_longest(*(iter(groups),) * 6)
    markups = list()
    for group in list_of_groups:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(6):
            markup.add(types.InlineKeyboardButton(group[i], callback_data=groups[page*6 + i]))
        markups.append(markup)
    return markups


@dp.message_handler(commands='start')
async def start(message: types.Message):
    if not session.query(User).filter(User.telegram_id == message.from_user.id).first():
        markups = get_current_markups(0)
        markups[0].add(types.InlineKeyboardButton('Назад', callback_data='group_page=0'),
                   types.InlineKeyboardButton('Вперед', callback_data='group_page=1'))
        await message.reply(
            'Привет! Это бот расписания УрГПУ! Выбери свою группу ↓. Ты всегда сможешь ее изменить в настройках',
            reply_markup=markups[0])
    else:
        await message.delete()
        await message.answer(f'С возвращением!'
                             f' Ваша группа {str(session.query(User).filter(User.telegram_id == message.from_user.id).first().group)}',
                             reply_markup=get_start_markup())


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    if callback.message:
        if 'group_page=' in callback.data:
            number = int(callback.data.split('=')[1])
            if number in range(0, len(get_current_markups(page=number))-1):
                markup = get_current_markups(number)[number]
                markup.add(types.InlineKeyboardButton(f'Назад', callback_data=f'group_page={number-1}'),
                                        types.InlineKeyboardButton(f'Вперед', callback_data=f'group_page={number+1}'))
                try:
                    await callback.message.edit_reply_markup(reply_markup=markup)
                except aiogram.utils.exceptions.MessageNotModified:
                    pass
        elif callback.data in Parser.get_groups(ParserConfig.URL):
            if not session.query(User).filter(User.telegram_id == callback.from_user.id).first():
                user = User(telegram_id=callback.from_user.id, group=callback.data)
                session.add(user)
                session.commit()
            session.query(User).filter(User.telegram_id == callback.from_user.id).first().group = callback.data
            session.commit()
            group = session.query(User).filter(User.telegram_id == callback.from_user.id).first().group
            await callback.message.answer(f'Установлена группа {group}. Для изменения группы перейдите в настройки',
                                          reply_markup=get_start_markup())
            await callback.message.delete()
        elif callback.data in str(Parser.get_available_days(ParserConfig.URL, group=str(
                session.query(User).filter(User.telegram_id == callback.from_user.id).first().group))):
            day = ast.literal_eval(callback.data)
            content = Parser.get_content(url=ParserConfig.URL,
                                         group=str(session.query(User).filter(
                                             User.telegram_id == callback.from_user.id).first().group),
                                         day=day)
            result = content['update'] + '\n' + day['week'] + ' ' + day['date'] + '\n' * 2
            for i in range(len(content['content'])):
                result += 'Время: ' + content['content'][i]['time'] + '\n' + 'Предмет: ' + content['content'][i][
                    'lesson_name + auditorium'] + (
                              '\n' + content['content'][i]['subgroup'].title() if content['content'][i][
                                                                                      'subgroup'] != '' else '') + '\n' + \
                          content['content'][i]['teacher'] + '\n' * 2
            await callback.message.answer(result)
            await callback.message.delete()
        elif callback.data == '/start':
            await start(message=callback.message)
            await callback.message.delete()
        elif callback.data == '/menu':
            await callback.message.delete()


@dp.message_handler(content_types='text')
async def main(message: types.Message):
    await message.delete()
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
        markup.add(change_group_button)
        markup.add(back_button)
        await message.answer('Настройки:', reply_markup=markup)
