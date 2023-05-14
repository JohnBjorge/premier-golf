from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from datetime import datetime


class PremierGolfScraper:
    def __init__(
        self,
        url: str = "https://premier.cps.golf/PremierV3",
        date_search: str = datetime.today(),
        time_search: str = "AnyTime",
        course_search: list = ["Select All"],
        players_search: str = "Any",
        hole_search: str = "18 Holes",
    ) -> None:
        self.url = url
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )
        self.driver.get(url)

        date_search = date_search.strftime("%m/%d/%Y")
        self.date_search = date_search
        self.time_search = time_search  # not being used
        self.course_search = course_search
        self.players_search = players_search  # not being used
        self.hole_search = hole_search
        self.scrape_time = None
        self.tee_times = []

    def navigate_page(self) -> str:
        # select date
        date_box = self.driver.find_element(By.ID, "FromDate")
        self.driver.execute_script(
            "arguments[0].removeAttribute('readonly');", date_box
        )
        date_box.clear()
        date_box.send_keys(self.date_search)
        date_box.send_keys(Keys.ENTER)

        # select courses
        course_dropdown = self.driver.find_element(
            By.CSS_SELECTOR, '[title="Please select a course"]'
        )
        course_dropdown.click()
        course_options = self.driver.find_element(
            By.CSS_SELECTOR,
            "#formWidgetView > div.container-fluid.widget-view.text-center > div.form-group.courseDropDown > div.btn-group.open > ul",
        )
        course_options = course_options.find_elements(By.TAG_NAME, "label")
        for course in course_options:
            if course.text in self.course_search:
                course.click()

        # select hole number
        hole_number_options = self.driver.find_element(By.ID, "holeNumberGroup")
        hole_number_options = self.driver.find_elements(By.TAG_NAME, "button")
        for hole_number in hole_number_options:
            if hole_number.text == self.hole_search:
                hole_number.click()

        # submit search
        submit_button = self.driver.find_element(By.ID, "btnSubmit")
        submit_button.click()

        time_now = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        self.scrape_time = time_now

        # wait for search results
        wait = WebDriverWait(self.driver, 180)
        wait.until(EC.element_to_be_clickable((By.ID, "bodyContent")))

        # click show more times button until all times shown
        while True:
            try:
                wait = WebDriverWait(self.driver, 3)
                wait.until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "spinner"))
                )
                show_more_times_button = wait.until(
                    EC.visibility_of_element_located((By.ID, "btnShowMoreTimes"))
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", show_more_times_button
                )
                wait.until(EC.visibility_of(show_more_times_button))
                show_more_times_button.click()
                wait.until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "spinner"))
                )
            except TimeoutException:  # or TimeoutException
                # If element is not found, break out of the loop
                break

        return self.driver.page_source  # html

    def scrape(self, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")

        body_content = soup.find(id="bodyContent")
        rows = body_content.findAll("div", class_="row")

        tee_time_list = []
        for row in rows:
            tee_time_dict = {}

            tee_time_div = row.find(class_="timeDiv timeDisplay")
            tee_time = tee_time_div.find("span").text

            price = ""
            price_span = row.find(class_="teeTimePrice")
            price_div_h3 = row.find(class_="detailAuctionRow")
            price_h3 = row.find(class_="priceDiv")

            if price_span is not None:
                price = price_span.text
            elif price_div_h3 is not None:
                price_div_h3 = price_div_h3.find("h3")
                price = price_div_h3.text
            else:
                price_h3 = price_h3.find("h3")
                price = price_h3.text

            p_tags = row.findAll("p")
            course = p_tags[0].text
            player_slots = p_tags[1].text

            tee_time_dict["tee_time"] = tee_time
            tee_time_dict["price"] = price
            tee_time_dict["course"] = course
            tee_time_dict["player_slots"] = player_slots

            tee_time_list.append(tee_time_dict)

        self.tee_times = tee_time_list

    def process_tee_times(self):
        # code to clean and process the scraped tee times data
        pass

    def save_to_csv(self, filename):
        # code to save processed data to CSV
        pass

    def quit(self):
        self.driver.quit()
