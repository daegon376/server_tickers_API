import requests
import sqlite3
import time

DB_NAME = 'tickers.db'
TABLE_NAME = 'tickers'
UPDATE_PERIOD = 10  # 30
API_URL = 'https://api.blockchain.com/v3/exchange/tickers'


class Ticker:
    all_instances = []

    def __init__(self, ticker_data_list):
        self.symbol = ticker_data_list[0]
        self.price = ticker_data_list[1]
        self.volume = ticker_data_list[2]
        self.last_trade = ticker_data_list[3]
        Ticker.all_instances.append(self)

    @classmethod
    def clear_instances(cls):
        cls.all_instances = []


def get_data_from_api(url):
    response_content = requests.get(url)  # .content
    tickers_list = response_content.json()  # json.loads(response_content)
    for ticker in tickers_list:
        Ticker(list(ticker.values()))


def table_exists(connection):
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'"
    cursor = connection.cursor()
    cursor.execute(query)
    record = cursor.fetchall()
    result = bool(record)
    cursor.close()
    return result


def create_table(connection):
    create_table_query = f'''CREATE TABLE {TABLE_NAME} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                symbol TEXT NOT NULL UNIQUE,
                                price REAL NOT NULL,
                                volume REAL NOT NULL,
                                last_trade REAL NOT NULL
                                );'''

    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()


def first_recording(connection):
    cursor = connection.cursor()
    values = ''
    for i, ticker in enumerate(Ticker.all_instances):
        single_row_values = f"('{ticker.symbol}', {ticker.price}, {ticker.volume}, {ticker.last_trade})"
        if i != (len(Ticker.all_instances) - 1):
            single_row_values += ',\n' + '\t'*3
        values += single_row_values

    query = f'''
            INSERT INTO {TABLE_NAME}
                (symbol, price, volume, last_trade)
            VALUES
                {values};
            '''
    cursor.execute(query)
    connection.commit()
    cursor.close()


def update_recording(connection):
    cursor = connection.cursor()
    for ticker in Ticker.all_instances:
        query = f'''
                UPDATE {TABLE_NAME}
                SET price = {ticker.price},
                    volume = {ticker.volume},
                    last_trade = {ticker.last_trade}
                WHERE
                    symbol = '{ticker.symbol}'
                '''
        cursor.execute(query)
    connection.commit()
    cursor.close()


if __name__ == '__main__':
    try:
        sqlite_connection = sqlite3.connect(DB_NAME)
        get_data_from_api(API_URL)

        if not table_exists(sqlite_connection):
            create_table(sqlite_connection)
            first_recording(sqlite_connection)
            Ticker.clear_instances()
            print('Table created and first recordings are made')

        while True:
            get_data_from_api(API_URL)
            update_recording(sqlite_connection)
            Ticker.clear_instances()
            print('DB updated successfully!')
            time.sleep(UPDATE_PERIOD)

    except sqlite3.Error as error:
        print("SQLite connection error: ", error)

