from settings.config import *
from tools.google import GoogleService

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

# proxy = (proxy_server, proxy_port, proxy_key)

client = TelegramClient(username, api_id, api_hash)
# connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
# proxy=proxy)

client.start()


async def dump_all_participants(channel):
    """Записывает json-файл с информацией о всех участниках канала/чата"""
    offset_user = 0    # номер участника, с которого начинается считывание
    limit_user = 100   # максимальное число записей, передаваемых за один раз

    all_participants = []   # список всех участников канала
    filter_user = ChannelParticipantsSearch('')

    while True:
        participants = await client(GetParticipantsRequest(channel,
                                                           filter_user, offset_user, limit_user, hash=0))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset_user += len(participants.users)

    all_users_details = []   # список словарей с интересующими параметрами участников канала

    for participant in all_participants:
        all_users_details.append({"id": participant.id,
                                  "first_name": participant.first_name,
                                  "last_name": participant.last_name,
                                  "user": participant.username,
                                  "phone": participant.phone,
                                  "is_bot": participant.bot})


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0    # номер записи, с которой начинается считывание
    limit_msg = 100   # максимальное число записей, передаваемых за один раз

    all_messages = []   # список всех сообщений
    total_messages = 0
    total_count_limit = 100  # поменяйте это значение, если вам нужны не все сообщения

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            return None
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            return (all_messages)


async def collect_msgs_from_telegram_channel(url):
    # url = "https://t.me/otzovik_blogger"
    channel = await client.get_entity(url)
    print(f"[TeleParse] Перешел в канал: {url}")
    msgs = await dump_all_messages(channel)
    # Собираем конкретно сообщения из всех данных
    msgs = list(map(lambda x: x.get('message'), msgs))
    final_lst = []
    for msg in msgs:
        if msg:
            m1 = re.search(r"(?:\Sеклам[е,у,ы,а]|\Sакет[ом,ы,ам,а]|\Sекламировал[ись,ала]|\Sенеджер|\Sабор)", msg)
            if m1 != None:
                msg = msg.split(m1[0])[1]
                m = re.search(r"https://instagram.com/\S{1,}", msg)
                if m:
                    acc_url = m[0]
                    msg = msg.split(m[0])[1]
                    if m:
                        msg = msg.lower()
                        m = re.search(r"(?:стоимость|цена)", msg)
                        if m:
                            msg = msg.split(m[0])[1]
                            m = re.search(
                                r"(?:\d{1,}.\d{2,}|\d{3,})", msg.lower())
                            if m:
                                cost = "".join(list(filter(lambda x: x in [str(x) for x in range(10)],m[0])))
                                final_lst.append((acc_url,cost))
    return final_lst

class TelegramPars():
    def __init__(self,google_service):
        self.google: GoogleService = google_service # подключается гуг сервис для сбора ссылок с таблицы
        self.running = True
        self.all_channels = self.google.telegram_channels()
        self.saved_data = self.check_save_groups()
        self.telegram_profiles_data = self.check_parsed_profiles()
        self.len_chan = len(self.all_channels)
        self.len_now = 0
        self.working_data = []

    def check_save_groups(self):
        with open("timeless_data/groups.txt","r") as fl: 
            dat = fl.read()
            dat = dat.split(',')
            return(dat)

    def save_group(self,group):
        with open("timeless_data/groups.txt","a") as fl: 
            fl.write(f'{group},')
    
    def check_parsed_profiles(self):
        data_path = "timeless_data/telegram_profiles.csv"
        data = []
        if os.path.exists(data_path):
            with open(data_path,'r',encoding='utf-8') as fl:
                reader = csv.reader(fl)
                for row in reader:
                    data.append(row)
                return(data)
        else:
            with open(data_path,'w',encoding='utf-8') as fl:
                fl.write("")
                return([])

    def append_parsed_profiles(self,info):
        """Дозапись профилей в базу
        Args:
            info (_type_): (ссылка, цена, собран или нет?)
        """
        data_path = "timeless_data/telegram_profiles.csv"
        self.telegram_profiles_data = self.check_parsed_profiles()
        already_appended = []
        with open(data_path,'a',encoding='utf-8') as fl:
            writer = csv.writer(fl,dialect = 'excel')
            for row in info:
                if (row[0] not in list(map(lambda x: x[0],self.telegram_profiles_data))) and row[0] not in already_appended:
                    row = list(row)
                    row.append("False")
                    writer.writerow(row)
                    already_appended.append(row[0])
    
    def collect_msgs_from_channels(self):
        with client:
            while self.all_channels != []:
                try:
                    url_group = self.all_channels.pop()
                    if url_group not in self.saved_data:
                        loop_data = client.loop.run_until_complete(collect_msgs_from_telegram_channel(url_group))
                        self.append_parsed_profiles(loop_data)
                        self.working_data = list(filter(lambda dat: dat[-1] != "True",self.check_parsed_profiles()))
                        # print("Итого работаем с: ",self.working_data)
                        self.working_data.extend(self.check_parsed_profiles())
                        self.saved_data.append(url_group)
                        self.save_group(url_group)
                        self.len_now += 1
                        logging.info(self.saved_data)
                    else:
                        self.all_channels.pop()
                except IndexError:
                    pass
                except:
                    logging.error(traceback.format_exc())
            else:
                self.working_data = list(filter(lambda dat: dat[-1] != "True",self.check_parsed_profiles()))
            if self.working_data != []:
                self.working_data = list(map(lambda dat: dat[:-1],self.working_data))
            print(self.working_data)
    def run(self):
        try:
            if self.all_channels != []:
                self.collect_msgs_from_channels()
        except:
            logging.error(traceback.format_exc())

if __name__ == "__main__":
    pass
    g = GoogleService()
    # print(client.loop.run_until_complete(collect_msgs_from_telegram_channel("https://t.me/otzovik_blogger")))
    TelegramPars(g).run()
    print(1)