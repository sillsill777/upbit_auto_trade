import pyupbit
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import os

buy_log = open("purchase_log.txt", "w")
sell_log = open("sell_log.txt", "w")
buy_log.close()
sell_log.close()
writer = pd.ExcelWriter("./CoinData.xlsx")


class Coin:
    def __init__(self, name):
        self.name = name.split("-")[1]
        self.trade_name = name
        self.bought = False
        self.after_5 = False
        self.is_sell = False
        self.amount = 0
        self.purchase = 0
        self.price = 0
        self.sell = 0
        self.ratio = 0
        self.max_ratio = 1
        self.purchasetime = datetime.datetime.now()
        self.df = pd.DataFrame()

    def initialize(self):
        self.bought = False
        self.after_5 = False
        self.is_sell = False
        self.purchase = 0
        self.ratio = 0
        self.max_ratio = 1

    def init_df(self):
        self.df = pd.DataFrame([[self.purchase,self.price,self.ratio,self.max_ratio,self.is_sell,self.sell]],
            index=[self.purchasetime.strftime("%Y/%m/%d_%H:%M:%S")],
                               columns=['purchase','cur_price','ratio','max_ratio','is_sell','sell_price'])

    def update_df(self, cur_time):
        self.df.loc[cur_time] = pd.Series([self.purchase,self.price,self.ratio,self.max_ratio,self.is_sell,self.sell],
                            index=['purchase', 'cur_price', 'ratio', 'max_ratio', 'is_sell', 'sell_price'] )

    def toExcel(self, writer):
        self.df.to_excel(writer, sheet_name=self.name)
        writer.save()

    def print(self, f):
        f.write("-"*50)
        f.write("\n   name: {}        purchase_time: {}\n".format(self.name, self.purchasetime))
        if self.is_sell:
            f.write("     purchase_price: {}      sell_price: {}      ratio: {}\n".format(self.purchase,
                                                                                        self.sell,self.ratio))
        else:
            f.write("     purchase_price: {}      current_price: {}       ratio: {}     max_ratio:{} \n".format
                    (self.purchase, self.price, self.price/self.purchase, self.max_ratio))
        f.write("\n\n")

    def print_screen(self):
        print("-"*60)
        print("\n   name: {}        purchase_time: {}\n".format(self.name, self.purchasetime))
        if self.is_sell:
            print("     purchase_price: {}      sell_price: {}      ratio: {}\n".format(self.purchase,
                                                                                        self.sell,self.ratio))
        else:
            print("     purchase_price: {}      current_price: {}       ratio: {}\n".format(self.purchase,
                                                                                self.price, self.price/self.purchase))
        print("\n\n")


coin_list = pyupbit.get_tickers(fiat="KRW")
coins = {}
purchased_coin = {}
for item in coin_list:
    coins[item] = Coin(item)
"""
 coins["KRW-BTC"]와 같이 코인 접근 가능, coins["KRW-BTC"].name
"""

current_time = datetime.datetime.now()
delta30 = datetime.timedelta(seconds=30)
delta_1min = datetime.timedelta(minutes=1)
target_time = current_time + delta_1min
delta1 = datetime.timedelta(seconds=1)
delta_5min = datetime.timedelta(minutes=5)
target_purchased_coin_time = current_time + delta_5min

total_coin_num = len(coin_list)
get_price_iter = int(total_coin_num/100)
def get_cur_price():
    if total_coin_num <= 100:
        price_dicc = pyupbit.get_current_price(coin_list[:total_coin_num])
    else:
        price_dicc = pyupbit.get_current_price(coin_list[:100])
        price_dicc.update(pyupbit.get_current_price(coin_list[100:total_coin_num]))
    return price_dicc


coin_df = pd.DataFrame(list(get_cur_price().items()))
coin_df.set_index([0], inplace=True)
coin_df.rename({1: "prev1"}, axis=1, inplace=True)
time.sleep(60)
price_dic = get_cur_price()
coin_df['prev2'] = pd.DataFrame(price_dic.values(), index=price_dic.keys())
time.sleep(60)
price_dic = get_cur_price()
coin_df['prev3'] = pd.DataFrame(price_dic.values(), index=price_dic.keys())
time.sleep(60)
price_dic = get_cur_price()
coin_df['prev4'] = pd.DataFrame(price_dic.values(), index=price_dic.keys())
print(coin_df)
threshHold = 1.01
threshHold2 = 1.002
while True:
    try:
        current_time = datetime.datetime.now()
        if (current_time >= (target_time-delta1)) & (current_time <= (target_time+delta1)):
            price_dic = get_cur_price()
            current_time = datetime.datetime.now()
            target_time = current_time + delta_1min
            coin_df['cur'] = pd.DataFrame(price_dic.values(), index=price_dic.keys())
            coin_df['ratio1'] = (coin_df['prev2']/coin_df['prev1']) > threshHold
            coin_df['ratio2'] = (coin_df['prev3']/coin_df['prev2']) > threshHold2
            coin_df['ratio3'] = (coin_df['prev4']/coin_df['prev3']) > threshHold2
            coin_df['ratio4'] = (coin_df['cur'] / coin_df['prev4']) > threshHold2

            coin_df['target'] = coin_df['ratio1'] & ((coin_df['ratio2']*1 + coin_df['ratio3']*1 + coin_df['ratio4']*1)>=2)
            purchase_df = coin_df[coin_df['target']]
            coin_df['prev1'] = coin_df['prev2']
            coin_df['prev2'] = coin_df['prev3']
            coin_df['prev3'] = coin_df['prev4']
            coin_df['prev4'] = coin_df['cur']
            if not purchase_df.empty:
                print("-"*40)
                print(purchase_df)
                print("-"*40)
                for check_pur in list(purchase_df.index):
                    buy_log = open("purchase_log.txt", "a")
                    if not(check_pur in purchased_coin):
                        '''
                        buy coin
                        '''
                        coins[check_pur].bought = True
                        coins[check_pur].purchasetime = current_time
                        coins[check_pur].purchase = purchase_df.loc[check_pur, 'cur']
                        coins[check_pur].price = coins[check_pur].purchase
                        coins[check_pur].print(buy_log)
                        coins[check_pur].print_screen()
                        coins[check_pur].init_df()
                        coins[check_pur].toExcel(writer)
                        purchased_coin[check_pur] = coins[check_pur]
                    buy_log.close()

        list_of_purchased_coin = list(purchased_coin.keys())
        if len(list_of_purchased_coin) != 0:
            price_dic = pyupbit.get_current_price(list_of_purchased_coin)
        list_to_del = []
        if (current_time >= (target_purchased_coin_time - delta1)) & (
                current_time <= (target_purchased_coin_time + delta1)):
            target_purchased_coin_time = current_time + delta_5min
            curr_time = current_time.strftime("%Y/%m/%d_%H:%M:%S")
            for name, check_price in purchased_coin.items():
                check_price.update_df(curr_time)
                check_price.toExcel(writer)
        for name, check_price in purchased_coin.items():
            check_price.price = price_dic[name]
            check_price.ratio = check_price.price/check_price.purchase
            check_price.max_ratio = max(check_price.max_ratio, check_price.ratio)

            if (current_time - check_price.purchasetime) > delta_5min:
                check_price.after_5 = True
            if check_price.after_5:
                if (check_price.max_ratio > 1) & (check_price.ratio < ((check_price.max_ratio-1)/2 + 1)):
                    '''
                    coin sell
                    '''
                    sell_log = open("sell_log.txt", "a")
                    check_price.is_sell = True
                    check_price.sell = pyupbit.get_current_price(name)
                    check_price.print(sell_log)
                    check_price.update_df(current_time.strftime("%Y/%m/%d_%H:%M:%S"))
                    check_price.toExcel(writer)
                    print("="*60)
                    print("Sell")
                    print("="*60)
                    check_price.print_screen()
                    check_price.initialize()
                    list_to_del.append(name)
                    sell_log.close()
        for name in list_to_del:
            purchased_coin.pop(name)
        time.sleep(0.5)
    except Exception as e:
        print(e)
        time.sleep(0.5)



