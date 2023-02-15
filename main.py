from settings.config import *
from tools.google import GoogleService
from tools.mpstats import MpStats
from tools.insta import InstPars
from tools.tele import TelegramPars

class Monitor(Thread):
    def __inti__(self):
        self.main_class = None

    def monitoring_screen(self):
        while self.main_class.MainTreeProcesses[0].running:
            try:
                self.main_class.google_monitor(self.main_class.MainTreeProcesses[0])
                self.main_class.tele_monitor(self.main_class.MainTreeProcesses[1])
                for proc in self.main_class.MainTreeProcesses[2:]:
                    self.main_class.inst_monitor(proc)
                time.sleep(3)
                os.system("clear")
            except:
                logging.info(f"Ошибка отображения {traceback.format_exc()}")
        else:
            time.sleep(10)

    def run(self):
        self.monitoring_screen()

class Main():
    def __init__(self):
        self.running = True
        self.MainTreeProcesses = []
        
    def general_start(self):
        """TODO: Проверить"""
        cpu_counts = os.cpu_count()
        self.MainTreeProcesses = []
        '''
        0 - Google Service
        1 - Telegram
        2+ - InstPars
        -1 - InstPars(перепроверка)
        '''
        # Добоавляем потоки
        self.MainTreeProcesses.append(GoogleService())
        self.MainTreeProcesses.append(TelegramPars(
            google_service=self.MainTreeProcesses[0]))
        self.MainTreeProcesses[0].start() # Запуск гугл модуля
        self.MainTreeProcesses[1] # Собираем данные о пользователей

    
        
        Instagram_Accounts = self.MainTreeProcesses[0].instagram_accounts() # Получаем "сырые" аккаунт
        Instagram_Accounts = list(filter(lambda x: self.MainTreeProcesses[0].check_account_limit(x),Instagram_Accounts))
        if len(Instagram_Accounts) < cpu_counts-4:# Защита если количество подходящих акканутов нет
            total = len(Instagram_Accounts)
        else:
            total =  cpu_counts-4
        for _ in range(len(self.MainTreeProcesses), total):
            try:
                acc_data = Instagram_Accounts.pop()
                logpass = acc_data
                self.MainTreeProcesses.append(InstPars(
                    PROFILE_DATA=acc_data,
                    invisable=False,
                    google_services=self.MainTreeProcesses[0]))
            except IndexError:
                print("Аккаунтов на все потоки не вхатило")
                logging.info("Аккаунтов на все потоки не хватило")

        
        
        
        # Для этого модуля логин и пароль не нужны он работает только с MpStats
        self.MainTreeProcesses.append(InstPars(
            invisable=True,
            google_services=self.MainTreeProcesses[0],
            checking=True))


        # Инициируем мониторинг
        monitor = Monitor()
        monitor.main_class = self
        monitor.start()
        
        #  "Поток-менеджмент"
        for proc in self.MainTreeProcesses[2:]: # Запускаемся со второго потому что Гугл и Телега уже запущены
            try:
                proc.start()
            except:
                pass
        while self.MainTreeProcesses[0].running:
            while self.MainTreeProcesses[1].working_data != []:
                for proc in self.MainTreeProcesses[2:-2]:# со второго процесса идет добавление ссылок
                    try:
                        proc.check_this_pages.append(
                            self.MainTreeProcesses[1].working_data.pop())
                    except:
                        pass
                monitor.main_class = self
            if Instagram_Accounts != []:
                for ind in range(2,len(self.MainTreeProcesses[:-2])):
                    if self.MainTreeProcesses[ind].running == False:
                        try:
                            acc_data = Instagram_Accounts.pop()
                            logpass = acc_data[0].split(":")[:2]
                            self.MainTreeProcesses.append(InstPars(
                                LOGIN = logpass[0],
                                PASSWORD = logpass[1],
                                PROFILE_ID = acc_data[3],
                                PORT = acc_data[4],
                                invisable=False,
                                google_services=self.MainTreeProcesses[0]))
                        except:
                            break
            else:
                if len(list(filter(lambda x: x.running == False,self.MainTreeProcesses[2:-2]))) == len(self.MainTreeProcesses[2:-2]):
                    logging.info("Завершение работы программы")
                    break
        else:
            for proc in self.MainTreeProcesses[1:]:
                proc.running = False
            monitor.main_class = self

    def connection_speed(self):
        pass
        # st = pyspeedtest.SpeedTest()
        # nbytes = st.download()
        # return (nbytes)

    def inst_monitor(self, inst_thread: InstPars):
        print("-"*6, "Instagram", "-"*6)
        print(inst_thread.name)
        print(f"Авторизация: {inst_thread.status['auth']}")
        print(f"Профиль: {inst_thread.LOGIN}")
        print(f"Сбор публикаций: {inst_thread.status['publish']}")
        if bool(config["Instagram"]["story_look"]):
            print(f"Сбор рилсов: {inst_thread.status['stories']}")
        print(f"Сбор историй: {inst_thread.status['realse']}")
        print(f"Статус блокировки: {inst_thread.status['guard']}")
        print(f"Выполненно: {inst_thread.total_len_check - len(inst_thread.check_this_pages)}/{inst_thread.total_len_check}")
        print("-"*21)

    def google_monitor(self, google_thread: GoogleService):
        print("-"*7, "Google", "-"*7)
        print(google_thread.name)
        print(f"Статус:{'Запущен' if google_thread.running else 'Не запущен'}")
        print(
            f"Текущая база данных: https://docs.google.com/spreadsheets/d/{config['Google']['table_id']}/")
        print(
            f"База для телеграмм постов: https://docs.google.com/spreadsheets/d/{config['Telegram']['table_id']}/")
        print(
            f"Аккаунты инстаграма хранятся тут: https://d1ocs.google.com/spreadsheets/d/{config['Instagram']['table_id']}\n\tПолучено:{google_thread.instagram_acc_len}")
           
        print("-"*20)

    def tele_monitor(self, telegram_thread: TelegramPars):
        print("-"*6, "Telegram", "-"*6)
        print(
            f"Статус: {'Запущен' if telegram_thread.running else 'Не запущен'}")
        print(
            f"Проверенно групп[{telegram_thread.len_now}/{telegram_thread.len_chan}]")
        print(
            f"Собранно информации из групп [{telegram_thread.len_now}/{telegram_thread.len_chan}]")
        print(
            f"Максимальное количество сообщений: {config['Telegram']['max_messages']}")
        print("-"*20)

    def main_menu(self):
        print("_______________________________________________")
        print("|Выберите нужную опцию:                    |")
        print("|\t1. Запуск                               |")
        print("|\t2. Тестирования модуля для инстаграма   |")
        print("|\t3. Тестирования модуля машинного зрения |")
        print("|\t4.* Скорость интернет-соединения        |")
        print("|\t5. Изменить ТОКЕН для MpStats           |")
        print("|\t6. Тестирования модуля машинного зрения |")
        print("|\t8. Очистить список групп                |")
        print("|\t9. Изменить некоторые парамтры параметры|")
        print("|\t0. Просмотреть текущие параметры        |")
        print("|\t99. Выход                               |")
        print("_______________________________________________")
        try:
            chs = int(input("\n>>> Ответ(цифра опции): "))
            os.system("clear")
        except:
            os.system("clear")
            return (self.main_menu())
        match chs:
            case 1:
                try:
                    self.general_start()
                except Exception as e:
                    print("Произошла ошибка...")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 2:
                try:
                    googl = GoogleService()
                    i = InstPars(LOGIN=googl.instagram_accounts()[0][0].split(":")[0],
                                 PASSWORD=googl.instagram_accounts()[0][0].split(":")[1],
                                 PROFILE_ID=googl.instagram_accounts()[0][3],
                                 google_services=googl,
                                 invisable=False)
                    i.check_this_pages.append(
                        ("https://instagram.com/nastya_pro_wb", 5000))
                    # i.run()
                    print("Тестирование историй...")
                    i.test_stories()
                    print("Тестирование постов...")
                    i.test_pub()
                    i.running = False
                    googl.running = False
                    time.sleep(10)
                except Exception as e:
                    print("Произошла ошибка...")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 3:
                try:
                    img_path = f'timeless_data/test.png'
                    image = cv2.imread(img_path)
                    gry1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    thr1 = cv2.threshold(
                        gry1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                    text = pytesseract.image_to_string(
                        thr1, config="--psm 12 digits")
                    print(text)
                    time.sleep(5)
                except Exception as e:
                    print("Произошла ошибка...")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 4:
                try:
                    print(self.connection_speed())
                    time.sleep(5)
                except Exception as e:
                    print("Скорость интернета выяснить не удалось")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 5:
                try:
                    token = input("Введите токен товара: ")
                    config['Mpstats']['token'] = token
                    time.sleep(5)
                except Exception as e:
                    print("Ошибка")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 6:
                try:
                    token = input("Введите токен товара: ")
                    config['Mpstats']['token'] = token
                    time.sleep(5)
                except Exception as e:
                    print("Ошибка")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 8:
                try:
                    with open("timeless_data/groups.txt", 'w', encoding='utf-8') as fl:
                        fl.write('')
                except Exception as e:
                    print("Ошибка")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 9:
                try:
                    sec = input(
                        'Введите название секции в который собираетесь что то изменить (Например "Instagram"): ')
                    options = [opt for opt in config[sec]]
                    print("Доступные параметры")
                    for opt in options:
                        print(opt)
                    inp = input('Введите название параметра: ')
                    for opt in options:
                        if inp == opt:
                            config[sec][opt] = input("Значение параметра: ")
                            config_update()
                    time.sleep(5)
                except Exception as e:
                    print("Не удалось обновить конфигурацию...")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 0:
                try:
                    for sec in config.sections():
                        print('-'*15, sec, '-'*15)
                        options = [opt for opt in config[sec]]
                        match sec:
                            case 'Telegram':
                                l = ['| IP Телеграм профиля',
                                     '| ХЭШ профиля',
                                     '| Имя пользователя',
                                     '| Предел сообщений',
                                     '| таблица в гугл']
                                for i in range(len(options)):
                                    options[i] = options[i] + " " + \
                                        config[sec][options[i]] + l[i]
                                    print(options[i])
                            case 'Instagram':
                                l = ['| Таблица логинов и паролей',
                                     '| Значение масс-лукинга (если переборщить аккаунт забанят)',
                                     '| Ожидание для входа в профиль(сек)',
                                     '| Максимальное собранное число публикаций',
                                     '| Время после прогрузки страницы пользователя',
                                     '| Ожидание перед появлением истории',
                                     '| Ожидание появления истории',
                                     '| Ожидание появления виджета',
                                     '| Ожидание для работы машинного зрения',
                                     '| Прекращать просмотр рилса, если на таком \nколичестве историй не было артикла',
                                     '| "False" - смотреть рилсы\ "True" - не смотреть',
                                     ]
                                for i in range(len(options)):
                                    options[i] = options[i] + " " + \
                                        config[sec][options[i]] + l[i]
                                    print(options[i])
                            case 'Google':
                                l = ['| Таблица для вывода данных',
                                     '| Период ожидания комманд(сек)',
                                     '| Время ожидания кода(сек)',
                                     '| Количество попыток ожидания за раз'
                                     ]
                                for i in range(len(options)):
                                    options[i] = options[i] + " " + \
                                        config[sec][options[i]] + l[i]
                                    print(options[i])
                            case 'SMS-Activate':
                                l = ['| API - Токен',
                                     '| Скртыный режим',
                                     '| Ожидание кода(сек)',
                                     '| Количество попыток ожидания за раз',
                                     '| Диапазон времени когда должен был прийти код +- *параметр* минут',
                                     ]
                                for i in range(len(options)):
                                    options[i] = options[i] + " " + \
                                        config[sec][options[i]] + l[i]
                                    print(options[i])
                            case 'Mpstats':
                                l = ['| API - Токен']
                                for i in range(len(options)):
                                    options[i] = options[i] + " " + \
                                        config[sec][options[i]] + l[i]
                                    print(options[i])
                    input("Нажмите Ввод для продолжения...")
                except Exception as e:
                    print("Не удалось обновить конфигурацию...")
                    logging.error(traceback.format_exc())
                    time.sleep(5)
                return (self.main_menu())
            case 99:
                self.running = False
                return None
            case _:
                print("Нет такой опции")
                time.sleep(5)
                return (self.main_menu())





if __name__ == "__main__":
    m = Main().main_menu()
    
