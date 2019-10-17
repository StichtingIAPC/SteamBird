from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag

from steambird.tests.helpers.webdriver import get_webdriver


@tag('browser', 'any-browser')
class HomepageTest(StaticLiveServerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.driver = get_webdriver()

    def tearDown(self) -> None:
        super().tearDown()
        self.driver.close()

    def test_screenshot(self):
        driver = self.driver

        driver.get("{base}/".format(
            base=self.live_server_url
        ))

        # Test whether the homepage can be reached.
        driver.find_element_by_class_name("navbar")
