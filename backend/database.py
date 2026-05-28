from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session, select

# ─────────────────────────────────────────
# 1. 餐廳資料表
# ─────────────────────────────────────────
class Restaurant(SQLModel, table=True):
    id:          Optional[int] = Field(default=None, primary_key=True)
    name:        str           = Field(index=True, unique=True)
    category:    str           # 料理種類，例如：火鍋、泰式、小吃
    price_tier:  int           # 1=低(<150), 2=中(150-350), 3=高(>350)
    address:     str
    latitude:    Optional[float] = None
    longitude:   Optional[float] = None

    # ★ 新增：以逗號分隔的情緒標籤，例如 "開心,平靜"
    # 讓 API 可依使用者問卷情緒結果過濾推薦餐廳
    emotion_tags: Optional[str] = Field(default=None)

    reviews: List["Review"] = Relationship(back_populates="restaurant")


# ─────────────────────────────────────────
# 2. 評論資料表
# ─────────────────────────────────────────
class Review(SQLModel, table=True):
    id:            Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int           = Field(foreign_key="restaurant.id")
    author:        str
    rating:        int
    comment:       str
    review_date:   datetime
    # 由情緒分析模組寫入（可為 None）
    emotion_tag:   Optional[str] = Field(default=None)

    restaurant: Restaurant = Relationship(back_populates="reviews")


# ─────────────────────────────────────────
# 3. 資料庫連線
# ─────────────────────────────────────────
DATABASE_URL = "sqlite:///gongguan_food.db"
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """建立所有資料表（若已存在則略過）"""
    SQLModel.metadata.create_all(engine)


# ─────────────────────────────────────────
# 4. 查詢輔助：依情緒＋預算取得推薦餐廳
# ─────────────────────────────────────────
PRICE_TIER_MAP = {"低": 1, "中": 2, "高": 3}

def get_recommendations(emotion: str, budget: str, limit: int = 5) -> List[Restaurant]:
    """
    依情緒標籤與預算回傳推薦餐廳列表。
    - emotion: "開心" | "生氣" | "難過" | "煩躁" | "平靜"
    - budget:  "低" | "中" | "高"
    """
    price_tier = PRICE_TIER_MAP.get(budget)
    with Session(engine) as session:
        stmt = select(Restaurant)
        results = session.exec(stmt).all()

        filtered = [
            r for r in results
            if (r.emotion_tags and emotion in r.emotion_tags.split(","))
            and (price_tier is None or r.price_tier == price_tier)
        ]
        return filtered[:limit]


if __name__ == "__main__":
    init_db()
    print("Database & Tables created successfully!")