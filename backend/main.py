"""
main.py  （來自 pythonproj.docx，原版不動）
ETL 流程串接：爬蟲 → 時間過濾 → 寫入資料庫
"""
from datetime import datetime
from sqlmodel import Session, select
from database import init_db, engine, Restaurant, Review
from scraper import fetch_gongguan_restaurant_data
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gong-food-guan.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    print("[STEP 1] 初始化資料庫...")
    init_db()

    print("\n[STEP 2] 執行爬蟲與時間過濾...")
    scraped_data = fetch_gongguan_restaurant_data()

    print("\n[STEP 3] 開始將合格資料寫入資料庫...")
    with Session(engine) as session:
        for item in scraped_data:
            statement = select(Restaurant).where(Restaurant.name == item["name"])
            existing_restaurant = session.exec(statement).first()

            if not existing_restaurant:
                db_restaurant = Restaurant(
                    name=item["name"],
                    category=item["category"],
                    price_tier=item["price_tier"],
                    address=item["address"],
                )
                session.add(db_restaurant)
                session.commit()
                session.refresh(db_restaurant)
            else:
                db_restaurant = existing_restaurant

            # 相容新版 'reviews' 與舊版 'cleaned_reviews'
            reviews_list = item.get("reviews") or item.get("cleaned_reviews") or []

            for rev in reviews_list:
                review_statement = select(Review).where(
                    Review.restaurant_id == db_restaurant.id,
                    Review.author == rev["author"],
                )
                existing_review = session.exec(review_statement).first()

                if not existing_review:
                    final_date = datetime.now()
                    if "review_date" in rev:
                        if isinstance(rev["review_date"], datetime):
                            final_date = rev["review_date"]
                        else:
                            final_date = datetime.strptime(str(rev["review_date"]), "%Y-%m-%d")
                    elif "date_str" in rev:
                        final_date = datetime.strptime(rev["date_str"], "%Y-%m-%d")

                    db_review = Review(
                        restaurant_id=db_restaurant.id,
                        author=rev["author"],
                        rating=rev["rating"],
                        comment=rev["comment"],
                        review_date=final_date,
                    )
                    session.add(db_review)

        session.commit()

    print("\n🎉 資料庫寫入完成！近 3 年公館美食數據已就緒。")
    print("\n[驗證] 目前資料庫內的真實資料：")
    with Session(engine) as session:
        restaurants = session.exec(select(Restaurant)).all()
        for r in restaurants:
            print(f"餐廳：{r.name} ({r.category})")
            print(f"  └ 成功存入 {len(r.reviews)} 則近 3 年的鄉民評論。")


if __name__ == "__main__":
    main()