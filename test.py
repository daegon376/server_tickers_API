import requests
import time


class Ticker:
    tickers_list = []

    def __init__(self, ticker_data_list):
        self.symbol = ticker_data_list[0]
        self.price = ticker_data_list[1]
        self.volume = ticker_data_list[2]
        self.last_trade = ticker_data_list[3]
        Ticker.tickers_list.append([self.symbol, self.price, self.volume, self.last_trade])

    @classmethod
    def clear_tickers_list(cls):
        cls.tickers_list = []


def get_data_from_api(url):
    response_content = requests.get(url)
    tickers_list = response_content.json()
    for ticker in tickers_list:
        Ticker(list(ticker.values()))


def get_data_from_my_serv(url):
    response_content = requests.get(url)
    tickers_dict = response_content.json()
    tickers_list = []
    for key in tickers_dict:
        one_ticker = [key] + list(tickers_dict[key].values())
        tickers_list.append(one_ticker)
    return tickers_list


if __name__ == '__main__':
    while True:
        get_data_from_api('https://api.blockchain.com/v3/exchange/tickers')
        api_data = Ticker.tickers_list
        my_data = get_data_from_my_serv('http://127.0.0.1:5000/')
        if api_data == my_data:
            print('Test: SUCCESS')
        else:
            print('Test: FAILED')
            if len(my_data) == len(api_data):
                for i in range(len(my_data)):
                    if my_data[i] != api_data[i]:
                        print('  API DATA:', api_data[i], '\n',
                              'SERV DATA:', my_data[i])
        Ticker.clear_tickers_list()
        time.sleep(5)
