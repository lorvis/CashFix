import requests
import json
import certifi
import sys, os

# def override_where():
#     """ overrides certifi.core.where to return actual location of cacert.pem"""
#     # change this to match the location of cacert.pem
#     return os.path.abspath("C:\Python34\Lib\site-packages\certifi\cacert.pem")
#
#
# # is the program compiled?
# if hasattr(sys, "frozen"):
#     import certifi.core
#
#     os.environ["REQUESTS_CA_BUNDLE"] = override_where()
#     certifi.core.where = override_where
#
#     # delay importing until after where() has been replaced
#     import requests.utils
#     import requests.adapters
#     # replace these variables in case these modules were
#     # imported before we replaced certifi.core.where
#     requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
#     requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()

file = open('currencies.txt', 'r')
currs_with_amount = file.read().split('\n')
file.close()
try:
    currs_with_amount.remove('')
except:
    pass

prev_uah_cost = None
prev_usd_cost = None

try:
    log = open('log.txt', 'r')
    log_arr = log.read().split('\n')
    float(log_arr[-1])
    float(log_arr[-2])
except:
    print("No log file found")
else:
    prev_uah_cost = float(log_arr[-1])
    prev_usd_cost = float(log_arr[-2])
finally:
    log.close()

log = open('log.txt', "w")

currs = {}

for curr in currs_with_amount:
    pair = curr.split(" ")
    currs[pair[1]] = pair[0]

total_cost = 0

print("TOKEN: AMOUNT * PRICE = COST / 1h / 24h / 7d")
for curr in currs:
    response = json.loads(requests.get("https://api.coinmarketcap.com/v1/ticker/" + curr + "/").text)[0]
    amount = currs[curr]
    price = response["price_usd"]
    cost = float(amount) * float(price)
    total_cost += cost
    curr_line = response["symbol"] + ": " + str(amount) + " * " + str(price) + " = " + str(cost) + " / " + response["percent_change_1h"] + "% / " + response["percent_change_24h"] + "% / " + response["percent_change_7d"] + "%"
    print(curr_line)
    log.write(curr_line + "\n")
NBU_response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
USD_to_UAH = [x["rate"] for x in json.loads(NBU_response.text) if int(x["r030"]) == 840]
uah_cost = USD_to_UAH[0] * total_cost
log.write("\nUAH TO USD: " + str(USD_to_UAH[0]) + '\n')
print("\nUAH TO USD: " + str(USD_to_UAH[0]))
log.write("TOTAL COST USD/UAH: " + "{0:.2f}".format(total_cost) + "/" + "{0:.2f}".format(uah_cost))
print("TOTAL COST USD/UAH: " + "{0:.2f}".format(total_cost) + "/" + "{0:.2f}".format(uah_cost))
if prev_uah_cost != None and prev_usd_cost !=None:
    perline = "TOTAL COST PERCENTAGE USD%/UAH%: " + "{0:.2f}".format((total_cost - prev_usd_cost)/prev_usd_cost*100) + "% / " + "{0:.2f}".format((uah_cost - prev_uah_cost)/prev_uah_cost*100) + "%"
    print(perline)
    log.write('\n' + perline + '\n')
log.write('\n\n' + "{0:.2f}".format(total_cost) + '\n' + "{0:.2f}".format(uah_cost))
log.close()
input("Press any key")
