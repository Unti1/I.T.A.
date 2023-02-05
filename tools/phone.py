from settings.config import *


class VirtualNumber:
    def __init__(self, invisable=bool(config["SMS-Activate"]["invis"])):
        self.activator = SMSActivateAPI(config["SMS-Activate"]["API"])
        self.phone = self.activator.getRentList().get("values").get("0").get('phone')
        self.id = self.activator.getRentList().get("values").get("0").get('id')
        if not invisable:
            self.activator.debug_mode = True

    def check_time(self):
        msg_time = self.activator.getRentStatus(
            self.id).get("values").get("0").get("date")
        n_time = datetime.datetime.strptime(msg_time, '%Y-%m-%d %H:%M:%S')
        time_in_s = datetime.datetime.timestamp(n_time)
        last = datetime.datetime.timestamp(
            datetime.datetime.now() - datetime.timedelta(minutes=int(config["SMS-Activate"]["sms_area_time"])))
        past = datetime.datetime.timestamp(
            datetime.datetime.now() + datetime.timedelta(minutes=int(config["SMS-Activate"]["sms_area_time"])))
        if float(time_in_s) in range(int(last), int(past)):
            return True
        else:
            return False

    def check_sms(self,counter = 0):
        logging.info("Попытка получить код по СМС")
        while counter < int(config["SMS-Activate"]["max_try"]):
            if self.activator.getRentStatus(self.id).get("status") == "error":
                counter += 1
                logging.info("SMS не получено")
                time.sleep(int(config["SMS-Activate"]["timeout"]))
            elif self.check_time(): # Настройка диапазона времени в которое мы должны будем получить сообщение
                msg: dict = self.activator.getRentStatus(
                    self.id).get("values").get("0")
                text = msg.get('text')
                date = msg.get('date')
                code = re.search(r'\d{6}', text)
                code = code[0]
                logging.info("Сообщение найдено",code, text, date, sep=" | ")
                return (code)
            else:
                logging.info("SMS не получено")
                time.sleep(int(config["SMS-Activate"]["timeout"]))
                counter += 1
        return("")
            

if __name__ == "__main__":
    VirtualNumber().check_sms()
