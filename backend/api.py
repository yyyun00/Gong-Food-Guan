# from contextlib import asynccontextmanager
# from typing import Optional

# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# from database import init_db, get_recommendations, Restaurant, Session, engine, select
# from quiz import generate_quiz, evaluate_answers


# # ─────────────────────────────────────────
# # 啟動時初始化資料庫
# # ─────────────────────────────────────────
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     init_db()
#     yield


# app = FastAPI(title="公館美食地圖 API", lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # Next.js dev server
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ─────────────────────────────────────────
# # Schema
# # ─────────────────────────────────────────
# class QuizSubmitRequest(BaseModel):
#     # 每題的作答：選項文字對應的 emotion，例如 ["開心", "平靜", "開心"]
#     emotions: list[str]
#     budget: str  # "低" | "中" | "高"


# class RestaurantOut(BaseModel):
#     id: int
#     name: str
#     category: str
#     price_tier: int
#     address: str
#     latitude: Optional[float]
#     longitude: Optional[float]
#     emotion_tags: Optional[str]

#     model_config = {"from_attributes": True}


# class QuizSubmitResponse(BaseModel):
#     final_emotion: str
#     budget: str
#     recommendations: list[RestaurantOut]


# # ─────────────────────────────────────────
# # 問卷端點
# # ─────────────────────────────────────────
# @app.get("/quiz/questions")
# def get_questions():
#     """
#     產生一份三題的心情問卷，每次都會重新隨機抽題。
#     前端應在使用者開始測驗時呼叫。
#     """
#     return {"questions": generate_quiz()}


# @app.post("/quiz/submit", response_model=QuizSubmitResponse)
# def submit_quiz(body: QuizSubmitRequest):
#     """
#     接收三題情緒作答 + 預算，回傳情緒判定結果與推薦餐廳。
#     """
#     valid_emotions = {"開心", "生氣", "難過", "煩躁", "平靜"}
#     valid_budgets  = {"低", "中", "高"}

#     if len(body.emotions) != 3:
#         raise HTTPException(status_code=422, detail="emotions 必須包含 3 個值")
#     if not all(e in valid_emotions for e in body.emotions):
#         raise HTTPException(status_code=422, detail=f"emotions 只能是 {valid_emotions}")
#     if body.budget not in valid_budgets:
#         raise HTTPException(status_code=422, detail=f"budget 只能是 {valid_budgets}")

#     final_emotion = evaluate_answers(body.emotions)
#     recs = get_recommendations(final_emotion, body.budget)

#     return QuizSubmitResponse(
#         final_emotion=final_emotion,
#         budget=body.budget,
#         recommendations=[RestaurantOut.model_validate(r) for r in recs],
#     )


# # ─────────────────────────────────────────
# # 餐廳瀏覽端點
# # ─────────────────────────────────────────
# @app.get("/restaurants", response_model=list[RestaurantOut])
# def list_restaurants(
#     emotion: Optional[str] = Query(default=None, description="情緒過濾，例如 開心"),
#     budget:  Optional[str] = Query(default=None, description="預算過濾：低/中/高"),
# ):
#     """列出所有餐廳，可依情緒與預算過濾。"""
#     if emotion or budget:
#         results = get_recommendations(emotion or "", budget or "")
#         # 如果只過濾其中一個條件，fallback 取全部再過濾
#         if not emotion:
#             price_map = {"低": 1, "中": 2, "高": 3}
#             tier = price_map.get(budget)
#             with Session(engine) as session:
#                 all_r = session.exec(select(Restaurant)).all()
#                 results = [r for r in all_r if tier is None or r.price_tier == tier]
#         return [RestaurantOut.model_validate(r) for r in results]

#     with Session(engine) as session:
#         all_restaurants = session.exec(select(Restaurant)).all()
#     return [RestaurantOut.model_validate(r) for r in all_restaurants]


# # ─────────────────────────────────────────
# # 管理端點：觸發爬蟲
# # ─────────────────────────────────────────
# @app.post("/admin/scrape")
# def trigger_scrape():
#     """
#     手動觸發爬蟲並將結果寫入資料庫。
#     建議搭配 API key 保護此端點（生產環境請加驗證）。
#     """
#     try:
#         # 延遲引入，避免 scraper 依賴影響一般啟動
#         from main import main as run_etl
#         run_etl()
#         return {"status": "ok", "message": "爬蟲執行完畢，資料已寫入資料庫。"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

"""
api.py
FastAPI 後端（配合新版 QuizEngine）

流程：
  1. GET  /quiz/questions          → 產生問卷，回傳選項文字（不含情緒）
  2. POST /quiz/check              → 傳索引，回傳是否觸發第四題
  3. POST /quiz/recommend          → 傳最終情緒＋預算，回傳推薦餐廳
  4. GET  /restaurants             → 列出資料庫所有餐廳
  5. POST /admin/scrape            → 觸發爬蟲
"""

import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, engine, Restaurant, Session, select
from quiz import QuizEngine

# ── 每個 session 各自一份 QuizEngine（存在記憶體，不跨 session）
_sessions: dict[str, QuizEngine] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="公館美食地圖 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Schema
# ─────────────────────────────────────────
class CheckRequest(BaseModel):
    session_id: str
    idx1: int
    idx2: int
    idx3: int

class RecommendRequest(BaseModel):
    session_id: str
    final_emotion: str  # 來自第四題選擇，或 check 直接判定的情緒
    budget: str         # "低" | "中" | "高"

class RestaurantOut(BaseModel):
    id: int
    name: str
    category: str
    price_tier: int
    address: str
    emotion_tags: Optional[str]
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────
# 問卷端點
# ─────────────────────────────────────────
@app.get("/quiz/questions")
def get_questions():
    """建立新的 QuizEngine session，回傳三道題選項。"""
    session_id = str(uuid.uuid4())
    engine_instance = QuizEngine()
    _sessions[session_id] = engine_instance
    return {
        "session_id": session_id,
        "questions": engine_instance.get_questions(),
    }


@app.post("/quiz/check")
def check_flow(body: CheckRequest):
    """
    接收三題索引，解碼情緒，判斷是否需要第四題。
    回傳：
      trigger_q4=False → { trigger_q4, determined_emotion }
      trigger_q4=True  → { trigger_q4, q4_options }
    """
    engine_instance = _sessions.get(body.session_id)
    if not engine_instance:
        raise HTTPException(status_code=404, detail="session 不存在，請重新取得問卷")

    emotions = engine_instance.decode_emotions(body.idx1, body.idx2, body.idx3)
    result = engine_instance.check_flow(emotions)
    return result


@app.post("/quiz/recommend")
def recommend(body: RecommendRequest):
    """依最終情緒＋預算回傳推薦餐廳名稱。"""
    valid_emotions = {"開心", "難過", "生氣", "煩躁", "平靜", "都可以"}
    valid_budgets  = {"低", "中", "高"}

    if body.final_emotion not in valid_emotions:
        raise HTTPException(status_code=422, detail=f"情緒需為 {valid_emotions}")
    if body.budget not in valid_budgets:
        raise HTTPException(status_code=422, detail=f"預算需為 {valid_budgets}")

    engine_instance = _sessions.get(body.session_id)
    if not engine_instance:
        raise HTTPException(status_code=404, detail="session 不存在，請重新取得問卷")

    name = engine_instance.fetch_restaurant(body.final_emotion, body.budget)
    if not name:
        return {"restaurant_name": None, "message": f"目前【{body.final_emotion}-{body.budget}】池為空"}

    # 從資料庫查詢完整資料（若有的話）
    with Session(engine) as s:
        r = s.exec(select(Restaurant).where(Restaurant.name == name)).first()

    return {
        "restaurant_name": name,
        "detail": RestaurantOut.model_validate(r) if r else None,
    }


# ─────────────────────────────────────────
# 餐廳瀏覽
# ─────────────────────────────────────────
@app.get("/restaurants", response_model=list[RestaurantOut])
def list_restaurants():
    with Session(engine) as s:
        return [RestaurantOut.model_validate(r) for r in s.exec(select(Restaurant)).all()]


# ─────────────────────────────────────────
# 管理：觸發爬蟲
# ─────────────────────────────────────────
@app.post("/admin/scrape")
def trigger_scrape():
    try:
        from main import main as run_etl
        run_etl()
        return {"status": "ok", "message": "爬蟲執行完畢，資料已寫入資料庫。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))