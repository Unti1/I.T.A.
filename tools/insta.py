from settings.config import *
from tools.google import GoogleService
from tools.mpstats import MpStats
from tools.phone import VirtualNumber
from tools.mailru import mailru_mail


class InstPars(Thread):
    def __init__(self, PROFILE_DATA: str = "", invisable=False, google_services: GoogleService = None,checking = False) -> None:
        super(InstPars, self).__init__()
        
        # Эмулятор
        self.browser_startUp(PROFILE_DATA[3],invisable = invisable)
        self.action = ActionChains(self.driver)
        self.profile_data = PROFILE_DATA
        
        # Переменные
        self.status_of_working: bool = True
        self.LOGIN: str = PROFILE_DATA[0].split(":")[0]
        self.PASSWORD: str = PROFILE_DATA[0].split(":")[1]
        # Сторонние классы
        self.google_services: GoogleService = google_services
        # self.phone = VirtualNumber()
        self.mpstats = MpStats()

        # Инициализация потока
        self.status = {
            'auth': "Не авторизован",
            'publish': "Ещё не запущен",
            'realse': "Ещё не запущен",
            'stories': "Ещё не запущен",
            'guard': "Не заблокирован",
            'actions': "0",

        }
        self.profile_data = PROFILE_DATA
        self.mail = mailru_mail(self.driver)
        self.used_actions = 0
        self.running = True
        self.checking = checking
        self.check_this_pages = []  # сюда передаются объекты телеграмм
        self.total_len_check = len(self.check_this_pages)
        self.checked_pages = {}

    def browser_startUp(self, PROFILE_ID,invisable):
        """Создание настройка и создания эмуляции браузера
        """
        # Настройка браузера Google
        chrome_drive_path = Service('./chromedriver.exe')
        options = webdriver.ChromeOptions()
        reg_url = f'http://localhost:3001/v1.0/browser_profiles/{PROFILE_ID}/start?automation=1'
        response = requests.get(reg_url)
        respons_json = response.json()
        PORT = str(respons_json['automation']['port'])
        options.debugger_address = '127.0.0.1:'+ PORT
        options.add_argument("window-size=1600,900")
        # Доп. параметры
        options.add_argument('--disable-logging')
        options.add_argument('--ignore-error')
        if invisable:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        # serv = Service(ChromeDriverManager().install())
        # Запуск эмулятора браузера
        # self.driver: webdriver.Chrome = webdriver.Chrome(
            # service=serv, options=options)
        self.driver = webdriver.Chrome(service=chrome_drive_path,chrome_options=options)

    def __publishes_text_collect(self, publish):
        self.__acception_challange(publish)
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//ul/div/li/div/div/div[2]/div[1]/span")))
            time.sleep(0.5)
            post_el = self.driver.find_element(
                By.XPATH, "//ul/div/li/div/div/div[2]/div[1]/span")
            date = self.driver.find_element(
                By.XPATH, '//ul/div/li/div/div/div[2]/div[2]/div/time').get_attribute("datetime").split('.')[0]
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            return (post_el.text, date)
        except:
            return ("")

    def __article_grab(self, text):
        self.status['publish'] = 'Анализирую артикли'
        date = text[1]
        text = text[0]
        m = re.search(
            r"(?:wlb|wb|wildberries|вб|влб|вайлберис|вайлдберис|артикул|арт)", text.lower())
        if m:
            m = re.findall(r"(?:\d{6,})", text)
            if m:
                if len(m) > 1:
                    return ([[art, date] for art in m])
                else:
                    return ([m[0], date])

    def mpstats_analize_profile(self, user_url='', cost='',articuls = [],recheck = False):
        try:
            if articuls == []:
                articuls = self.checked_pages[user_url]
            else:
                pass

            if articuls != []:
                means_lst = []
                for art, date in articuls:
                    if art != None:
                        mean = self.mpstats.analyse_sales(art, date)
                        means_lst.append(mean)
                means_lst = list(filter(lambda x: x != None, means_lst))
                try:
                    mean_from_means = sum(means_lst)//len(means_lst)
                except ZeroDivisionError:
                    mean_from_means = 0

                if not recheck:
                    transform_data = list(map(lambda x: [x[0],x[1].strftime('%Y-%m-%d')],self.checked_pages[user_url]))
                    d = [user_url, cost, mean_from_means,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),str(transform_data)]
                else:
                    transform_data = list(map(lambda x: [x[0],x[1]],articuls))
                    d = [user_url, cost, mean_from_means,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),str(transform_data)]
                self.google_services.append_db(d)
        except Exception as e:
            logging.error(traceback.format_exc())

    def all_profile_collect(self, page):
        logging.info(f"{self.name} >>>> {page}")
        try:
            pub = self.all_publish_collect(page)
        except Exception as e:
            logging.error(traceback.format_exc())
            pub = []
        try:
            rls = self.realse_collect(page)
        except Exception as e:
            logging.error(traceback.format_exc())
            rls = []
        try:
            sto = self.all_story_collect(page)
        except Exception as e:
            logging.error(traceback.format_exc())
            sto = []
        pub.extend(sto)
        pub.extend(rls)
        self.update_insta_acc_table()
        return (pub)

    def all_publish_collect(self, page):
        """Сбор всех публикаций"""
        self.status['publish'] = 'В процессе сбора постов'
        self.__acception_challange(page) # проверка ошибок
        publish_links = [] # Все собранные ссылки
        max_pub = int(config["Instagram"]["max_publishes"])
        Y = 1000
        last_len = len(publish_links) # Последняя полученная длина
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//article//a[@role="link"]')))

        while len(publish_links) < max_pub:
            publish_links = list(map(lambda x: x.get_attribute(
                "href"), self.driver.find_elements(By.XPATH, '//article//a[@role="link"]')))
            self.used_actions += len(publish_links)
            self.driver.execute_script(f"window.scrollTo(0, {Y})")
            if len(publish_links) == last_len:#Если собранная длина равна прошлой => постов больше нет
                logging.info(f"Завершение сбора ссылок на публикации {last_len}было {len(publish_links)}стало")
                break
            last_len = len(publish_links)
            Y += 1000

        if len(publish_links) != max_pub:
            publish_links = publish_links[:max_pub]

        pub_textes = list(
            map(lambda pub: self.__publishes_text_collect(pub), publish_links))
        articles = list(
            map(lambda text: self.__article_grab(text), pub_textes))
        articles = list(filter(lambda x: x != None, articles))
        for i in range(len(articles)):
            try:
                articles[i][2]
                d = articles.pop(i)
                for val in d:
                    articles.append(val)
            except:
                pass
        self.status['publish'] = f'Получено {len(articles)} артиклей'
        return (articles)

    def all_story_collect(self, page):
        if bool(config['Instagram']['story_look']):
            return []

        self.status['story'] = 'В процессе'
        self.__acception_challange(page)
        all_articles = []
        # self.driver.get(page)
        WebDriverWait(self.driver, 15, ignored_exceptions=exceptions.StaleElementReferenceException).until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@role="presentation"]/div/ul/li[@class]')))
        time.sleep(int(config["Instagram"]["preload_timeout"]))
        stories_el = self.driver.find_elements(
            By.XPATH, '//div[@role="presentation"]/div/ul/li[@class]')  # сперва собираем количество историй
        for num in range(len(stories_el)):  # Начинаем проход по каждому
            try:
                WebDriverWait(self.driver, 15, ignored_exceptions=exceptions.StaleElementReferenceException).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@role="presentation"]/div/ul/li[@class]')))
                if num >= 6:
                    cnt = (num+1)//7
                    for c in range(cnt):
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                            (By.XPATH, '//button[@aria-label="Далее"]')))
                        time.sleep(1.5)
                        self.driver.find_element(
                            By.XPATH, '//button[@aria-label="Далее"]').click()
                time.sleep(1.5)
                story = self.driver.find_elements(
                    By.XPATH, '//div[@role="presentation"]/div/ul/li[@class]')[num]
                story.click()
                # print("История номер ", num)
                all_articles.extend(self.__grab_stories())
            except Exception as e:
                logging.ERROR(traceback.format_exc())
            self.driver.get(page)
        self.status['story'] = f"Собрано {len(all_articles)} артиклей"
        return (all_articles)

    def realse_collect(self, page):
        try:
            self.__acception_challange(page)
            self.status['realse'] = "В процессе сбора"
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(
                (By.XPATH, '//section/main/div/header/div/div[@aria-disabled="false"]')))
            time.sleep(float(config['Instagram']['preload_timeout']))
            self.driver.find_element(
                By.XPATH, '//section/main/div/header/div/div[@aria-disabled="false"]').click()
            rls = self.__grab_stories(limit=False)
            self.status['realse'] = f"Получено {len(rls)} артиклей"
            return (rls)
        except Exception as e:
            logging.error(traceback.format_exc())
            return []

    def __grab_stories(self, limit=True):
        article_list = []
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//section//header//button[@aria-label]')))
        time.sleep(int(config["Instagram"]["story_timeout"]))
        stories = self.driver.find_elements(By.XPATH, '//header/div[1]/div')
        story_len = len(stories) #длина всех историй
        self.used_actions += story_len
        # print(f'>Длина истории {story_len}')
        origin_window = self.driver.current_window_handle
        for _ in range(story_len):
            # print("Подистория ", _)
            # Остановка текущей истории
            try:
                WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(EC.element_to_be_clickable(
                    (By.XPATH, '//section//div[@aria-label]//div[@role="button"]')))
                self.action.key_down(Keys.SPACE).perform()
                but = self.driver.find_element(
                    By.XPATH, '//section//div[@aria-label]//div[@role="button"]')
                self.driver.execute_script("arguments[0].click();", but)
                WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(EC.element_to_be_clickable(
                    (By.XPATH, '//section//div[@aria-label]//div[@role="dialog"]')))
                dialog = self.driver.find_element(
                    By.XPATH, '//section//div[@aria-label]//div[@role="dialog"]')
                self.driver.execute_script("arguments[0].click();", dialog)
                try:
                    WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(
                        EC.number_of_windows_to_be(2))
                    ww = 0
                    while "instagram" in self.driver.current_url and ww < 10:
                        self.driver.switch_to.window(
                            self.driver.window_handles[-1])
                        ww += 0.2
                        time.sleep(0.2)
                    article = re.search(r"\d{5,}", self.driver.current_url)[
                        0] if "wildberries" in self.driver.current_url else None
                    time.sleep(0.5)
                    self.driver.close()
                    self.driver.switch_to.window(origin_window)
                    WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(
                        EC.element_to_be_clickable((By.XPATH, '//header//time')))
                    date = self.driver.find_element(
                        By.XPATH, '//header//time').get_attribute("datetime").split('.')[0]
                    date = datetime.datetime.strptime(
                        date, '%Y-%m-%dT%H:%M:%S')
                    article_list.append([article, date])
                    self.action.key_down(Keys.ARROW_RIGHT).perform()
                except Exception as e:
                    logging.info(e)
                    try:
                        WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(
                            EC.number_of_windows_to_be(2))
                        self.driver.close()
                    except:
                        self.driver.back()
                    self.driver.switch_to.window(origin_window)
                    time.sleep(1.5)
                    WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(EC.element_to_be_clickable(
                        (By.XPATH, '//section//div[@aria-label]//div[@role="button"]')))
                    self.action.key_down(Keys.ARROW_RIGHT).perform()
            except (exceptions.TimeoutException or exceptions.NoSuchElementException):
                logging.info("Наклейки нет, опознаю машинным зрением")
                self.driver.switch_to.window(origin_window)
                try:
                    WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, '//video')))
                    self.action.key_down(Keys.SPACE).perform()
                    video_el = self.driver.find_element(By.XPATH, '//video')
                    video_url = video_el.get_attribute('src')
                    WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(
                        EC.element_to_be_clickable((By.XPATH, '//header//time')))
                    date = self.driver.find_element(
                        By.XPATH, '//header//time').get_attribute("datetime").split('.')[0]
                    date = datetime.datetime.strptime(
                        date, '%Y-%m-%dT%H:%M:%S')
                    article = self.__article_from_story(
                        video_url, mode="video")
                except:
                    try:
                        photo_el = self.driver.find_element(
                            By.XPATH, '//header//img')
                        WebDriverWait(self.driver, float(config["Instagram"]["widget_wait_time"])).until(
                            EC.element_to_be_clickable((By.XPATH, '//header//time')))
                        date = self.driver.find_element(
                            By.XPATH, '//header//time').get_attribute("datetime").split('.')[0]
                        date = datetime.datetime.strptime(
                            date, '%Y-%m-%dT%H:%M:%S')
                        photo_url = photo_el.get_attribute('src')
                        article = self.__article_from_story(
                            photo_url, mode="img")
                    except:
                        logging.error(traceback.format_exc)

                if article != None:
                    article_list.append([article, date])
                    # print(article, date)
                # else:
                    # print("Артикул не найден")
                # Переход к следующей истории
                self.action.key_down(Keys.ARROW_RIGHT).perform()
            except Exception as e:
                print("Ошибка при сборе")
                logging.error(traceback.format_exc())
            if limit:
                if _ >= int(config["Instagram"]["total_story_without_article"]) and len(article_list) == 0:
                    break
        return (article_list)

    def __article_from_story(self, url, mode):
        match mode:
            case 'video':
                video_path = f'timeless_data/story_{self.name}.mp4'
                urllib.request.urlretrieve(url, video_path)
                vidcap = cv2.VideoCapture(video_path)
                success, image = vidcap.read()

                gry1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thr1 = cv2.threshold(
                    gry1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                text = pytesseract.image_to_string(
                    thr1, config="--psm 12 digits")
                artic = re.search("\d{6,}", text)
                if artic != None:
                    artic = artic[0]
                vidcap.release()
                # if os.path.isfile(video_path):
                #     os.remove(video_path)
            case 'img':
                img_data = requests.get(url).content
                img_path = f'timeless_data/story_{self.name}.png'
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                image = cv2.imread(img_path)
                gry1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thr1 = cv2.threshold(
                    gry1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                text = pytesseract.image_to_string(
                    thr1, config="--psm 12 digits")
                artic = re.search("\d{6,}", text)
                if artic != None:
                    artic = artic[0]
            case _:
                artic = None
                print("Mode wasn't selected")

        return (artic)

    def __login(self):
        """Логининг при первом входе"""
        self.driver.get("https://instagram.com")
        try:
            self.status['auth'] = "Попытка авторизации"
            try:
                time.sleep(2)
                allow_cookie = self.driver.find_elements(By.XPATH,'//div[role="dialog"]//button')[-1]
                allow_cookie.click()
            except:
                pass
            WebDriverWait(self.driver, int(config['Instagram']['logining_wait'])).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@name="username"]')))
            login = self.driver.find_element(
                By.XPATH, '//input[@name="username"]')
            psw = self.driver.find_element(
                By.XPATH, '//input[@name="password"]')
            login.send_keys(self.LOGIN)
            psw.send_keys(self.PASSWORD)
            btn = self.driver.find_elements(By.XPATH, '//button')[1]
            btn.click()
            time.sleep(2)
            if "csrf token missing or incorrect" in self.driver.page_source.lower():
                self.driver.execute_script(
                    "n=new Date;t=n.getTime();et=t+36E9;n.setTime(et);document.cookie='csrftoken='+document.body.innerHTML.split('csrf_token')[1].split('\\\"')[2]+';path=\;domain=.instagram.com;expires='+n.toUTCString();")
                self.driver.refresh()
                WebDriverWait(self.driver, int(config['Instagram']['logining_wait'])).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@name="username"]')))
                login = self.driver.find_element(
                    By.XPATH, '//input[@name="username"]')
                psw = self.driver.find_element(
                    By.XPATH, '//input[@name="password"]')
                login.send_keys(self.LOGIN)
                psw.send_keys(self.PASSWORD)
                btn = self.driver.find_elements(By.XPATH, '//button')[1]
                btn.click()
                
            ######### Проверка челленджей #######
            self.__acception_challange()

            ######### Этап сохранения браузера для автологининга #########
            # try:
            #     WebDriverWait(self.driver, int(config['Instagram']['logining_wait'])).until(
            #         EC.element_to_be_clickable((By.XPATH, '//section')))
            #     if "cохранить данные для входа?" in self.driver.page_source.lower():
            #         access_btn = self.driver.find_elements(
            #             By.XPATH, "//button")[0]
            #         access_btn.click()
            # except Exception as e:
            #     pass
        except exceptions.TimeoutException as e:
            self.status['auth'] = "Авторизирован"
            # logging.info("Авторизован")
            logging.info(traceback.format_exc())
            # print("Профиль уже авторизирован")
        except:
            logging.info(traceback.format_exc())

    def __acception_challange(self, page="https://instagram.com"):
        """Модуль обхода блокировки """
        chose_method = None  # принимает "mail"
        while "challenge" in self.driver.current_url:
            self.status['guard'] = 'Обход заморозки'
            if "что вы владелец этого аккаунта" in self.driver.page_source.lower():
                self.status['guard'] = 'Выбор метода получения кода'
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]')))
                    all_buttons = self.driver.find_elements(
                        By.XPATH, '//div[@role="button"]')

                    for but in all_buttons:
                        if "адрес" in but.text.lower():
                            but.click()
                            chose_method = "mail"
                            break
                    all_buttons[-1].click()  # обычно последняя кнопка это вход

                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//input')))
                    match chose_method:
                        case "mail":
                            self.status['guard'] = 'Ожидание кода на почте'
                            code = self.mail.mail_check()
                            btns = self.driver.find_elements(
                                By.XPATH, '//div[@role="button"]')
                            if code == "":
                                for btn in btns:
                                    if "новый код" in btn.text.lower():
                                        btn.click()
                                        break
                                continue
                            else:
                                self.driver.find_element(
                                    By.XPATH, '//input').send_keys(code)
                                for btn in btns:
                                    if "подтвердить" in btn.text.lower():
                                        btn.click()
                                        break
                except:
                    pass
            elif "верна ли информация вашего профиля" in self.driver.page_source.lower():
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]')))
                for but in self.driver.find_elements(By.XPATH, '//div[@role="button"]'):
                    if 'да' in but.text.lower():
                        but.click()
            else:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//input')))
                    if 'адрес' in self.driver.page_source.lower():
                        chose_method = 'mail'

                    match chose_method:
                        case "mail":
                            code = self.mail.mail_check()
                            if code == "":
                                continue
                            else:
                                self.driver.find_element(
                                    By.XPATH, '//input').send_keys(code)
                                self.driver.find_element(
                                    By.XPATH, '//div[@role="button"]').click()
                except:
                    pass
        else:
            self.status['guard'] = 'Не заблокирован'
            return (self.driver.get(page))

    def test_pub(self):
        self.__login()
        try:
            print(self.all_publish_collect("https://instagram.com/nastya_pro_wb"))
        except:
            logging.error(traceback.format_exc())

    def test_stories(self):
        try:
            self.__login()
            s = self.realse_collect("https://instagram.com/nastya_pro_wb")
        except:
            logging.error(traceback.format_exc())
    
    def always_rechecking_by_time(self):
        while self.running:
            table_data = self.google_services.get_all_values_db()
            for dat in table_data:
                dtime,articuls = datetime.datetime.strptime(dat[-2],"%Y-%m-%d %H:%M:%S")\
                                ,ast.literal_eval(dat[-1])
                # Узнаем время из даты 
                if dtime + datetime.timedelta(hours=12) <= datetime.datetime.now():
                    self.mpstats_analize_profile(dat[0],dat[1],articuls,recheck=True)
            time.sleep(3600)
        pass
    
    def update_insta_acc_table(self):
        self.profile_data[1] = f"{self.used_actions}"
        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.profile_data[2] = f"{time_now}"
        self.google_services.instagram_update_values(self.profile_data[0],self.profile_data)

    def run(self):
        self.__login()
        while self.running and self.used_actions <= int(config["Instagram"]["total_actions"]):
            if self.checking:
                try:
                    self.always_rechecking_by_time()
                except:
                    logging.error(traceback.format_exc())
            else:
                try:
                    if len(self.check_this_pages) != 0:
                        if len(self.check_this_pages) > self.total_len_check:
                            self.total_len_check = len(self.check_this_pages)
                        data = self.check_this_pages.pop()
                        user_url = data[0]
                        logging.info(user_url)
                        if user_url in self.checked_pages.keys():
                            continue

                        cost = data[1]
                        self.status['publish'] = "Ещё не запущен"
                        self.status['realse'] = "Ещё не запущен"
                        self.status['publish'] = "Ещё не запущен"
                        self.status['guard'] = "Не заблокирован"
                        self.status['actions'] = f"{self.used_actions}"
                        while self.mpstats.working != True:
                            self.status['guard'] = 'Смените API-токен MpStats'
                            time.sleep(5)
                        self.checked_pages[user_url] = self.all_profile_collect(
                            user_url)
                        self.mpstats_analize_profile(user_url, cost)
                    else:
                        time.sleep(5)
                except:
                    self.update_insta_acc_table()
                    self.running = False
                    self.driver.quit()
        else:
            try:
                self.update_insta_acc_table()
                for i in range(len(self.driver.window_handles)):
                    self.driver.close()
            except Exception as e:
                logging.info(e)
                    

if __name__ == "__main__":
    googl = GoogleService()
    i = InstPars(LOGIN="instaparstable@gmail.com",
                 PASSWORD="Qweasdzxc123!", google_services=googl)
    i.check_this_pages.append(("https://instagram.com/nastya_pro_wb", 5000))
    # i.run()
    print("Тестирование историй")
    i.test_stories()
    print("Тестирование постов")
    i.test_pub()
    i.running = False
    googl.running = False
