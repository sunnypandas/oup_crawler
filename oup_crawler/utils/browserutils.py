import os
import platform
import random
import sys
import time
import zipfile

from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium import webdriver

os.chdir(sys.path[0])

def get_browser(log=None, proxy=None):
    executable_path = '/usr/bin/chromedriver'  # 设置启动驱动
    if platform.system() == 'Darwin':
        executable_path = '../../chromedriver'
    chrome_options = webdriver.ChromeOptions()
    if proxy != None:
        p = random.choice(proxy)
        type = p.get('type')
        if type == 'bearer':
            log.logger.info('use bearer proxy: %s', str(p.get('api_url')))
            secret = p.get('secret')
            chrome_options.add_argument('--proxy-server=%s' % str(p.get('api_url')))  # 代理
            def interceptor(request):
                del request.headers['Authorization']
                request.headers['Authorization'] = ''.join(["Bearer ", str(secret)])
            if secret != None:
                chrome_options.request_interceptor = interceptor
        elif type == 'basic':
            log.logger.info('use basic proxy: %s:%s', p.get('host'), p.get('port'))
            PROXY_HOST = p.get('host')  # rotating proxy or host
            PROXY_PORT = int(p.get('port'))  # port
            PROXY_USER = p.get('username')  # username
            PROXY_PASS = p.get('password')  # password
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
                    "minimum_chrome_version":"22.0.0"
                }
                """

            background_js = """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                        singleProxy: {
                            scheme: "http",
                            host: "%s",
                            port: parseInt(%s)
                        },
                        bypassList: []
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
            pluginfile = './proxy_auth_plugin.zip'
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            chrome_options.add_extension(pluginfile)
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    # chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--profile-directory=Default')
    # chrome_options.add_argument("--incognito")
    # chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(executable_path), options=chrome_options)
    driver.delete_all_cookies()
    driver.set_window_size(800, 800)
    driver.set_window_position(0, 0)
    driver.set_page_load_timeout(30)
    # ua = UserAgent()
    # chrome_options.add_argument(f'user-agent={ua.random}')
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver

def solve_blocked(log=None, driver=None):
    if 'Access to this page has been denied' in driver.title:
        log.logger.warning('Access to this page has been denied')
        driver.quit()
        time.sleep(600)

if __name__ == '__main__':
    get_browser()