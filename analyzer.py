from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import dearpygui.dearpygui as dpg

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
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-review-uuid]'))
        )
    except Exception as e:
        return 0


def format_gpt_response(text):
    text = text.replace('**', '')

    lines = text.split('. ')

    formatted = []
    for line in lines:
        line = line.strip()
        if line:
            if not line.endswith('.'):
                line = line + '.'
            formatted.append(line)

    return '\n\n'.join(formatted)


def parsing_comments(art):
    all_comments = []

    driver = init_webdriver()
    driver.get(f"https://www.ozon.ru/product/{art}/?reviewsVariantMode=1")

    scrolldown(driver, 50)

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

            all_comments.append(text)

    return all_comments

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

        analysis = result["choices"][0]["message"]["content"]
        return analysis

    else:
        return "Error response"

def button_click():
    art = dpg.get_value("input_field")

    if not art:
        dpg.set_value("result_text", "Введите артикул!")
        return
    dpg.set_value("result_text", "Парсим...")

    all_comments = parsing_comments(art)
    analysis = analyze_reviews(all_comments)
    formatted = format_gpt_response(analysis)
    dpg.set_value("result_text", formatted)


dpg.create_context()

with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/arial.ttf", 20) as default_font:  # Путь к Arial
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font(default_font)

with dpg.window(label="Парсер отзывов с сайта OZON", width=500, height=500):
    dpg.add_text("Введите артикул товара OZON:")
    dpg.add_input_text(tag="input_field", width=200)
    dpg.add_button(label="Спарсить отзывы", callback=button_click)

    dpg.add_text("Результат анализа:", indent=10)
    with dpg.child_window(tag="result_window", width=750, height=400):
        dpg.add_text("", tag="result_text", wrap=750)

dpg.create_viewport(title="Минимальный пример", width=500, height=500)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

