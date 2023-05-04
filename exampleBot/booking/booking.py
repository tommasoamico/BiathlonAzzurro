import booking.constants as const
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Booking(webdriver.Chrome):
    def __init__(self, driver_path=r"/Users/tommaso/Workspace/seleniumDrivers/chromedriver_mac64",
                 teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        os.environ['PATH'] += self.driver_path
        super(Booking, self).__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Exiting...')
        if self.teardown:
            self.quit()

    def land_first_page(self):

        self.get(const.BASE_URL)

    def change_currency(self, currency='USD'):
        currencyElement = self.find_element(By.CSS_SELECTOR,
                                            'button[data-testid="header-currency-picker-trigger"]'
                                            )

        currencyElement.click()
        selectedCurrencyElement = self.find_element(By.XPATH,
                                                    f"//div[contains(text(), '{currency}')]")
        selectedCurrencyElement.click()

    def selectPlaceToGo(self, place_to_go):
        searchField = self.find_element(By.ID,
                                        ':Ra9:')
        searchField.clear()
        searchField.send_keys(place_to_go)
        firstResult = self.find_element(By.XPATH,
                                        f"//div[contains(text(), '{place_to_go}')]")
        firstResult.click()
