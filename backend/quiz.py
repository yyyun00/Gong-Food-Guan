"""
quiz.py - 心情問卷邏輯
"""

import random

RAW_Q1_QUOTES = [
    # 開心
    {"text": "「長風破浪會有時，直掛雲帆濟滄海。」—— 李白", "emotion": "開心"},
    {"text": "「每一個不曾翩翩起舞的日子，都是對生命的辜負。」—— 尼采", "emotion": "開心"},
    {"text": "「我只願相信一個會跳舞的神。」—— 尼采", "emotion": "開心"},
    {"text": "「在這個世界上，沒有熱情，就沒有任何偉大的事業可以完成。」—— 黑格爾", "emotion": "開心"},
    {"text": "「世界歷史就是自由意識的進展。」—— 黑格爾", "emotion": "開心"},
    {"text": "「快樂的三大要素：有事做、有人愛、有希望。」—— 康德", "emotion": "開心"},
    {"text": "「勇於求知！（Sapere Aude）」—— 康德", "emotion": "開心"},
    {"text": "「一個精神世界豐富的人，在完全孤獨之中，也能在自己的思想中找到極大的娛樂。」—— 叔本華", "emotion": "開心"},
    {"text": "「藝術是生命的解毒劑，它讓我們暫時擺脫意志的痛苦，獲得純粹的審美喜悅。」—— 叔本華", "emotion": "開心"},
    {"text": "「不登高山，不知天之高也；不臨深溪，不知地之厚也。」—— 荀子", "emotion": "開心"},
    {"text": "「積善成德，而神明自得，聖心備焉。」—— 荀子", "emotion": "開心"},
    {"text": "「獨與天地精神往來，而不敖倪於萬物。」—— 莊子", "emotion": "開心"},
    {"text": "「鰷魚出遊從容，是魚之樂也。」—— 莊子", "emotion": "開心"},
    {"text": "「祈禱並不改變上帝，但它改變祈禱的人。」—— 齊克果", "emotion": "開心"},
    {"text": "「生命的最高成就，就是能以一個獨立個體的身分，在上帝面前充滿喜悅地存在。」—— 齊克果", "emotion": "開心"},

    # 難過
    {"text": "「哪有人喜歡孤獨，不過是受夠了失望。」—— 村上春樹", "emotion": "難過"},
    {"text": "「希望是所有邪惡中之最，因為它延長了人類的痛苦。」—— 尼采", "emotion": "難過"},
    {"text": "「當你遠遠凝視深淵時，深淵也在凝視你。」—— 尼采", "emotion": "難過"},
    {"text": "「人類從歷史學到的唯一教訓，就是人類沒有從歷史中學到任何教訓。」—— 黑格爾", "emotion": "難過"},
    {"text": "「歷史並非幸福的劇場。那段幸福的時期，不過是歷史中空白的幾頁。」—— 黑格爾", "emotion": "難過"},
    {"text": "「用人類這根曲木，絕然造不出任何筆直的東西。」—— 康德", "emotion": "難過"},
    {"text": "「人類的理性有一種特殊的命運：它被一些無法迴避、卻也無法回答的問題所困擾。」—— 康德", "emotion": "難過"},
    {"text": "「人生就像鐘擺，在痛苦與無聊之間擺盪。」—— 叔本華", "emotion": "難過"},
    {"text": "「生命本質上就是一場痛苦的掙扎，我們最終都將以死亡迎來失敗。」—— 叔本華", "emotion": "難過"},
    {"text": "「人之性惡，其善者偽也。」—— 荀子", "emotion": "難過"},
    {"text": "「心憂恐則口銜芻豢而不知其味，耳聽鐘鼓而不知其聲。」—— 荀子", "emotion": "難過"},
    {"text": "「哀莫大於心死，而人死亦次之。」—— 莊子", "emotion": "難過"},
    {"text": "「人生天地之間，若白駒過隙，忽然而已。」—— 莊子", "emotion": "難過"},
    {"text": "「憂鬱是我的貼身伴侶，它是我最忠誠的情人。」—— 齊克果", "emotion": "難過"},
    {"text": "「絕望是走向死亡的疾病（致死的疾病）。」—— 齊克果", "emotion": "難過"},

    # 生氣
    {"text": "「不在沉默中爆發，就在沉默中滅亡。」—— 魯迅", "emotion": "生氣"},
    {"text": "「上帝已死！我們殺了他！」—— 尼采", "emotion": "生氣"},
    {"text": "「個人一直都在與部落搏鬥，以避免被其淹沒。」—— 尼采", "emotion": "生氣"},
    {"text": "「不聽從公眾輿論，是成就偉業的首要條件。」—— 黑格爾", "emotion": "生氣"},
    {"text": "「悲劇並非善與惡的鬥爭，而是兩種正義（權利）之間不可調和的衝突。」—— 黑格爾", "emotion": "生氣"},
    {"text": "「自願變成一條蠕蟲的人，事後就別抱怨被別人踩在腳下。」—— 康德", "emotion": "生氣"},
    {"text": "「你的行動，要把人當成『目的』，而永遠不要只當成『手段』。」—— 康德", "emotion": "生氣"},
    {"text": "「世界就是地獄，人類既是被折磨的靈魂，又是折磨別人的惡魔。」—— 叔本華", "emotion": "生氣"},
    {"text": "「群眾的頭腦不配稱為思考的場所，那裡裝滿了偏見與盲從。」—— 叔本華", "emotion": "生氣"},
    {"text": "「口言善，身行惡，國之妖也。」—— 荀子", "emotion": "生氣"},
    {"text": "「庸眾駑馬，皆自以為有餘，此天下之大患也。」—— 荀子", "emotion": "生氣"},
    {"text": "「竊鉤者誅，竊國者諸侯。」—— 莊子", "emotion": "生氣"},
    {"text": "「聖人不死，大盜不止。」—— 莊子", "emotion": "生氣"},
    {"text": "「群眾即是謊言。」—— 齊克果", "emotion": "生氣"},
    {"text": "「現代人最卑鄙的地方，就是用虛假的群體感來逃避個人的責任。」—— 齊克果", "emotion": "生氣"},

    # 煩躁
    {"text": "「人生是一團慾望，滿足便無聊，不滿足便痛苦。」—— 叔本華", "emotion": "煩躁"},
    {"text": "「沒有事實，只有詮釋。」—— 尼采", "emotion": "煩躁"},
    {"text": "「與怪龍搏鬥的人，要小心自己也變成怪龍。」—— 尼采", "emotion": "煩躁"},
    {"text": "「矛盾是一切運動和生命力的根源。」—— 黑格爾", "emotion": "煩躁"},
    {"text": "「真理是全體。」—— 黑格爾", "emotion": "煩躁"},
    {"text": "「沒有內容的思想是空洞的，沒有概念的直覺是盲目的。」—— 康德", "emotion": "煩躁"},
    {"text": "「沒有理論的經驗是盲目的，但沒有經驗的理論僅僅是智力遊戲。」—— 康德", "emotion": "煩躁"},
    {"text": "「智力越高的人，對噪音的忍受力就越低，這會打斷他們的思考靈感。」—— 叔本華", "emotion": "煩躁"},
    {"text": "「當我們擺脫了痛苦，無聊隨即襲來；我們就在這兩端痛苦地拉扯。」—— 叔本華", "emotion": "煩躁"},
    {"text": "「人生而有欲，欲而不得，則不能無求，求而無度量分界，則不能不爭，爭則亂。」—— 荀子", "emotion": "煩躁"},
    {"text": "「凡人之患，蔽於一曲，而闇於大理。」—— 荀子", "emotion": "煩躁"},
    {"text": "「相呴以濕，相濡以沫，不如相忘於江湖。」—— 莊子", "emotion": "煩躁"},
    {"text": "「吾生也有涯，而知也無涯。以有涯隨無涯，殆已！」—— 莊子", "emotion": "煩躁"},
    {"text": "「焦慮是自由帶來的眩暈。」—— 齊克果", "emotion": "煩躁"},
    {"text": "「最痛苦的矛盾，莫過於你既渴望被理解，又害怕被人看穿。」—— 齊克果", "emotion": "煩躁"},
]

RAW_Q2_ENVIRONMENTS = [
    # 開心
    {"text": "春日文學院的杜鵑花海", "emotion": "開心"},
    {"text": "新體育館打贏球的絕殺時刻", "emotion": "開心"},
    {"text": "秋季初晴朗的椰林大道", "emotion": "開心"},
    {"text": "正午活大找到空桌的熱鬧午餐", "emotion": "開心"},
    {"text": "期末考結束的總圖前廣場", "emotion": "開心"},
    # 生氣
    {"text": "七月烈日下的水源腳踏車拖吊場", "emotion": "生氣"},
    {"text": "早八快遲到時舟山路的腳踏車大塞車", "emotion": "生氣"},
    {"text": "大雨中小福外卡死的泥濘車陣", "emotion": "生氣"},
    {"text": "快遲到時博雅教學館超載的電梯", "emotion": "生氣"},
    {"text": "深夜宿舍隔壁傳來捶牆的嘶吼聲", "emotion": "生氣"},
    # 難過
    {"text": "寒流冬雨中的醉月湖亭子", "emotion": "難過"},
    {"text": "凌晨起霧的總圖後草皮", "emotion": "難過"},
    {"text": "陰雨綿綿昏暗的文學院長廊", "emotion": "難過"},
    {"text": "週末傍晚空蕩蕩的共同教學館", "emotion": "難過"},
    {"text": "冬夜冷雨中的公館捷運站出口", "emotion": "難過"},
    # 煩躁
    {"text": "午後雷陣雨濕黏悶熱的椰林大道", "emotion": "煩躁"},
    {"text": "期中考週社科院圖書館被噪音干擾的座位", "emotion": "煩躁"},
    {"text": "尖峰時段學餐桌面凌亂黏膩的座位", "emotion": "煩躁"},
    {"text": "初夏悶熱且冷氣狂吵的共同教室", "emotion": "煩躁"},
    {"text": "下班時間機車廢氣刺鼻的公館圓環", "emotion": "煩躁"},
]

RAW_Q3_COLORS = [
    # 開心
    {"text": "正午烈日般的亮橘色", "emotion": "開心"},
    {"text": "明亮的暖黃色", "emotion": "開心"},
    {"text": "充滿活力的螢光綠", "emotion": "開心"},
    # 生氣
    {"text": "帶有壓迫感的警示紅", "emotion": "生氣"},
    {"text": "邊緣銳利的螢光洋紅", "emotion": "生氣"},
    {"text": "燃燒的烈焰紅", "emotion": "生氣"},
    # 難過
    {"text": "深邃的憂鬱藍", "emotion": "難過"},
    {"text": "能吸走光線的幽暗深藍", "emotion": "難過"},
    {"text": "帶著灰階的霧霾藍", "emotion": "難過"},
    # 煩躁
    {"text": "混濁的暗綠色", "emotion": "煩躁"},
    {"text": "令人疲勞的混濁黃綠", "emotion": "煩躁"},
    {"text": "帶有雜訊感的暗紫色", "emotion": "煩躁"},
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
}

EMOTIONS = ["開心", "難過", "生氣", "煩躁"]  

class QuizEngine:
    def __init__(self):
        self.current_q1 = self._sample_one_per_emotion(RAW_Q1_QUOTES)
        self.current_q2 = self._sample_one_per_emotion(RAW_Q2_ENVIRONMENTS)
        self.current_q3 = self._sample_one_per_emotion(RAW_Q3_COLORS)

# class QuizEngine:
#     def __init__(self):
#         self.current_q1 = self._shuffle(RAW_Q1_QUOTES)
#         self.current_q2 = self._shuffle(RAW_Q2_ENVIRONMENTS)
#         self.current_q3 = self._shuffle(RAW_Q3_COLORS)

    # def _shuffle(self, pool: list) -> list:
    #     copy = pool.copy()
    #     random.shuffle(copy)
    #     return copy
    def _sample_one_per_emotion(self, pool: list) -> list:
        picked = []
        for emotion in EMOTIONS:
            candidates = [item for item in pool if item["emotion"] == emotion]
            if candidates:
                picked.append(random.choice(candidates))
        random.shuffle(picked)
        return picked

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