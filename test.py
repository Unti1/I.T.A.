from tools.tele import *
from tools.google import *



if __name__ == "__main__":
    g = GoogleService()
    g.start()

    account = g.instagram_accounts()
    print(list(map(lambda x: g.check_account_limit(x),account)))
    account = list(filter(lambda x: g.check_account_limit(x),account))
    print(account)
#     account[0][-1] = '0'
#     g.instagram_update_values(account[0][0],account[0])  
    # for acc in account:
#         print(g.check_account_limit(acc))
#     # print(client.loop.run_until_complete(collect_msgs_from_telegram_channel("https://t.me/otzovik_blogger")))
#     # TelegramPars(g).run()
#     # print(1)
