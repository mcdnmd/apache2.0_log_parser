#!/usr/bin/env python3
import unittest
import re
from enum import Enum
import datetime
import urllib.request

TEST_LOG = "https://raw.githubusercontent.com/mcdnmd/" \
           "hw4/master/test.log"


class Month(Enum):
    Jan = 1
    Feb = 2
    Mar = 3
    Apr = 4
    May = 5
    Jun = 6
    Jul = 7
    Aug = 8
    Sep = 9
    Oct = 10
    Nov = 11
    Dec = 12


class Log:
    def __init__(self):
        self.parse_is_possible = False
        self.ip = ""
        self.date = ""
        self.method = ""
        self.request_path = ""
        self.http_version = ""
        self.status_code = 0
        self.response_size = 0
        self.referrer = ""
        self.user_agent = ""
        self.time = 0

    def parse_log_string(self, log_str):
        if log_str != "":
            log_regex = r'(?P<ip>[(\d\.)]+) - - ' \
                        r'\[(?P<date>.*?) [-+](.*?)\] ' \
                        r'"(?P<method>\w+) ' \
                        r'(?P<request_path>.*?) ' \
                        r'HTTP/(?P<http_version>.*?)" ' \
                        r'(?P<status_code>\d+) ' \
                        r'(?P<response_size>\d+) ' \
                        r'"(?P<referrer>.*?)" ' \
                        '"(?P<user_agent>.*?)" ' \
                        r'(?P<time>.\d+)'
            regex = re.compile(log_regex)
            self.parse_is_possible = True
            mo = regex.match(log_str)
            if mo is None:
                self.parse_is_possible = False
                return
            self.load_variables(mo)
        else:
            self.parse_is_possible = False

    def load_variables(self, data):
        self.ip = data.group('ip')
        self.date = self.converte_date(data.group('date'))
        self.method = data.group('method')
        self.request_path = data.group('request_path')
        self.http_version = data.group('http_version')
        self.status_code = data.group('status_code')
        self.response_size = data.group('response_size')
        self.referrer = data.group('referrer')
        self.user_agent = data.group('user_agent')
        self.time = data.group('time')

    def converte_date(self, date):
        date_filter = r'(?P<day>\d+)/(?P<month>\w+)/(?P<year>\d+)+'
        compiled = re.compile(date_filter)
        mo = compiled.match(date)
        return datetime.date(int(mo.group("year")),
                             int(Month[mo.group("month")].value),
                             int(mo.group("day")))


class Statistics:
    def __init__(self):
        self.recalculation = False
        self.Log = Log()
        self.FastestPage = ""
        self.MostActiveClient = ""
        self.MostActiveClientByDay = ""
        self.MostPopularBrowser = ""
        self.MostPopularPage = ""
        self.SlowestAveragePage = ""
        self.SlowestPage = ""
        self.browser_dict = {}
        self.ip_dict = {}
        self.page_dict = {}
        self.day_active_dict = {}
        self.average_page_time = {}
        self.minimal_response_time = 99999999
        self.maximal_response_time = -1
        self.slowest_average_time = -1
        self.result = {}

    def add_line(self, line):
        self.Log.parse_log_string(line)
        if self.Log.parse_is_possible and self.Log.time != -1:
            self.update_ip_active(self.Log.ip)
            self.update_response_time(self.Log.time)
            self.update_page(self.Log.request_path)
            self.update_user_agent(self.Log.user_agent)
            self.update_day_active(self.Log.date)
            self.recalculation = True
        else:
            return

    def update_day_active(self, date):
        if date not in self.day_active_dict.keys():
            self.day_active_dict[date] = {}
        if self.Log.ip in self.day_active_dict[date]:
            self.day_active_dict[date][self.Log.ip] += 1
        else:
            self.day_active_dict[date][self.Log.ip] = 1

    def update_response_time(self, time):
        if int(time) <= self.minimal_response_time:
            self.minimal_response_time = int(time)
            self.FastestPage = self.Log.request_path
        if int(time) >= self.maximal_response_time:
            self.maximal_response_time = int(time)
            self.SlowestPage = self.Log.request_path

    def update_ip_active(self, ip):
        if ip in self.ip_dict.keys():
            self.ip_dict[ip] += 1
        else:
            self.ip_dict[ip] = 1

    def update_user_agent(self, user_agent):
        if user_agent in self.browser_dict.keys():
            self.browser_dict[user_agent] += 1
        else:
            self.browser_dict[user_agent] = 1

    def update_page(self, page):
        if page in self.page_dict.keys():
            self.page_dict[page] += 1
        else:
            self.page_dict[page] = 1
        if page not in self.average_page_time.keys():
            self.average_page_time[page] = int(self.Log.time)
        else:
            self.average_page_time[page] += int(self.Log.time)

    def prepare_daily_active(self):
        dict = {}
        for day in self.day_active_dict.items():
            day_str = day[0]
            day = sorted(day[1].items(),
                         key=lambda item: (item[1], item[0]),
                         reverse=True)
            dict[day_str] = day[0][0]
        return dict

    def result_average_page_time(self):
        for page in self.page_dict:
            average_time = self.average_page_time[page[0]] / page[1]
            if average_time > self.slowest_average_time:
                self.slowest_average_time = average_time
                self.SlowestAveragePage = page[0]

    def results(self):
        if self.recalculation:
            self.browser_dict = sorted(self.browser_dict.items(),
                                       key=lambda item: (item[1], item[0]),
                                       reverse=True)
            self.page_dict = sorted(self.page_dict.items(),
                                    key=lambda item: (-item[1], item[0]))
            self.ip_dict = sorted(self.ip_dict.items(),
                                  key=lambda item: (item[1], item[0]),
                                  reverse=True)
            self.result_average_page_time()

            self.result["FastestPage"] = self.FastestPage
            self.result["SlowestPage"] = self.SlowestPage
            self.result["MostPopularBrowser"] = self.browser_dict[0][0]
            self.result["MostPopularPage"] = self.page_dict[0][0]
            self.result["MostActiveClient"] = self.ip_dict[0][0]
            self.result["MostActiveClientByDay"] = self.prepare_daily_active()
            self.result["SlowestAveragePage"] = self.SlowestAveragePage
        return self.result


def make_stat():
    return Statistics()


class LogStatTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        with urllib.request.urlopen(TEST_LOG) as f:
            self.data = f.read().decode('utf-8').split('\n')
        self.stat = make_stat()

    def test(self):
        for line in filter(lambda s: 'OPTION' not in s, self.data):
            self.stat.add_line(line)

        self.assertDictEqual(self.stat.results(), TEST)


TEST = {
    'FastestPage': '/css/main.css',
    'MostActiveClient': '192.168.74.151',
    'MostActiveClientByDay': {datetime.date(2013, 2, 17): '192.168.74.151'},
    'MostPopularBrowser': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; '
                          'WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; '
                          '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media '
                          'Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'MostPopularPage': '/pause/ajaxPause?pauseConfigId=&admin=0',
    'SlowestAveragePage': '/lib/callider/graph.registr_tel.php?auto=0',
    'SlowestPage': '/pause/ajaxPause?pauseConfigId=&admin=0'}
