from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from time import sleep

HUMBLE_URL = "https://humblebundle.com/"
SUBSCRIPTION_URL = HUMBLE_URL + "/subscription/home"
LOGIN_BTN_XPATH = "//a[contains(@class, 'js-account-login')]"
USERNAME_INPUT_XPATH = "//input[@name='username']"
PASSWORD_INPUT_XPATH = "//input[@name='password']"
LOGIN_FORM_SUBMIT_XPATH = "//button[@type='submit']"
VERICIATION_CODE_XPATH = "//input[@name='code']"
USER_AVATAR_BTN_XPATH = "//button[contains(@class, 'js-user-item-dropdown-toggle')]"
SEE_MORE_MONTHS_BTN_XPATH = "//a[contains(@class, 'see-more-months')]"
HUMBLE_CHOICE_LINKS = "//span[contains(@class, 'choices-claimed-or-remaining')]/a"
HUMBLE_CHOICE_GAME_TITLE_XPATH = "//span[@class='content-choice-title']"
HUMBLE_CHOICE_MONTH_XPATH = "//h3[@class='content-choices-title']"
HUMBLE_MONTHLY_LINKS = "//a[@class='previous-month-product-link-header']"
HUMBLE_MONTHLY_GAME_XPATH = "//a[contains(@class, 'section-name')]"

class HumbleChoiceEnumerator:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get(HUMBLE_URL)
        self.driver.implicitly_wait(10) # seconds
        self.games = {}

    def _get_element(self, xpath):
        """
        Returns a single element based on the given xpath
        """
        return self.driver.find_element_by_xpath(xpath)

    def _click_login_btn(self):
        btn = self._get_element(LOGIN_BTN_XPATH)
        btn.click()

    def list_all_games(self, username, password):
        self.login(username, password)
        self.navigate_to_humble_choice()
        self.expand_game_months()
        # self.retrieve_humble_choice_games()
        # self.retrieve_humble_monthly_games()
        # self.print_games()

    def print_games(self):
        for month in self.games:
            print(month.capitalize())
            for game in self.games[month]:
                print("    " + game.capitalize())

    def login(self, username, password):
        """
        Navigates to the login page and fills out the form
        with the provided username and password
        """
        if "/login" not in self.driver.current_url:
            self._click_login_btn()
        username_input = self._get_element(USERNAME_INPUT_XPATH)
        password_input = self._get_element(PASSWORD_INPUT_XPATH)
        submit = self._get_element(LOGIN_FORM_SUBMIT_XPATH)
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit.click()
        self.verify()
        sleep(5)

    def verify(self):
        """
        Requests the verification code interactively
        Humble bundle typically asks for a verification code.
        """
        try:
            verification_input = self._get_element(VERICIATION_CODE_XPATH)
            submit_btn = self._get_element(LOGIN_FORM_SUBMIT_XPATH)
            code = input("Enter verification code: ")
            verification_input.send_keys(code.strip())
            sleep(1)
            submit_btn.click()
        except NoSuchElementException:
            # If they don't ask for verification I guess that's a good thing?
            pass

    def navigate_to_humble_choice(self):
        self.driver.get(SUBSCRIPTION_URL)

    def expand_game_months(self):
        """
        Expand months until they can't be expanded anymore!
        """
        btn = self._get_element(SEE_MORE_MONTHS_BTN_XPATH)
        count = 0
        while True:
            try:
                if "is-hidden" in btn.get_attribute("class"):
                    # if button is hidden for 5 seconds, then consider
                    # expansion is done.
                    if count > 10:
                        return
                    count += 1
                    sleep(1)
                else:
                    btn.click()
                    count = 0
            except NoSuchElementException:
                continue

    def get_choice_links(self):
        """
        Returns a list of the humble choice links on the page
        """
        return self.driver.find_elements_by_xpath(HUMBLE_CHOICE_LINKS)

    def click_element_new_tab(self, element):
        """
        Open a link in a new tab
        """
        element.send_keys(Keys.CONTROL, Keys.ENTER)

    def get_choice_month(self):
        """
        Returns the current page's humble choice month
        """
        return self._get_element(HUMBLE_CHOICE_MONTH_XPATH).text

    def get_choice_titles(self):
        title_spans = self.driver.find_elements_by_xpath(HUMBLE_CHOICE_GAME_TITLE_XPATH)
        games = []
        for title in title_spans:
            games.append(title.text)
        return games

    def get_monthly_links(self):
        return self.driver.find_elements_by_xpath(HUMBLE_MONTHLY_LINKS)

    def get_monthly_titles(self):
        # Enforce an implicit delay for the page to load
        self.driver.find_elements_by_xpath(HUMBLE_MONTHLY_GAME_XPATH)
        js = """elements = document.getElementsByClassName('section-name')
                var results = []
                for (let i = 0; i < elements.length; i++) {{
                    let el = elements[i]
                    results.push(el.textContent.trim())
                }}
                return results"""
        return self.driver.execute_script(js)

    def _switch_to_window_index(self, idx):
        self.driver.switch_to.window(self.driver.window_handles[idx])

    def retrieve_humble_choice_games(self):
        humble_choice_links = self.get_choice_links()
        for link in humble_choice_links:
            # Open new tab
            self.click_element_new_tab(link)
            sleep(1)
            self._switch_to_window_index(1)
            titles = self.get_choice_titles()
            month = self.get_choice_month()
            self.games[month] = titles
            # close tab
            self.driver.close()
            self._switch_to_window_index(0)

    def retrieve_humble_monthly_games(self):
        monthlies = self.get_monthly_links()
        for month_link in monthlies:
            month = month_link.text
            self.click_element_new_tab(month_link)
            self._switch_to_window_index(1)
            titles = self.get_monthly_titles()
            self.games[month] = titles
            self.driver.close()
            self._switch_to_window_index(0)
