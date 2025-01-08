from typing import List, Optional
from pydantic import BaseModel

sample_messages = """
짜파게티 먹고싶다

:헐 저녁에 묵어야지

저녁에 다른 반찬 추가해서 먹어😉

:의식의 흐름 그자체 ㅋㅋㅋㅋㅋ

정신은 없지만 버블은 하고싶고 그런 상태랄까

:ㅋㅋㅋㅋㅋ새삼 방금 류진이는 카레 추천해준게 너무 웃기다ㅋㅋㅋㅋㅋ정반대자나

오

짜장,카레

:예지냐 류진이냐 이건가

그치만 믿지들은 편 가르지 말고 

:둘 다 먹어~!~!
다들 땡덩 좋아하는 거 다 알아👀

짜장카레 섞어서 이렇게? ！
이건 좀 사랑이다..!

암튼 ㅎㅎ

곧 저녁 먹을 시간인데 맛있는 걸로 잘 챙겨먹구 남은 하루도 잘 보내기야ㅎㅎ

:예지도 남은 하루도 잘 보내요🖤

웅 고마워showay🖤🍀
"""

class RawMessage(BaseModel):
    artist_message: str = ""
    fan_message: Optional[str] = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.fan_message:
            return f">{self.fan_message}\n{self.artist_message}"
        else:
            return f"{self.artist_message}"

def handle_message(message: str, user_name: str) -> List[RawMessage]:
    """
    Every sentences from the artist will be separated by \n\n.
    It is possible that some sentences is sent by fans.
    If so, it will be prefixed with ":" or followed by \n and the artist's response.
    A fan message will always be followed by an artist's response.
    @@@ means that the artist is mentioning all users. It should be remained.
    """
    raw_messages = []
    message = message.replace(user_name, "@@@")
    is_responsing = False
    for msg in message.split("\n\n"):
        msg = msg.strip()

        if msg.count("\n") == 1:  # a fan message followed by \n and the artist's response
            fan_message, artist_message = msg.split("\n")
            fan_message = fan_message[1:] if fan_message.startswith(":") else fan_message
            raw_messages.append(RawMessage(artist_message=artist_message.strip(), fan_message=fan_message.strip()))
            continue
        
        if msg.startswith(":"):  # a fan message, the next message will be the artist's response
            msg = msg[1:]
            raw_messages.append(RawMessage(fan_message=msg.strip()))
            is_responsing = True
            continue
    
        if is_responsing:  # the artist's response
            raw_messages[-1].artist_message = msg.strip()
            is_responsing = False
            continue

        raw_messages.append(RawMessage(artist_message=msg.strip()))

    return raw_messages

if __name__ == "__main__":
    for line in handle_message(sample_messages, "showay"):
        print(f"{line}\n")