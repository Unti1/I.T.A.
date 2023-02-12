#Visual Studio
#Py
#Установить модули Selenium, reguests, time

# импорт модулей
from selenium import webdriver #модуль Selenium драйвера
from selenium.webdriver.chrome.service import Service #модуль Selenium драйвера
import requests
import time

profile_id = '50592901'	 #профиль в Dolphin-Anty

reg_url = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'

response = requests.get(reg_url)
print(response)

respons_json = response.json()
print(respons_json)
port = str(respons_json['automation']['port'])
print(port) 

# #инициализируем вебдрайвер Долфин Анти
chrome_drive_path = Service('chromedriver.exe')
options = webdriver.ChromeOptions()
options.debugger_address = '127.0.0.1:'+port

driver = webdriver.Chrome(service=chrome_drive_path,chrome_options=options)