import os.path
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env'))


class TelegramBotConfig(object):
    TOKEN = os.environ.get('BOT_TOKEN')


class ParserConfig(object):
    URL = 'https://uspu.ru/education/eios/schedule/?group_name='
    HEADERS = {
        'Accept': '*/*',
        'User-Agent': 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70'
    }
