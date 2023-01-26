""" Модуль работы с браузерными ссылками"""
import logging
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from smsactivate.api import SMSActivateAPI
from telethon import connection
from telethon.sync import TelegramClient
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetParticipantsRequest
import os
import re
import cv2
import ast
import json
import time
import zipfile
import asyncio
import datetime
import requests
import pyspeedtest
import pytesseract
import numpy as np
import traceback
import configparser
import urllib.request
from threading import Thread
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.proxy import Proxy, ProxyType
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium import webdriver
# from seleniumwire import webdriver as webdriverwire
############################################

"""Прочие необходимые библиотеки"""

############################################

"""Блок библиотек для работы с телеграм"""
# класс для работы с сообщениями
# классы для работы с каналами


############################################

"""Библиотека для работы с виртуальным номером"""

"""Библиотеки для работы с google API"""


config = configparser.ConfigParser()
config.read(r'\settings\settings.ini')  # читаем конфиг

# pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract'


def config_update():
    with open(r'\settings\settings.ini', 'w') as f:
        config.write(f)


logging.basicConfig(
    level=logging.INFO,
    filename="logs.log",
    format="%(asctime)s - %(module)s\n[%(levelname)s] %(funcName)s:\n %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    encoding="utf-8"
)
