from settings.config import *
from tools.google import GoogleService
from tools.mpstats import MpStats
from tools.insta import InstPars
from tools.tele import TelegramPars


class Main():
    def __init__(self):
        self.running = True

    def general_start(self):
        """TODO: Проверить"""
        cpu_counts = os.cpu_count()
        self.MainTreeProcesses = []
        '''
        0 - Google Service
        1 - Telegram
        2+ - InstPars 
        '''
        # Добоавляем потоки
        self.MainTreeProcesses.append(GoogleService())
        self.MainTreeProcesses.append(TelegramPars(
            google_service=self.MainTreeProcesses[0]))
        for _ in range(len(self.MainTreeProcesses), cpu_counts-2):
            self.MainTreeProcesses.append(InstPars(
                LOGIN=config['Instagram']['Login'],
                PASSWORD=config['Instagram']['Password'],
                invisable=True,
                google_services=self.MainTreeProcesses[0]))
        self.MainTreeProcesses.append(InstPars(
            LOGIN=config['Instagram']['Login'],
            PASSWORD=config['Instagram']['Password'],
            invisable=True,
            google_services=self.MainTreeProcesses[0],
            checking=True))
        self.MainTreeProcesses[1].run() # Собираем данные для пользователей
        # Запускаем потоки

        for proc in self.MainTreeProcesses:
            try:
                proc.start()
            except:
                pass
        Thread(target=monitoring_screen, args=(self)).run()
        while self.MainTreeProcesses[0].running:
            while self.MainTreeProcesses[1].working_data != []:
                for proc in self.MainTreeProcesses[2:-1]:# со второго процесса идет добавление ссылок
                    try:
                        proc.check_this_pages.append(
                            self.MainTreeProcesses[1].working_data.pop())
                    except:
                        pass
        else:
            for proc in self.MainTreeProcesses[1:]:
                proc.running = False

    def connection_speed(self):
        pass
        # st = pyspeedtest.SpeedTest()
        # nbytes = st.download()
        # return (nbytes)

    def inst_monitor(self, inst_thread: InstPars):
        print("-"*6, "Instagram", "-"*6)
        print(inst_thread.name)
        print(f"Авторизация: {inst_thread.status['auth']}")
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
                    i = InstPars(LOGIN="instaparstable@gmail.com",
                                 PASSWORD="Qweasdzxc123!",
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
                                l = ['| логин',
                                     '| пароль',
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


def monitoring_screen(mainproc: Main):
    while mainproc.MainTreeProcesses[0].running:
        try:
            mainproc.google_monitor(mainproc.MainTreeProcesses[0])
            mainproc.tele_monitor(mainproc.MainTreeProcesses[1])
            for proc in mainproc.MainTreeProcesses[2:]:
                mainproc.inst_monitor(proc)
            time.sleep(3)
            os.system("clear")
        except:
            logging.info(f"Ошибка отображения {traceback.format_exc()}")
    else:
        time.sleep(10)


if __name__ == "__main__":
    m = Main().main_menu()
    
