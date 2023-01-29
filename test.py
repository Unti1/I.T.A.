from settings.config import *

options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument('--no-sandbox')
driver= webdriver.Chrome(options=options)
serv = Service(ChromeDriverManager().install())
driver.get('https://www.instagram.com/support_point/')

print(driver.title)
driver.quit()