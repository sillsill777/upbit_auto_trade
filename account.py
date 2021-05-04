from pyupbit import Upbit
f = open('keys.txt', 'r')
info = f.readlines()
AccessKey = info[0].split(' ')[0]
SecretKey = info[1].split(' ')[0]


def return_account():
    return Upbit(AccessKey, SecretKey)

