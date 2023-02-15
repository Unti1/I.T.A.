from settings.config import *


class mailru_mail:
    def __init__(self,driver:webdriver.Chrome) -> None:
        self.driver = driver
    
    def mail_check(self):
        main_page = self.driver.current_window_handle
        self.driver.switch_to.new_window("mail_win")
        ####################### Вход ##########################
        '''
        try:
            self.driver.get("https://mail.ru/")

            WebDriverWait(self.driver,15).until(EC.element_to_be_clickable((By.XPATH,'//button[@data-testid="enter-mail-primary"]')))
            self.driver.find_element(By.XPATH,'//button[@data-testid="enter-mail-primary"]').click()
            time.sleep(10)
            input_mail_area = self.driver.find_element(By.XPATH,'//input[@name="username"]')
            input_mail_area.send_keys(f"{email}")
            self.driver.find_element(By.XPATH,'//button[@data-test-id="next-button"]').click()

            time.sleep(5)
            input_pass_area = self.driver.find_element(By.XPATH,'//input[@name="password"]')
            input_pass_area.send_keys(f"{password}")
            self.driver.find_element(By.XPATH,'//button[@data-test-id="submit-button"]').click()

        except exceptions.TimeoutException:
            logging.error(traceback.format_exc())
        '''
        ######### Разбор почты ############
        try:
            self.driver.get("https://e.mail.ru/messages/inbox/")
            WebDriverWait(self.driver,18).until(EC.visibility_of_element_located((By.XPATH,'//a[@data-uidl-id]')))
            all_mails = self.driver.find_elements(By.XPATH,'//a[@data-uidl-id]')
            all_mails = list(map(lambda x: x.get_attribute('href'), self.driver.find_elements(By.XPATH,'//a[@data-uidl-id]')))
            all_mails_time = list(map(lambda x: x.get_attribute('title').lower(), self.driver.find_elements(By.XPATH,'//a[@data-uidl-id]//div[@title]')))
            all_mails = list(zip(all_mails,all_mails_time))
            all_mails = list(filter(lambda x: "сегодня" in x[1] or "вчера" in x[1],all_mails))
            for mail in all_mails:
                self.driver.get(mail[0])
                WebDriverWait(self.driver,15).until(EC.element_to_be_clickable((By.XPATH,'//div[@class="letter__head"]')))
                header = self.driver.find_element(By.XPATH,'//div[@class="letter__head"]').text.lower()
                if "instagram" in header:
                    text = self.driver.find_element(By.XPATH,'//div[@class="letter__body"]').text
                    text = text.replace(" ","")
                    code = re.search(r"\d{6}", text)
                    if code:
                        return(code[0])
                else:
                    continue
        except:
            logging.error(traceback.format_exc())
        self.driver.close()
        self.driver.switch_to.window(main_page)
        time.sleep(10)
        return('')
