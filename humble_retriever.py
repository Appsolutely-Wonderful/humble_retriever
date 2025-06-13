from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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
HUMBLE_CHOICE_LINKS = "//a[@class='content-choices-footer js-previous-month-link']"
HUMBLE_CHOICE_GAME_TITLE_XPATH = "//div[@class='content-choice-title']"
HUMBLE_CHOICE_MONTH_XPATH = "//h3[@class='content-choices-title']"
HUMBLE_CHOICE_GAME_CONTAINER_FROM_TITLE = "./ancestor::div[contains(@class, 'choice-content')]"
HUMBLE_CHOICE_IMAGE_XPATH_FROM_CONTAINER = ".//img[@class='choice-image']"
HUMBLE_CHOICE_ELEMENT_WITH_MACHINE_NAME = ".//*[@data-machine-name]"
HUMBLE_CHOICE_CUSTOM_INSTRUCTION = ".//div[@class='custom-instruction']"
HUMBLE_MONTHLY_LINKS = "//a[@class='previous-month-product-link-header']"
HUMBLE_MONTHLY_GAME_XPATH = "//a[contains(@class, 'section-name')]"
COOKIE_CONSENT_BTN_XPATH = "//button[@id='onetrust-accept-btn-handler']"
GENRE_XPATH = "//span[@class='genres']"
MODAL_CLOSE_BUTTON = "//a[contains(@class, 'js-close-modal close-modal')]"

class HumbleRetriever:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get(HUMBLE_URL)
        self.driver.implicitly_wait(10) # seconds
        self.consent_to_cookies()
        self.games = {}

    def _get_element(self, xpath):
        """
        Returns a single element based on the given xpath
        """
        return self.driver.find_element(By.XPATH, xpath)

    def _click_login_btn(self):
        btn = self._get_element(LOGIN_BTN_XPATH)
        btn.click()

    def list_all_games(self, username, password):
        self.login(username, password)
        self.navigate_to_humble_choice()
        self.expand_game_months()
        self.retrieve_humble_choice_games()
        self.retrieve_humble_monthly_games()
        self.save_as_json("games.json")

    def save_as_json(self, file):
        with open(file, "w") as fp:
            import json
            json.dump(self.games, fp)

    def login(self, username, password):
        """
        Navigates to the login page and fills out the form
        with the provided username and password
        """
        if "/login" not in self.driver.current_url:
            self._click_login_btn()
        sleep(1)
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

    def consent_to_cookies(self):
        """
        Clicks the cookie consent button if it exists
        """
        try:
            consent_btn = self._get_element(COOKIE_CONSENT_BTN_XPATH)
            while True:
                try:
                    consent_btn.click()
                    break
                except ElementNotInteractableException:
                    sleep(1)
        except NoSuchElementException:
            # If the consent button doesn't exist, continue
            pass

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
        return self.driver.find_elements(By.XPATH, HUMBLE_CHOICE_LINKS)

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

    def get_custom_instruction(self, title_element):
        # Store the original implicit wait time
        original_wait = self.driver.timeouts.implicit_wait
        # Disable implicit wait
        self.driver.implicitly_wait(0)
        instructions = self.driver.find_elements(By.XPATH, HUMBLE_CHOICE_CUSTOM_INSTRUCTION)
        self.driver.implicitly_wait(original_wait)

        if len(instructions) > 0:
            return instructions[0].text
        else:
            return None

    def open_game(self, title_element):
        title_element.click()
        sleep(0.5)

    def close_game(self):
        self.driver.find_element(By.XPATH, MODAL_CLOSE_BUTTON).click()
        sleep(0.5)

    def _get_genres(self, title_element) -> list[str]:
        """
        Opens the game modal, reads the genre, and closes the modal.
        Returns the genre
        """
        genre_element = self.driver.find_element(By.XPATH, GENRE_XPATH)
        genres = list(map(lambda x: x.strip().title(), genre_element.text.split(",")))
        return genres

    def get_choice_image(self, title_element):
        """
        Returns the URL of the game's thumbnail image
        """
        # Navigate to the parent content-choice div, then find the img element
        content_choice = title_element.find_element(By.XPATH, HUMBLE_CHOICE_GAME_CONTAINER_FROM_TITLE)
        img_element = content_choice.find_element(By.XPATH, HUMBLE_CHOICE_IMAGE_XPATH_FROM_CONTAINER)
        return img_element.get_attribute("src")

    def get_direct_link(self, title_element):
        """
        Returns the direct link to the game using data-machine-name attribute
        """
        # Navigate to the parent content-choice div, then find the element with data-machine-name
        content_choice = title_element.find_element(By.XPATH, HUMBLE_CHOICE_GAME_CONTAINER_FROM_TITLE)
        machine_name_element = content_choice.find_element(By.XPATH, HUMBLE_CHOICE_ELEMENT_WITH_MACHINE_NAME)
        machine_id = machine_name_element.get_attribute("data-machine-name")
        
        # Get the current month and year from the page
        month_text = self.get_choice_month()
        # Extract month and year from text like "December 2023 Humble Choice"
        month_name = month_text.split(" ")[0].lower()
        year = month_text.split(" ")[1]
        return f"https://www.humblebundle.com/membership/{month_name}-{year}/{machine_id}"

    def get_choice_titles(self):
        title_spans = self.driver.find_elements(By.XPATH, HUMBLE_CHOICE_GAME_TITLE_XPATH)
        games = []
        for title in title_spans:
            self.open_game(title)
            genres = self._get_genres(title)
            instructions = self.get_custom_instruction(title)
            self.close_game()
            img = self.get_choice_image(title)
            direct_link = self.get_direct_link(title)
            games.append({"name": title.text.title(), "genres": genres, "image": img, "link": direct_link, "instructions": instructions})
        return games

    def get_monthly_links(self):
        return self.driver.find_elements(By.XPATH, HUMBLE_MONTHLY_LINKS)

    def get_monthly_titles(self):
        # Enforce an implicit delay for the page to load
        self.driver.find_elements(By.XPATH, HUMBLE_MONTHLY_GAME_XPATH)
        js = """elements = document.getElementsByClassName('section-name')
                var results = []
                for (let i = 0; i < elements.length; i++) {{
                    let el = elements[i]
                    results.push({"name": el.textContent.trim(), "genres": [], "image": null, "link": "www.humblebundle.com" + window.location.pathname, "instructions": null})
                }}
                return results"""
        return self.driver.execute_script(js)

    def _switch_to_window_index(self, idx):
        self.driver.switch_to.window(self.driver.window_handles[idx])

    def retrieve_humble_choice_games(self):
        import pdb; pdb.set_trace()
        # Get current month games
        titles = self.get_choice_titles()
        month = self.get_choice_month()
        self.games[month] = titles

        # Get past month games
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

if __name__ == "__main__":
  import getpass
  driver = HumbleRetriever()
  game_list = driver.list_all_games(input("Username: "), getpass.getpass("Password: "))
