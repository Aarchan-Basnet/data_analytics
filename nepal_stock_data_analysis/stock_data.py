import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
import pandas as pd
from datetime import datetime


def create_directories():
    current_dir = os.getcwd()
    new_dir1 = os.path.join(current_dir, r"html_files")
    if not os.path.exists(new_dir1):
        os.makedirs(new_dir1)

    new_dir2 = os.path.join(current_dir, r"csv_files")
    if not os.path.exists(new_dir2):
        os.makedirs(new_dir2)


def fetch_url(url):
    print("Fetching url...")

    #open webpage using selenium
    driver = webdriver.Firefox()

    try:
        driver.get(url)
        driver.maximize_window()
        sleep(5)
    except Exception as e:
        print(e)
        driver.quit()

    return driver


def save_html_files():
    try:
        url = "https://www.nepalstock.com/today-price"
        driver = fetch_url(url)
        with open("html_files/nepalstock_today.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        with open("html_files/nepalstock_today.html", "rb") as file:
            html_content = file.read()

        tree = html.fromstring(html_content)

        #get pagination list
        global pages
        pagination_list = tree.xpath(
            "//pagination-template//li[last() - 1]//span[last()]/text()")
        # pagination_list = driver.find_element(By.XPATH,
        #                             "//pagination-template//li[last() - 1]//span[last()]/text()")
        pages = int(pagination_list[0])
        # print(f"pages: {pages}")
        # print(type(pages))

        #get today date
        global today
        today_date = tree.xpath("//div[@class='ticker__date']//span/text()")
        # today_date = driver.find_element(By.XPATH, "//div[@class='ticker__date']//span/text()")
        today = str(today_date[0])
        # print(today)
        # print(type(today))

        #save all pages as html
        for i in range(pages):
            print(f"Scraping page {i+1}...")
            filename = f"html_files/nepalstock_today{i+1}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(driver.page_source)

            next_button = driver.find_element(By.CLASS_NAME,
                                              "pagination-next")
            next_button.click()
            sleep(5)
    finally:
        driver.quit()


def parse_columns():
    print("Parsing columns ...")
    with open('html_files/nepalstock_today1.html', 'rb') as f:
        html_content = f.read()

    # Parse the HTML using lxml
    tree = html.fromstring(html_content)

    # Extract all columns using xpath
    columns = tree.xpath("//div[@class='table-responsive']//th//text()")
    return columns


def parse_data():
    print("Parsing data ...")
    cell_data = []
    for i in range(pages):
        filename = f"html_files/nepalstock_today{i+1}.html"
        with open(filename, 'rb') as f:
            html_content = f.read()

        tree = html.fromstring(html_content)

        # extract all rows using xpath
        data_rows = tree.xpath("//div[@class='table-responsive']//tbody/tr")
        for row in data_rows:
            data = row.xpath("td//text()")
            cell_data.append(data)

    return cell_data


def clean_data(data):
    print("Cleaning data ...")
    df = pd.DataFrame(data)

    df.iloc[:, 9] = df.iloc[:, 9].astype(str) + df.iloc[:, 10].astype(str)
    df.drop(df.columns[10], axis=1, inplace=True)
    cleaned_data = df.values.tolist()

    return cleaned_data


def data_to_csv(data_list, columns):
    print("Getting csv file ...")
    df = pd.DataFrame(data_list, columns=columns)
    date_format = "%b %d, %Y, %I:%M:%S %p "
    date_object = datetime.strptime(today, date_format).date()
    print(date_object)
    df.insert(0, "Date", date_object)
    print(df)
    df.to_csv(f"csv_files/nepalstock_{str(date_object)}.csv", index=False)


if __name__ == "__main__":
    save_html_files()
    columns = parse_columns()
    cell_data = parse_data()
    cleaned_data = clean_data(cell_data)
    data_to_csv(cleaned_data, columns)