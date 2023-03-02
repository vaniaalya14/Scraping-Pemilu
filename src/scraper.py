from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import enum


class CategoryEnum(enum.Enum):
    PROVINSI = "PROVINSI"
    KABUPATEN_KOTA = "KABUPATEN/KOTA"
    LUAR_NEGERI = "LUAR_NEGERI"
    PPLN = "PPLN"


class Scraper:
    def __init__(self, driver: Chrome, wait: WebDriverWait, url: str):
        self.driver = driver
        self.wait = wait
        self.url = url
        self.records = []

    def scrape_provinces(self, row_count, table_number):
        for counter in range(row_count):
            record_entry = []

            self.driver.get(self.url)

            time.sleep(3)

            self.driver.execute_script("window.scrollTo(0,650)")

            province = self.driver.find_element(
                By.XPATH,
                "/html/body/div/div[2]/div[1]/div[2]/section/div/div[4]/div/div[{table_number}]/table/tbody/tr[{count}]/td[1]/button".format(
                    table_number=table_number, count=counter + 1
                ),
            )

            vote_jokowi = self.driver.find_element(
                By.XPATH,
                '//*[@id="app"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[{table_number}]/table/tbody/tr[{count}]/td[2]'.format(
                    table_number=table_number, count=counter + 1
                ),
            )

            vote_prabowo = self.driver.find_element(
                By.XPATH,
                '//*[@id="app"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[{table_number}]/table/tbody/tr[{count}]/td[3]'.format(
                    table_number=table_number, count=counter + 1
                ),
            )

            province_name = province.get_attribute("innerHTML").strip()
            vote_jokowi_number = (
                vote_jokowi.get_attribute("innerHTML").replace(".", "").strip()
            )
            vote_prabowo_number = (
                vote_prabowo.get_attribute("innerHTML").replace(".", "").strip()
            )

            print(
                "{province_name} - {vote_jokowi} : {vote_prabowo}".format(
                    province_name=province_name,
                    vote_jokowi=vote_jokowi_number,
                    vote_prabowo=vote_prabowo_number,
                )
            )

            category = CategoryEnum.PROVINSI.value
            is_foreign = False

            if province_name == "+Luar Negeri":
                category = CategoryEnum.LUAR_NEGERI.value
                is_foreign = True

            record_entry = [
                province_name,
                vote_jokowi_number,
                vote_prabowo_number,
                category,
            ]

            self.records.append(record_entry)

            wait.until(EC.element_to_be_clickable(province)).click()

            time.sleep(3)

            tabel_prov_kiri = driver.find_elements(
                By.XPATH,
                '//*[@id="app"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[1]/table/tbody/tr',
            )
            tabel_prov_kanan = driver.find_elements(
                By.XPATH,
                '//*[@id="app"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[2]/table/tbody/tr',
            )
            self.scrape_cities(len(tabel_prov_kiri), 1, is_foreign)
            self.scrape_cities(len(tabel_prov_kanan), 2, is_foreign)

    def scrape_cities(self, row_count, table_number, is_foreign):
        for counter in range(row_count):
            record_entry = []

            city = driver.find_element(
                By.XPATH,
                "//*[@id=\"app\"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[{table_number}]/table/tbody/tr[{count_prov}]/td[1]/button[contains(@class,'clear-button text-primary text-left')]".format(
                    table_number=table_number, count_prov=counter + 1
                ),
            )

            vote_jokowi = driver.find_element(
                By.XPATH,
                '//*[@id="app"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[{table_number}]/table/tbody/tr[{count_prov}]/td[2]'.format(
                    table_number=table_number, count_prov=counter + 1
                ),
            )

            vote_prabowo = driver.find_element(
                By.XPATH,
                '//*[@id="app"]/div[2]/div[1]/div[2]/section/div/div[4]/div/div[{table_number}]/table/tbody/tr[{count_prov}]/td[3]'.format(
                    table_number=table_number, count_prov=counter + 1
                ),
            )

            city_name = city.get_attribute("innerHTML").strip()
            vote_jokowi_number = (
                vote_jokowi.get_attribute("innerHTML").replace(".", "").strip()
            )
            vote_prabowo_number = (
                vote_prabowo.get_attribute("innerHTML").replace(".", "").strip()
            )

            print(
                "{city_name} - {vote_jokowi} : {vote_prabowo}".format(
                    city_name=city_name,
                    vote_jokowi=vote_jokowi_number,
                    vote_prabowo=vote_prabowo_number,
                )
            )

            category = CategoryEnum.KABUPATEN_KOTA.value

            if is_foreign == True:
                category = CategoryEnum.PPLN.value

            record_entry = [
                city_name,
                vote_jokowi_number,
                vote_prabowo_number,
                category,
            ]

            self.records.append(record_entry)

    def print_values(self):
        print(self.records)

    def get_all_records(self):
        return self.records


if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("detach", True)

    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver=driver, timeout=10)

    driver.maximize_window()

    scraper_table_1 = Scraper(
        driver=driver,
        wait=wait,
        url="https://pemilu2019.kpu.go.id/#/ppwp/hitung-suara/",
    )
    scraper_table_1.scrape_provinces(18, 1)
    scraper_table_1.scrape_provinces(17, 2)
    scraper_table_1.print_values()

    all_records = scraper_table_1.get_all_records()
    with open("scraping_v3.csv", "w", encoding="UTF8") as file:
        header = ["daerah", "vote_jokowi", "vote_prabowo", "kategori"]
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(all_records)
