from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

def analyze_reviews(comments):
    all_reviews_text = " ".join(comments)

    url = "https://gptproto.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "key"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "Analyze the product reviews and write down its advantages and disadvantages separately. "
                           "Evaluate the product based on these reviews and write down whether "
                           f"it is worth buying or not, justifying your choice. Generate the answer in Russian. {all_reviews_text}"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()

        print(result["choices"][0]["message"]["content"])

    else:
        print(f"Ошибка: {response.status_code}")

def init_webdriver():
    driver = webdriver.Chrome()
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver


def scrolldown(driver, deep):
    for _ in range(deep):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(0.5)

art = "1558640800"
driver = init_webdriver()
driver.get(f"https://www.ozon.ru/product/{art}/?reviewsVariantMode=1")
time.sleep(10)
scrolldown(driver, 50)
time.sleep(10)
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-review-uuid]'))
    )
except Exception as e:
    print("Не дождались загрузки отзывов")


all_comments = []

reviews = driver.find_elements(By.CSS_SELECTOR, '[data-widget="webListReviews"]')

for review in reviews:
    blocks = review.find_element(By.XPATH, './div[last()]')

    triple_blocks = blocks.find_elements(By.XPATH, './div')

    for triple_block in triple_blocks:

        comments = triple_block.find_element(By.XPATH, './div[1]/div[2]/div[2]/div/div')
        text = comments.find_element(By.TAG_NAME, 'span').text
        rating_block = triple_block.find_element(By.XPATH, './div[1]/div[1]/div[2]/div[2]/div')
        rating = rating_block.find_elements(By.TAG_NAME, 'svg')
        try:
            stars = sum(1 for s in rating if "--graphicRating" in s.get_attribute("style"))
        except:
            stars = 0
        print(f"Отзыв: {text}")
        print(f"Оценка: {stars}\n")

        all_comments.append(text)

print(f"\nВсего собрано отзывов: {len(all_comments)}")

analyze_reviews(all_comments)

