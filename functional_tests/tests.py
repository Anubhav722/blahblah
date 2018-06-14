from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get('http://localhost:8000/resume/')
        # time.sleep(1)
        self.assertIn('Upload Resume', self.browser.title)
        # self.fail('Finish the Test')
