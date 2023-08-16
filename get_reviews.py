from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import time
import json
from hashlib import md5
import os
import traceback
from datetime import datetime

from loguru import logger
logger.add(f'logs/{datetime.now():%Y-%m-%d-%H-%M-%S}.log')

options = Options()
# options.add_argument('-headless')
proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': '127.0.0.1:7890',
    'sslProxy': '127.0.0.1:7890',
})
options.proxy = proxy
options.set_preference('permissions.default.image', 2)
options.set_preference('permissions.default.stylesheet', 2)
driver = Firefox(options=options)
driver.implicitly_wait(1)

RATING_MAP = {
    '0.00': 0,
    '0.50': 0.5,
    '1.00': 1,
    '1.50': 1.5,
    '2.00': 2,
    '2.50': 2.5,
    '3.00': 3,
    '3.50': 3.5,
    '4.00': 4,
    '4.50': 4.5,
    '5.00': 5,
}

def parse_page(url: str) -> tuple[list[tuple[float, str]], bool, str]:
    global driver
    driver.get(url)
    time.sleep(1)
    
    title = driver.title
    while not title.startswith("Reviews"):
        logger.warning(f"IP blocked, sleep 10s")
        time.sleep(10)
        
        driver.quit()
        driver = Firefox(options=options)
        driver.implicitly_wait(1)
        
        driver.get(url)
        title = driver.title
    
    next_btn = driver.find_elements(by=By.CSS_SELECTOR, value='a.navlinknext')
    has_next = len(next_btn) > 0
    
    container = driver.find_element(by=By.CLASS_NAME, value='page_section')
    reviews = container.find_elements(by=By.CLASS_NAME, value='review')
    logger.debug(f"got {len(reviews)} reviews in this page")
    
    data = []
    for review in reviews:
        try:
            try:
                rating_ele = review.find_element(by=By.CLASS_NAME, value='review_rating').find_element(by=By.TAG_NAME, value='img')
                rating = rating_ele.get_attribute('title')[: 4]
                if rating not in RATING_MAP:
                    breakpoint()
                rating = RATING_MAP[rating]
            except NoSuchElementException as e:
                logger.warning(f"no rating")
                continue
            
            quote_ele = review.find_element(by=By.CLASS_NAME, value='review_body')
            quote = quote_ele.text
            
            if len(quote) <= 30:
                logger.warning(f"quote too short: {quote}")
                continue
            
            short = quote if len(quote) <= 20 else quote[:20] + '...'
            logger.debug(f"{rating} => {short}")
            
            data.append((rating, quote))
        except Exception as e:
            logger.error(traceback.format_exc())
            breakpoint()
    
    logger.info(f"got {len(data)} reviews of {title}")
    return data, has_next, title
        

@logger.catch(reraise=True)
def fetch(url: str, save_path: str, max_num: int = 200):
    # driver.get(url)
    # title = driver.title
    # logger.info(f"fetching {title}")
    title = None
    logger.info(f"fetching {url}")
    
    results = []
    for i in range(100):
        data, has_next, title_ = parse_page(f"{url}/reviews/{i+1}/")
        if title is None:
            title = title_.split()[2]
        results.extend(data)
        if not has_next:
            logger.info("No more pages")
            break
        if len(results) >= max_num:
            logger.info("Max num reached")
            break
    logger.info(f"got {len(results)} reviews of {title}")
    json.dump({
        'title': title,
        'url': url,
        'reviews': results,
    }, open(save_path, 'w'), indent=2)

if __name__ == '__main__':
    albums = json.load(open('album_urls.json', 'r', encoding='utf-8'))
    # albums = ['https://rateyourmusic.com/release/ep/newjeans/get-up'] # for test
    
    for i, album in enumerate(albums):
        short = md5(album.encode('utf-8')).hexdigest()
        save_path = f"data/{short}.json"
        if os.path.exists(save_path):
            logger.warning(f"skip {album}")
            continue
        fetch(album, save_path)
    
    # driver.quit()