import os
import time
import csv
from helpers import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def downloadImageSeries(urls, partNumber):
    i = 1
    for image_url in urls:
        path = os.path.join(os.getcwd(), f"images/{partNumber}_image{i}.jpg")
        download_image(image_url, path)
        i += 1


def getData(driver):
    try:
        productDetails = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
        )
        items = WebDriverWait(productDetails, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pull-right"))
        )
        PartNumber = items[0].text
        Description = items[1].text
        tableDetails = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-condensed"))
        )
        tableAttrs = WebDriverWait(tableDetails, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "data-plate-odd"))
        )
        atrs = [i.find_elements(By.CLASS_NAME, "ng-star-inserted") for i in tableAttrs]
        Sellable = atrs[0][-1].text
        Length = atrs[1][-1].text
        Weight = atrs[2][-1].text
        Width = atrs[3][-1].text
        Height = atrs[4][-1].text
        productPageUrl = driver.current_url

        prodDetails = {
            "PartNumber": PartNumber,
            "Description": Description,
            "Sellable": Sellable,
            "Length": Length,
            "Weight": Weight,
            "Width": Width,
            "Height": Height,
            "productPageUrl": productPageUrl,
        }

        try:
            swiper = driver.find_element(By.CLASS_NAME, "swiper-wrapper")
            img_elements = WebDriverWait(swiper, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
            )
            if img_elements:
                urls = [i.get_attribute("src") for i in img_elements]
                for idx, image_url in enumerate(urls, 1):
                    prodDetails[f"image{idx}_url"] = image_url
                    prodDetails[f"image{idx}_name"] = f"{PartNumber}_image{idx}.jpg"
                downloadImageSeries(urls, PartNumber)
            else:
                prodDetails["image1_url"] = "no image available"
                prodDetails["image1_name"] = "no image available"
        except Exception as e:
            prodDetails["image1_url"] = "no image available"
            prodDetails["image1_name"] = "no image available"

        return prodDetails

    except Exception as e:
        pass
        # print("Error fetching details:", e)


def getProducts(driver):
    wait = WebDriverWait(driver, 5)
    products = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "product-info"))
    )
    PRODUCT = []
    for i in range(len(products)):
        products = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-info"))
        )
        product = products[i]

        try:
            WebDriverWait(product, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[class="ng-star-inserted"]')
                )
            ).click()
            product = getData(driver)
            if product:
                PRODUCT.append(product)
            driver.back()
            time.sleep(2)
        except Exception as e:
            pass
            # print(f"An error occurred: {e}")

    return PRODUCT


def chunk_list(lst, chunk_size):
    """Yield successive chunk_size-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def scrapData(driver, partNumbers):
    wait = WebDriverWait(driver, 10)
    all_products = []

    for part_chunk in chunk_list(partNumbers, 50):  # Change batch size to 50
        chunk_products = []
        for number in part_chunk:
            try:
                search = wait.until(EC.presence_of_element_located((By.ID, "criteria")))
                print(f"Searching for part number: {number}")
                search.clear()
                search.send_keys(number)
                searchBtn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="search"]'))
                )
                searchBtn.click()
                samples = getProducts(driver)
                if samples:
                    chunk_products.extend(samples)
                else:
                    print("No products found.")

            except Exception as e:
                url = "https://parts.cummins.com/global-search/main/5471860"
                driver.get(url)
                try:
                    wait = WebDriverWait(driver, 5)
                    closeCookie = wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, '[id="onetrust-accept-btn-handler"]')
                            )
                        )
                    closeCookie.click()
                    time.sleep(2)
                except:
                    pass    

        if chunk_products:
            write_to_csv(chunk_products, "data", "Products.csv")
            print("Products.csv Updated ....")
            all_products.extend(chunk_products)

    return all_products


def write_to_csv(data, directory, filename):
    fieldnames = []
    for item in data:
        for key in item.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    file_exists = os.path.isfile(filepath)

    with open(
        filepath, "a" if file_exists else "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for item in data:
            writer.writerow(item)


def scraping():
    partNumbers = getPartNumbers(
        "input1.xlsx", "combine part number", "Selling Part Number"
    )
    try:
        driver = configure_undetected_chrome_driver(True)
        driver.maximize_window()
        url = "https://parts.cummins.com/global-search/main/5471860"
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        closeCookie = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[id="onetrust-accept-btn-handler"]')
            )
        )
        closeCookie.click()
        time.sleep(2)

        all_products = scrapData(driver, partNumbers)
        if all_products:
            write_to_csv(all_products, "data", "All_Products.csv")
        else:
            print("No products found.")
    except Exception as e:
        pass
        print(f"An error occurred: {e}")


scraping()
