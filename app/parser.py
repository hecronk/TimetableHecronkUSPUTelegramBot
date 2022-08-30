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
        stud_r = soup.find('div', attrs={'class': 'stud-r'})
        update = stud_r.find('script').get_text().split(r"$('.stud-r .rasp-update').html('")[1][:-8]
        items = stud_r.find_all('div', attrs={'class': 'rasp-item'})[0]  # paste here day
        items.find('span', attrs={'class': 'rasp-day'}).getText()
        items.find('div', attrs={'class': 'rasp-week'}).getText()
        items.find_all('span', attrs={'class': 'para-time'})[0].getText()  # paste here para time by index
        return update


print(Parser.get_content(url=ParserConfig.URL, group='РиА-1931'))
