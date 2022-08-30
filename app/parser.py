import requests
from bs4 import BeautifulSoup
from config import ParserConfig


class Parser:
    @staticmethod
    def _get_html(url):
        html = requests.get(url, headers=ParserConfig.HEADERS)
        if Parser._server_is_respond(html):
            return html
        else:
            raise ConnectionError('Status code = {code}'.format(code=html.status_code))

    @staticmethod
    def _server_is_respond(html):
        return True if html.status_code == 200 else False

    @staticmethod
    def get_groups(url):
        try:
            soup = BeautifulSoup(Parser._get_html(url).text, 'html.parser')
        except ConnectionError:
            return "Can't Parse!"
        groups = soup.find('select', attrs={'name': 'group_name'})
        return groups.text.split('\n')[2:-2]

    @staticmethod
    def get_content(url: str, group: str):
        try:
            soup = BeautifulSoup(Parser._get_html(url + group).text, 'html.parser')
        except ConnectionError:
            return "Can't Parse!"
        temp = soup.find('div', attrs={'class': 'rasp-list rasp-list-group'}).text.split('\n' * 6)
        result = {
            'date': temp[0].split('\n\n')[1],
            'day_of_the_week': temp[0].split('\n\n')[2],
            'schedule': list(),
        }
        for i in temp[0].split('\n\n\n'):
            times = 0
            if i != ('\n\n' + result['date'] + '\n\n' + result['day_of_the_week']) and times == 0:
                times += 1
                result['schedule'].append({'time': i.split('\n\n')[0],
                                           'lesson_name': i.split('\n')[2].split('(')[0][:-1],
                                           'auditorium': i.split('\n')[2].split(')')[-1][1:],
                                           'teacher': i.split('\n')[3]})
        return result


print(Parser.get_content(url=ParserConfig.URL, group='РиА-1931'))
