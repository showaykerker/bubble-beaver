"""
Sample Korean messages from different artists for testing the translation pipeline.
Each artist has their own style and common phrases.
"""

ARTIST_PROMPTS = {
    "IU": (
        "IU often uses playful and warm language, frequently addressing fans as 'UAENA'. "
        "She's known for her witty wordplay and often includes musical references. "
        "Her messages tend to be detailed and thoughtful. She often uses cute emoticons "
        "and maintains a close, friendly relationship with fans while staying professional."
    ),
    "BTS_V": (
        "V (Kim Taehyung) has a unique, quirky writing style with lots of creative expressions. "
        "He often uses 'Borahae' (보라해) and purple heart emojis. His messages can be philosophical "
        "and artistic, reflecting his personality. He's known for his deep thinking and unique "
        "perspectives, often sharing artistic photos and thoughts about music and art."
    )
}

SAMPLE_MESSAGES = {
    "IU": [
        {
            "text": "우리 유애나 보고싶다 🥺 다들 잘 지내고 있죠? 이제 곧 추워질 텐데 감기 조심하세요!",
            "context": "Regular check-in with fans"
        },
        {
            "text": "오늘 새로운 곡 녹음했어요~ 기대되시죠? 힌트는... 🎵✨",
            "context": "Music update"
        },
        {
            "text": "드디어 콘서트 준비 시작! 열심히 연습하고 있으니까 기대해주세요 우리 유애나 ❤️",
            "context": "Concert preparation"
        }
    ],
    "BTS_V": [
        {
            "text": "보라해요 아미들~ 🫰💜 오늘도 행복한 하루 보내세요",
            "context": "Daily greeting"
        },
        {
            "text": "방금 찍은 사진이에요... 어때요? 분위기 있죠? 🎨 영감이 떠올랐어요",
            "context": "Sharing artistic photo"
        },
        {
            "text": "여러분 덕분에 제가 더 성장할 수 있었어요... 감사합니다 아미 💜 보라해",
            "context": "Gratitude message"
        }
    ]
}

CONVERSATION_THREADS = {
    "IU": {
        "IU_Concert_Prep": [
            {
                "text": "안녕하세요 유애나~ 오늘부터 콘서트 연습 시작했어요!",
                "context": "First message about concert preparation"
            },
            {
                "text": "새로운 버전의 노래도 준비하고 있는데... 깜짝 놀라실 거예요 ㅎㅎ",
                "context": "Follow-up about special preparations"
            },
            {
                "text": "연습하다가 찍은 영상 살짝 보여드릴까요...? 🤫",
                "context": "Teasing concert spoiler"
            }
        ]
    },
    "BTS_V": {
        "V_Art_Series": [
            {
                "text": "요즘 그림 많이 그리고 있어요... 영감이 막 떠올라서 💭",
                "context": "Starting art series"
            },
            {
                "text": "이건 어떠세요...? 색감이 마음에 들어서 한참 그렸어요 🎨",
                "context": "Sharing artwork"
            },
            {
                "text": "보라색이 포인트인데... 아미 생각하면서 그렸어요 💜",
                "context": "Explaining art meaning"
            }
        ]
    }
}
