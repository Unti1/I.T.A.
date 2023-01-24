""" Модуль работы с браузерными ссылками"""
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
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from threading import Thread
import urllib.request
import configparser
import traceback
import numpy as np
import pytesseract
import pyspeedtest
import requests
import datetime
import asyncio
import zipfile
import time
import json
import ast
import cv2
import re
import os

############################################

"""Блок библиотек для работы с телеграм"""
# класс для работы с сообщениями
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest
# классы для работы с каналами
from telethon.tl.types import ChannelParticipantsSearch
from telethon.sync import TelegramClient
from telethon import connection




############################################

"""Библиотека для работы с виртуальным номером"""
from smsactivate.api import SMSActivateAPI

"""Библиотеки для работы с google API"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import google.auth

config = configparser.ConfigParser()
config.read(r'.\settings\settings.ini')  # читаем конфиг

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract'

def config_update():
    with open(r'.\settings\settings.ini', 'w') as f:
        config.write(f)

import logging
logging.basicConfig(
    level=logging.INFO,
    filename="logs.log",
    format="%(asctime)s - %(module)s\n[%(levelname)s] %(funcName)s:\n %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    encoding="utf-8"
)
