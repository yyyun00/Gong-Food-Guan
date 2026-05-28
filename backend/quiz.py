"""
quiz.py - 心情問卷邏輯
"""

import random

RAW_Q1_QUOTES = [
    {"text": "「長風破浪會有時，直掛雲帆濟滄海。」—— 李白", "emotion": "開心"},
    {"text": "「哪有人喜歡孤獨，不過是受夠了失望。」—— 村上春樹", "emotion": "難過"},
    {"text": "「不在沉默中爆發，就在沉默中滅亡。」—— 魯迅", "emotion": "生氣"},
    {"text": "「人生是一團慾望，滿足便無聊，不滿足便痛苦。」—— 叔本華", "emotion": "煩躁"},
    {"text": "「回首向來蕭瑟處，歸去，也無風雨也無晴。」—— 蘇軾", "emotion": "平靜"},
]

RAW_Q2_ENVIRONMENTS = [
    {"text": "春日文學院的杜鵑花海", "emotion": "開心"},
    {"text": "寒流冬雨中的醉月湖亭子", "emotion": "難過"},
    {"text": "七月烈日下的水源腳踏車拖吊場", "emotion": "生氣"},
    {"text": "午後雷陣雨濕黏悶熱的椰林大道", "emotion": "煩躁"},
    {"text": "週日早晨安靜空曠的總圖二樓閱覽室", "emotion": "平靜"},
]

RAW_Q3_COLORS = [
    {"text": "正午烈日般的亮橘色", "emotion": "開心"},
    {"text": "深邃的憂鬱藍", "emotion": "難過"},
    {"text": "帶有壓迫感的警示紅", "emotion": "生氣"},
    {"text": "混濁的暗綠色", "emotion": "煩躁"},
    {"text": "柔和的米白色", "emotion": "平靜"},
]

# 低：200元以內（price_tier=1）
# 中：200-400元（price_tier=2）
# 高：400元以上（price_tier=3）
RESTAURANT_POOL = {
    "生氣": {
        "低": ["水源市場祥記炒燴", "沙威瑪大王", "小螺波 Xiao Luo Bo", "鳳城燒臘",
               "阿布都中東清真料理", "麻辣巴雷", "德克士", "龍記炒燴", "刁四麻辣燙",
               "老鐵沒毛病"],
        "中": ["得記麻辣", "直火人直火燒肉丼飯屋", "初牛（公館店）", "新馬辣",
               "台大牛莊", "上賀海南雞", "大埔鐵板燒", "炎弟鐵板燒", "韓國時間",
               "蚩尤鐵板燒", "赤神日式豬排公館店", "威宇牛排", "延三溫體牛-黃記"],
        "高": ["辛殿麻辣鍋", "龐德羅莎"],
    },
    "難過": {
        "低": ["四海遊龍", "八方雲集", "銀座河粉蛋麵", "山西刀削麵", "墨洋拉麵",
               "丼丼go", "小高拉麵", "越南清化河粉", "一川鍋燒麵", "巷子口面攤",
               "泰好吃泰國船麵", "桃源街石記麵館", "香鄉麵食館", "粥大福",
               "麥當勞(新生)", "麥當勞(公館)", "維綸麵食館"],
        "中": ["山嵐拉麵（公館店）", "天使ハート女僕咖啡廳", "溏老鴨", "想聚mr.jadeng",
               "隱家拉麵", "夢見女僕咖啡館", "七里亭", "馬德連小酒館", "米澤製麵",
               "純愛小吃部", "巴生仔大馬料理店", "靜壽司", "順園小館"],
        "高": ["壽司郎"],
    },
    "煩躁": {
        "低": ["藍家割包", "太學口糯米腸包香腸", "雄記蔥抓餅", "阿薄郎",
               "如來素食樂園", "妙觀音素食", "Subway", "鱷吐司"],
        "中": ["BFF Gossip Brunch早午餐", "阿鸞手工法國麵包", "韓天閣",
               "Tacoc joe美墨塔可", "義樂麵屋", "曹氏家司機食堂", "五九麵館",
               "義響食堂", "首爾之家", "喜禾嘉", "este dia這一天異國廚房", "小飯館兒"],
        "高": ["貳樓餐館", "貳樓", "希臘左巴", "JJ's POKE & CAFE", "花漾薇漫餐廳"],
    },
    "開心": {
        "低": ["活大", "女九", "大一女", "禮賢堂", "台科大樓下", "沙嗲士多",
               "yoyo韓式飯捲", "公館阿姨滷味", "福二漢堡製造所"],
        "中": ["大叔食事", "泰正點泰式料理", "泰國小館", "發現義大利麵", "泰街頭",
               "瑪麗針", "咖哩先生", "神燈搓一下", "祝您行運", "稻咖哩", "參柒",
               "yoyo韓式飯捲", "雲香亭", "深夜未歸", "潮味決", "泰悠thai yo",
               "個人鍋物", "柳狀元螺獅粉特色火鍋"],
        "高": ["池先生", "光一肆號三時午咖哩屋", "俄羅斯城堡", "歐嬤德式美食",
               "El Sabroso Mexican Food", "好處餐酒館"],
    },
    "平靜": {
        "低": [],   # 從所有情緒低價池隨機抽（見 fetch_restaurant）
        "中": [],
        "高": [],
    },
}

# 平靜：從全池各預算隨機抽
def _all_by_budget(budget: str) -> list[str]:
    result = []
    for emo, tiers in RESTAURANT_POOL.items():
        if emo == "平靜":
            continue
        result.extend(tiers.get(budget, []))
    return result

RESTAURANT_POOL["平靜"] = {
    "低": _all_by_budget("低"),
    "中": _all_by_budget("中"),
    "高": _all_by_budget("高"),
}


class QuizEngine:
    def __init__(self):
        self.current_q1 = self._shuffle(RAW_Q1_QUOTES)
        self.current_q2 = self._shuffle(RAW_Q2_ENVIRONMENTS)
        self.current_q3 = self._shuffle(RAW_Q3_COLORS)

    def _shuffle(self, pool: list) -> list:
        copy = pool.copy()
        random.shuffle(copy)
        return copy

    def get_questions(self) -> list[dict]:
        return [
            {"stage": "quote",       "topic": "【第一層：名言】", "text": "請選擇一句最符合你現在心境的句子",         "options": [i["text"] for i in self.current_q1]},
            {"stage": "environment", "topic": "【第二層：環境】", "text": "如果能瞬間移動，你的靈魂最想去台大的哪裡？", "options": [i["text"] for i in self.current_q2]},
            {"stage": "color",       "topic": "【第三層：顏色】", "text": "直覺選一個最能代表你此刻感受的顏色",       "options": [i["text"] for i in self.current_q3]},
        ]

    def decode_emotions(self, idx1: int, idx2: int, idx3: int) -> list[str]:
        try:
            return [self.current_q1[idx1]["emotion"],
                    self.current_q2[idx2]["emotion"],
                    self.current_q3[idx3]["emotion"]]
        except IndexError:
            raise ValueError("選項索引超出範圍")

    def check_flow(self, emotions: list[str]) -> dict:
        if len(set(emotions)) < 3:
            final = max(set(emotions), key=emotions.count)
            return {"trigger_q4": False, "determined_emotion": final}
        return {"trigger_q4": True, "determined_emotion": None,
                "q4_options": ["開心", "難過", "生氣", "煩躁", "都可以"]}

    def fetch_restaurant(self, emotion: str, budget: str) -> str | None:
        if emotion == "都可以":
            candidates = []
            for tiers in RESTAURANT_POOL.values():
                candidates.extend(tiers.get(budget, []))
        else:
            candidates = RESTAURANT_POOL.get(emotion, {}).get(budget, [])
        return random.choice(candidates) if candidates else None