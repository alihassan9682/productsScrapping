import csv
import os

import time
from helpers import configure_webdriver

def write_to_csv(data, directory, filename):
    fieldnames = list(data[0].keys())
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
            

def scraping():
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://www.amazon.com/gp/bestsellers/arts-crafts/ref=zg_b_bs_arts-crafts_1"
        try:
            driver.get(url)
            time.sleep(5)
            samples = [{},{}]
            if samples:
                write_to_csv(samples, "data", "sample.csv")
            else:
                print("No products found.")
        except Exception as e:
            print(f"Error during job scraping: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scraping()
