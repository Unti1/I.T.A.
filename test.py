from tools.tele import *
from tools.google import *


if __name__ == "__main__":
    g = GoogleService()
    account = g.instagram_accounts()
    print(account)
    for acc in account:
        print(g.check_account_limit(acc))
    # print(client.loop.run_until_complete(collect_msgs_from_telegram_channel("https://t.me/otzovik_blogger")))
    # TelegramPars(g).run()
    # print(1)