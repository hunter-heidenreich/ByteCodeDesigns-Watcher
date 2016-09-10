from time import sleep
import requests
from requests.auth import HTTPBasicAuth
import pyrebase
import pickle

STAT = {
    'ORDER_URL': "https://api.theprintful.com/orders",
    'ORDER_COUNT': 0,
    'EXP': 0,
    'SHIRT': 20,
    'TANK': 20,
    'LEGGING': 20,
    'SOCK': 10
}

PRINTFUL_CONFIG = pickle.load(open('api.p', 'rb'))
FIREBASE_CONFIG = pickle.load(open('fb_conf.p', 'rb'))
FIREBASE_LOGIN = pickle.load(open('fb_login.p', 'rb'))


def check_orders():
    global STAT
    data = requests.get(STAT['ORDER_URL'], auth=HTTPBasicAuth(PRINTFUL_CONFIG['user'], PRINTFUL_CONFIG['passw']))
    orderCount = data.json()['paging']['total']
    print("Order count: ", orderCount)
    if STAT['ORDER_COUNT'] < orderCount:
        formatted = data.json()['result']
        unprocessed = orderCount - STAT['ORDER_COUNT']
        for index in range(0, unprocessed):
            if formatted[index]['external_id']:
                proccess_items(formatted[index]['items'])
            STAT['ORDER_COUNT'] += 1
        if unprocessed > 0:
            update_firebase()

    print("EXP", STAT['EXP'])


def proccess_items(items):
    global STAT
    for item in items:
        print(item['name'])
        if 'Shirt' in item['name']:
            print("This is a shirt")
            add_exp(STAT['SHIRT'])
        elif 'Tank' in item['name']:
            print("This is a tank")
            add_exp(STAT['TANK'])
        elif 'Sock' in item['name']:
            print("These are socks")
            add_exp(STAT['SOCK'])
        elif 'Leggings' in item['name']:
            print("These are leggings")
            add_exp(STAT['LEGGING'])


def add_exp(addition):
    global STAT
    STAT['EXP'] += addition


def init_firebase():
    global STAT, USER
    USER = FIREBASE.auth().refresh(USER['refreshToken'])
    db = FIREBASE.database()
    STAT['EXP'] = db.child("EXP").get(USER['idToken']).val()


def update_firebase():
    print("Updated orders.")
    global STAT, USER
    FIREBASE.auth().refresh(USER['refreshToken'])
    db = FIREBASE.database()
    db.update({'EXP': STAT['EXP']}, USER['idToken'])
    write_data()


def load_data():
    global STAT
    data = open('data.txt', 'r')
    STAT['ORDER_COUNT'] = int(data.read())
    data.close()


def write_data():
    text_file = open("data.txt", "w")
    text_file.write("%s" % STAT['ORDER_COUNT'])
    text_file.close()


FIREBASE = pyrebase.initialize_app(FIREBASE_CONFIG)
USER = FIREBASE.auth().sign_in_with_email_and_password(FIREBASE_LOGIN['email'], FIREBASE_LOGIN['password'])
while True:
    load_data()
    init_firebase()
    check_orders()
    sleep(900)
