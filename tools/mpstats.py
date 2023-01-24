from settings.config import *


class MpStats():
    def __init__(self):
        self.token = config['Mpstats']['token']
        self.working = True

    def analyse_sales(self, article, date):
        # Блок рассчета времени
        if type(date) == str:
            date = datetime.datetime.strptime(date,"%Y-%m-%d")

        last = (date - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        past = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if date + datetime.timedelta(days=1) > datetime.datetime.now():
            past = datetime.datetime.now().strftime("%Y-%m-%d")
        response = requests.get(
            f'https://mpstats.io/api/wb/get/item/{article}/sales?d1={last}&d2={past}',
            headers={
                "X-Mpstats-TOKEN": self.token,
                "Content-Type": 'application/json'
            }
        )
        if int(response.status_code) == 200:

            data = response.json()
            sales = list(map(lambda x: x.get('sales'), data))
            mean_sales_last = sum(sales[:5])//5
            sales_after = sum(sales[-2:])//2
            difference = mean_sales_last - sales_after
            return(difference)
        else:
            if int(response.status_code) == 401:
                logging.error('Смените API-токен MpStats: ')
            else:
                logging.error('Код ошибки: ',response.json())
            return(None)
        

if __name__ == "__main__":
    MpStats().analyse_sales('3867317', datetime.datetime(
        year=2020, month=7, day=13, hour=0, minute=0, second=0))