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


def checkOrders():
    global STAT
    data = requests.get(STAT['ORDER_URL'], auth=HTTPBasicAuth(PRINTFUL_CONFIG['user'], PRINTFUL_CONFIG['passw']))
    orderCount = data.json()['paging']['total']
    print("Order count: ", orderCount)
    if STAT['ORDER_COUNT'] < orderCount:
        formatted = data.json()['result']
        unprocessed = orderCount - STAT['ORDER_COUNT']
        for index in range(0, unprocessed):
            if formatted[index]['external_id']:
                processItems(formatted[index]['items'])
            STAT['ORDER_COUNT'] += 1
        if unprocessed > 0:
            updateFirebase()

    print("EXP", STAT['EXP'])

def processItems(items):
    global STAT
    for item in items:
        print(item['name'])
        if 'Shirt' in item['name']:
            print("This is a shirt")
            addExp(STAT['SHIRT'])
        elif 'Tank' in item['name']:
            print("This is a tank")
            addExp(STAT['TANK'])
        elif 'Sock' in item['name']:
            print("These are socks")
            addExp(STAT['SOCK'])
        elif 'Leggings' in item['name']:
            print("These are leggings")
            addExp(STAT['LEGGING'])

def addExp(addition):
    global STAT
    STAT['EXP'] += addition

def initFirebase():
    global STAT, USER
    USER = FIREBASE.auth().refresh(USER['refreshToken'])
    db = FIREBASE.database()
    STAT['EXP'] = db.child("EXP").get(USER['idToken']).val()

def updateFirebase():
    print("Updated orders.")
    global STAT, USER
    FIREBASE.auth().refresh(USER['refreshToken'])
    db = FIREBASE.database()
    db.update({'EXP': STAT['EXP']}, USER['idToken'])
    writeData()

def loadData():
    global STAT
    data = open('data.txt', 'r')
    STAT['ORDER_COUNT'] = int(data.read())
    data.close()

def writeData():
    text_file = open("data.txt", "w")
    text_file.write("%s" % STAT['ORDER_COUNT'])
    text_file.close()


FIREBASE = pyrebase.initialize_app(FIREBASE_CONFIG)
USER = FIREBASE.auth().sign_in_with_email_and_password(FIREBASE_LOGIN['email'], FIREBASE_LOGIN['password'])
while True:
    loadData()
    initFirebase()
    checkOrders()
    sleep(900)
