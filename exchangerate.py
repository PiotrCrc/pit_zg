import pandas as pd
import datetime as dt
import re

class ExchangeRates:
    def __init__(self):
        self.df = None
        self.read_csv_kwargs = {"sep": ";", "skiprows": [1], "skipfooter": 3, "decimal": ",",
                                "index_col": 0, "parse_dates": True, "encoding": "cp1250"}

    def get_data(self, years, path):
        data = []
        for i, year in enumerate(years):
            assert (2012 <= year <= dt.date.today().year), "Year not in range"
            data.append(pd.read_csv(path + str(int(year)) + ".csv", **self.read_csv_kwargs))
        self.df = pd.concat(data)
        self.df = self.df.iloc[:, :-3]  # usunięcie 3 ostatnich kolumn
        print(self.df)

    def download_data(self, years: list, url="https://static.nbp.pl/dane/kursy/archiwum/archiwum_tab_a_"):
        self.get_data(years, url)

    def open_data(self, years: list, path="data/archiwum_tab_a_"):
        self.get_data(years, path)

    def all_rates_at_date(self, date):
        assert self.df is not None, "no dataframe available"
        return self.df.loc[date.strftime("%Y-%m-%d")]

    def rate_at_date(self, date, currency):
        rates = self.all_rates_at_date(date)
        return rates[currency] ### re.match(r"(?<=1)[A-Z]{3}$","1USD").group(0)

    # def get_previous_date_rate(self, rate_date):
    #     if (len(self.list_of_rates) > 1):
    #         self.list_of_rates.sort(key=lambda x: x.rate_date)
    #     previous_date_rate = 0
    #     for rate_at_date in self.list_of_rates:
    #         if (rate_at_date.rate_date >= rate_date):
    #             # print("0",rate_at_date.rate_date, previous_date_rate)
    #             if (previous_date_rate != 0):
    #
    #                 return previous_date_rate
    #             else:
    #                 sys.exit("rate " + str(rate_date) + " don't exist in csv")
    #                 return "rate not available"
    #
    #         else:
    #             previous_date_rate = rate_at_date.rate
    #             # print("1",rate_at_date.rate_date, previous_date_rate)


if __name__ == "__main__":
    e_r = ExchangeRates()
    e_r.open_data([2023])
    e_r.rate_at_date(dt.date(2023, 2, 8), "1USD")
    #
    # class RateAtDate:
    #     rate_date: datetime.date
    #     rate: float
    #
    #     def __init__(self, rate_date, rate):
    #         self.rate = rate
    #         self.rate_date = rate_date
    #
    #     def __repr__(self):
    #         return self.rate_date.strftime("%Y %m %d") + " " + str(self.rate)
