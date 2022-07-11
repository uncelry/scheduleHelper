import requests
from diploma_rest.settings import BOT_TOKEN, TG_CHAT_ID


def send_info_to_bot(message):
    res = requests.post(
        url="https://api.telegram.org/bot{0}/{1}".format(BOT_TOKEN, "sendMessage"),
        data={"chat_id": TG_CHAT_ID, "text": str(message)}
    )

