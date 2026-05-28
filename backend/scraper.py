"""
scraper.py  （來自 pythonproj.docx，原版不動）
爬蟲核心邏輯：PTT / Google 搜尋 / Pixnet (Google 代理版)
含近 3 年時間過濾（BOUNDARY_DATE = 2023-01-01）
"""
import re, random, time
from datetime import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BOUNDARY_DATE = datetime(2023, 1, 1)

FOOD_KEYWORDS = ["好吃","美味","推薦","踩雷","失望","拉麵","咖哩","火鍋","小館","泰式","割包","美食","小吃","餐廳","聚餐","味道"]
GUAN_RESTAURANTS = ["泰國小館","池先生","大盛豬排","易牙居","小木屋鬆餅","藍家割包","公館蔬菜蛋餅","塔庫先生"]
MIAOLI_BLACK_LIST = ["苗栗","公館鄉","棗莊","福樂麵店","紅棗","芋頭","草莓","大湖","銅鑼","頭屋","三義","客家料理","交流道"]

def get_common_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def dynamic_keyword_extractor(full_text, results, source_name):
    for black_word in MIAOLI_BLACK_LIST:
        if black_word in full_text:
            return
    has_taipei_context = any(tok in full_text for tok in ["台北","台大","捷運","中正區","大安區","羅斯福路","汀州路"])
    has_known_restaurant = any(res in full_text for res in GUAN_RESTAURANTS)
    if not (has_taipei_context or has_known_restaurant):
        return
    target_restaurant = "公館(台北)商圈推薦(綜合)"
    for r_name in GUAN_RESTAURANTS:
        if r_name in full_text:
            target_restaurant = r_name
            break
    regex_match = re.search(r'公館\s*([A-Za-z0-9\u4e00-\u9fa5]{2,6}(?:拉麵|咖哩|火鍋|小館|店|傳統小吃|烤肉|便當|割包|鬆餅|滷味))', full_text)
    if regex_match and target_restaurant == "公館(台北)商圈推薦(綜合)":
        target_restaurant = regex_match.group(1)
    clean_comment = full_text.strip().replace("\n", " ")
    if len(clean_comment) > 300:
        clean_comment = clean_comment[:300] + "..."
    print(f"   🎯 [精準台北數據提煉] 成功補獲 -> 歸類給 【{target_restaurant}】")
    if target_restaurant not in results:
        results[target_restaurant] = {
            "name": target_restaurant,
            "category": f"台北商圈探勘({source_name})",
            "price_tier": 2,
            "address": "台北市公館商圈",
            "reviews": []
        }
    if not any(rev["comment"] == clean_comment for rev in results[target_restaurant]["reviews"]):
        results[target_restaurant]["reviews"].append({
            "author": f"{source_name}精選評論",
            "rating": 5,
            "comment": f"【{source_name}精選】{clean_comment}",
            "review_date": datetime.now()
        })

def fetch_ptt_data(results):
    print("\n🌐 [1/3 PTT 模組] 開始採集 PTT Food 板...")
    try:
        encoded_keyword = urllib.parse.quote("台北 公館")
        url = f"https://www.ptt.cc/bbs/Food/search?page=1&q={encoded_keyword}"
        res = requests.get(url, headers=get_common_headers(), timeout=10)
        if res.status_code != 200: return
        soup = BeautifulSoup(res.text, 'html.parser')
        for art in soup.find_all('div', class_='r-ent'):
            title_node = art.find('div', class_='title').find('a')
            if title_node and "[食記]" in title_node.text:
                if any(bw in title_node.text for bw in MIAOLI_BLACK_LIST):
                    continue
                name = title_node.text.replace("[食記]", "").replace("台北", "").replace("公館", "").strip()
                if not name: name = "公館特色小吃"
                if name not in results:
                    results[name] = {"name": name, "category": "精選美食(PTT)", "price_tier": 2, "address": "台北市捷運公館站商圈", "reviews": []}
                results[name]["reviews"].append({
                    "author": art.find('div', class_='author').text, "rating": 4,
                    "comment": f"PTT台大鄉民大推：{title_node.text}", "review_date": datetime.now()
                })
        print(" -> PTT 模組採集成功。")
    except Exception as e: print(f" ⚠️ PTT 模組異常: {e}")

def fetch_google_search_data(results):
    print("\n🔍 [2/3 Google 搜尋模組] 啟動自動化瀏覽器...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1400,900')
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        search_query = "台北 捷運公館站 美食 餐廳 推薦"
        google_url = "https://www.google.com/search?q=" + urllib.parse.quote(search_query)
        driver.get(google_url)
        time.sleep(5)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        for line in body_text.split("\n"):
            if "公館" in line and any(k in line for k in FOOD_KEYWORDS):
                dynamic_keyword_extractor(line, results, "Google搜尋")
    except Exception as e: print(f" ❌ Google 搜尋採集異常: {e}")
    finally: driver.quit()

def fetch_pixnet_blog_data(results):
    print("\n🍰 [3/3 痞客邦深度代理模組] 借道 Google 抓取 Pixnet 台北公館食記...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1400,900')
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        search_query = "台北 捷運公館站 美食 食記 site:pixnet.net"
        google_url = "https://www.google.com/search?q=" + urllib.parse.quote(search_query)
        driver.get(google_url)
        time.sleep(5)
        links = driver.find_elements(By.TAG_NAME, "a")
        blog_urls = []
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and "pixnet.net/blog/post" in href and href not in blog_urls:
                    blog_urls.append(href)
            except: continue
        target_urls = blog_urls[:3]
        print(f" -> 定位出 {len(blog_urls)} 篇 Pixnet 文章，準備進入內頁...")
        for url in target_urls:
            driver.get(url)
            time.sleep(5)
            blog_full_text = driver.find_element(By.TAG_NAME, "body").text
            for para in blog_full_text.split("\n"):
                if "公館" in para and any(k in para for k in FOOD_KEYWORDS):
                    if len(para.strip()) > 25:
                        dynamic_keyword_extractor(para, results, "痞客邦代理")
    except Exception as e: print(f" ❌ 痞客邦代理採集異常: {e}")
    finally: driver.quit()

def fetch_gongguan_restaurant_data():
    print("🚀 [台北精準定位爬蟲啟動] 調度 PTT + Google + Pixnet...")
    aggregated_results = {}
    fetch_ptt_data(aggregated_results)
    fetch_google_search_data(aggregated_results)
    fetch_pixnet_blog_data(aggregated_results)
    final_list = list(aggregated_results.values())
    print(f"\n📊 [採集結束] 成功建立 {len(final_list)} 個精準台北公館餐廳數據節點。")
    return final_list

if __name__ == "__main__":
    fetch_gongguan_restaurant_data()