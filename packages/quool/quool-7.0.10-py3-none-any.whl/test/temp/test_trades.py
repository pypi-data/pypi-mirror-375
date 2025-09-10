# import schedule
# import time
from quool import XtBroker


def trade():
    broker = XtBroker(
        account="8883491319", path=r"D:\Program Files\国金证券QMT交易端\userdata_mini"
    )
    # broker.close(code="603170.SH")
    broker.buy(code="300869.SZ", quantity=3600000000000)

trade()
# schedule.every().day.at("09:30").do(trade)

# while True:
#     schedule.run_pending()
#     time.sleep(1)