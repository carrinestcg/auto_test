"""
最小可動範例：飛書/Lark WebSocket 長連接接收訊息
跑起來後，到你綁定這個應用的群組或私訊裡打字，console 會印出收到的內容。
"""

import os
import lark_oapi as lark
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("LARK_APP_SECRET")


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """收到訊息時觸發"""
    sender_id = data.event.sender.sender_id.open_id
    chat_id = data.event.message.chat_id
    content = data.event.message.content  # JSON 字串，例如 {"text":"hello"}

    print("=" * 50)
    print(f"收到訊息！")
    print(f"   sender_id: {sender_id}")
    print(f"   chat_id  : {chat_id}")
    print(f"   content  : {content}")
    print("=" * 50)


if __name__ == "__main__":
    if not APP_ID or not APP_SECRET:
        print("❌ 請先在 .env 設定 LARK_APP_ID 和 LARK_APP_SECRET")
        exit(1)

    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
        .build()

    cli = lark.ws.Client(
        APP_ID,
        APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.DEBUG,
        domain=lark.LARK_DOMAIN  # 國際版 Lark，預設是中國版 feishu.cn
    )

    print("🔌 正在連接 Lark...")
    cli.start()  # 連上之後會印出 "connected to wss://xxxxx"，並且 block 住主程式