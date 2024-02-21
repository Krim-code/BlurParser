import json
import zipfile
from pprint import pprint
from time import sleep, time
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
import os

from selenium.webdriver.common.by import By

PROXY_HOST = '178.130.53.108'
PROXY_PORT = 64468  # Your proxy port
PROXY_USER = '6SnbUcBe'
PROXY_PASS = 'AtcGLZjs'

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"76.0.0"
}
"""

background_js = """
let config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    s = Service(executable_path=os.path.normpath('C://Users//Elros//Documents//reviProjects//BlurParser//utils//chromedriver.exe'))
    driver = webdriver.Chrome(
        service=s,
        options=chrome_options
    )

    return driver


def extract_data_from_a_tag(a_tag):
    arr = []
    # Найти div с классом Text__TextRoot-sc-m23s7f-0 внутри тега a
    div_elements = a_tag.find_elements(By.CLASS_NAME, "Text__TextRoot-sc-m23s7f-0")
    # Извлечь текст из div
    for div in div_elements:
        arr.append(div.text)
    return arr

# Функция для скролла страницы
def scroll_down(driver):
    driver.execute_script('document.querySelector(".interactive").scrollTop += 100000')


def main():
    processed_data = {}
    driver = get_chromedriver(use_proxy=True,
                              user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15')
    driver.get('https://blur.io/collections')
    sleep(2)

    data_list = []
    test = driver.find_element(By.ID,"__next").find_element(By.CLASS_NAME,"index__Layout-sc-1bpwb42-0").find_element(By.ID,"GRID_AREA_COLLECTIONS").find_element(By.CLASS_NAME,"AllCollections__TableRootStyles-sc-csk96n-0 ").find_element(By.CLASS_NAME,"interactive")
    try:
        while True:
            # Найти все теги a с указанным классом
            a_tags = test.find_elements(By.CLASS_NAME, "Link__StyledRouterLink-sc-1xumirv-0")

            for a_tag in a_tags:
                # Извлечь данные из тега a
                extracted_data = extract_data_from_a_tag(a_tag)

                # Обработать текст и добавить в список
                if extracted_data[0] not in processed_data:
                    processed_data[extracted_data[0]] = extracted_data[1:]  # Здесь ты можешь добавить код для обработки текста

            if len(processed_data) >= 1460:
                break
            # Сделать скролл
            scroll_down(driver)
            pprint(processed_data)
            print(len(processed_data))
            # Подождать некоторое время (может потребоваться настроить)



    except KeyboardInterrupt:
        pass
    finally:
        driver.close()
        driver.quit()

    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(processed_data, json_file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()