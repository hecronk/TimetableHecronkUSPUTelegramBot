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
    def get_available_days(url: str, group: str):
        try:
            soup = BeautifulSoup(Parser._get_html(url + group).text, 'html.parser')
        except ConnectionError:
            return "Can't Parse!"
        stud_r = soup.find('div', attrs={'class': 'stud-r'})
        items = stud_r.find_all('div', attrs={'class': 'rasp-item'})
        days = list()
        for item in range(len(items)):
            days.append({
                'date': items[item].find('span', attrs={'class': 'rasp-day'}).getText(),
                'week': items[item].find('div', attrs={'class': 'rasp-week'}).getText()
            })
        return days

    @staticmethod
    def get_content(url: str, group: str, day: dict):
        try:
            soup = BeautifulSoup(Parser._get_html(url + group).text, 'html.parser')
        except ConnectionError:
            return "Can't Parse!"
        stud_r = soup.find('div', attrs={'class': 'stud-r'})
        items = stud_r.find_all('div', attrs={'class': 'rasp-item'})[Parser.get_available_days(url, group).index(day)]  # paste here day
        lessons_count = len(items.find_all('span', attrs={'class': 'para-time'}))
        lessons = list()
        for i in range(lessons_count):
            data = items.find_all('p')[i].getText().split('\n') # list with lesson, auditorium, teacher, subgroup
            lessons.append({
                'time': items.find_all('span', attrs={'class': 'para-time'})[i].getText(),  # paste here para time by index,
                'lesson_name + auditorium': data[0],
                'teacher': data[1],
                'subgroup': data[2]
            })
        result = {
            'update': stud_r.find('script').get_text().split(r"$('.stud-r .rasp-update').html('")[1][:-8],
            'content': lessons
        }
        return result


# print(Parser.get_available_days(url=ParserConfig.URL, group='ХОР-1931oz'))
print(Parser.get_content(url=ParserConfig.URL, group='ФК-2132', day={'date': '05 сентября', 'week': 'Пн'}))
