from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By

import time
import json

from loguru import logger

options = Options()
# options.add_argument('-headless')
proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': '127.0.0.1:7890',
    'sslProxy': '127.0.0.1:7890',
})
options.proxy = proxy
driver = Firefox(options=options)
driver.implicitly_wait(10)

@logger.catch
def main(num: int = 100):
    # driver.get('https://rateyourmusic.com/release/album/pixies/bossanova/reviews/2/')
    driver.get('https://rateyourmusic.com/new-music/')
    # driver.get('https://google.com')
    # print(driver.page_source)
    # with open('test.html', 'w', encoding='utf-8') as f:
    #     f.write(driver.page_source)
    # input()

    sort_btn = driver.find_element(by=By.CLASS_NAME, value='newreleases_sort_btn_date')
    btn = sort_btn
    btn.click()
    time.sleep(1)
    btn.click()
    time.sleep(1)
    
    container = driver.find_element(by=By.ID, value='newreleases_items_container_new_releases_all')
    logger.debug(f"container: {container}")
    
    while True:
        items = container.find_elements(by=By.CLASS_NAME, value='newreleases_itembox')
        logger.debug(f"got {len(items)} items")
        if len(items) >= num:
            break
        
        get_more_btn = driver.find_element(by=By.ID, value='view_more_new_releases_all')
        logger.info(f"click: {get_more_btn}")
        get_more_btn.click()
        time.sleep(1)
    
    results = []
    for item in items:
        link = item.find_element(by=By.XPATH, value='.//div[@class="newreleases_item_artbox"]/a')
        url = link.get_attribute('href')
        
        logger.debug(f"got url: {url}")
        results.append(url)
    
    json.dump(results, open('album_urls.json', 'w', encoding='utf-8'), indent=4)

if __name__ == '__main__':
    main()
    driver.quit()