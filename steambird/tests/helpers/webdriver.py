import os

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities


def get_webdriver():
    type = os.getenv('SELENIUM_DRIVER')
    if type == 'FIREFOX':
        return webdriver.Firefox()
    elif type == 'CHROME':
        return webdriver.Chrome()
    elif type == 'REMOTE':
        host = os.getenv('SELENIUM_HOST', '127.0.0.1')
        port = os.getenv('SELENIUM_PORT', '4444')
        type = os.getenv('SELENIUM_REMOTE_TYPE', 'CHROME')

        capabilities = DesiredCapabilities.__dict__[type]

        return webdriver.Remote(
            command_executor='http://{}:{}/wd/hub'.format(host, port),
            desired_capabilities=capabilities)
    elif type == 'FIREFOX_LOCAL_HEADLESS':
        from selenium.webdriver.firefox.options import Options

        options = Options()
        options.headless = True

        capabilities = webdriver.DesiredCapabilities().FIREFOX
        capabilities["marionette"] = True

        return webdriver.Firefox(options=options, capabilities=capabilities)
    elif type == 'CHROME_LOCAL_HEADLESS':
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Chrome(options=options)

    raise EnvironmentError('Environment did not define SELENIUM_DRIVER')
