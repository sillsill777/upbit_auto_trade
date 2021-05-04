import pyupbit
import pandas as pd
import datetime
import time


def get_data(ticker, interval, end_time, total_day):
    print("Loading Data...")
    minute = int(interval.split('e')[1])
    total_min = total_day*24*60
    count = int(total_min/minute)
    itr = int(count/200)
    if count <= 200:
        return pyupbit.get_ohlcv(ticker, interval=interval, count=count, to=end_time)

    df = pyupbit.get_ohlcv(ticker, interval=interval, to=end_time)
    for i in range(itr):
        print("{0:0.1f}% done".format((i+1)/itr*100))
        count = count-200
        end_time = end_time-datetime.timedelta(minutes=minute*200)
        if count >= 200:
            counts = 200
        else:
            counts = count

        df_add = pyupbit.get_ohlcv(ticker, interval=interval, to=end_time, count=counts)
        df = pd.concat([df_add, df])
        time.sleep(0.2)
    print("Loading Complete\n")
    return df


if __name__ == "__main__":
    df = get_data("KRW-BTC", "minute1", datetime.datetime.now(), 3)
    print(df)


