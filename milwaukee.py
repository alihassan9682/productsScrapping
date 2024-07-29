import os
import time
from helpers import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def closePopup(driver):
    popup = driver.find_element(By.CLASS_NAME, "lead-gen-pop-up")
    closeBtn = popup.find_element(By.CLASS_NAME, "fill-brandWhite")
    closeBtn.click()


def getImageSeries(partNumber, driver, prodDetails):
    try:
        swiper = driver.find_element(By.CLASS_NAME, "media-gallery")
        img_elements = WebDriverWait(swiper, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
        if img_elements:
            print('Downloading Images ......')
            urls = [i.get_attribute('src') for i in img_elements]
            for idx, image_url in enumerate(urls, 1):
                prodDetails[f'image{idx}_url'] = image_url
                prodDetails[f'image{idx}_name'] = f'{partNumber}_image{idx}.jpg'
            downloadImageSeries(
                urls, partNumber)
            time.sleep(2)
    except:
        prodDetails['image1_url'] = "Not available"
        prodDetails['image1_name'] = "Not available"


def getImageUrls(colorElements, partNumber, driver, prodDetails):
    for element in colorElements:
        element.click()
        time.sleep(2)
        getImageSeries(
            f'{partNumber}_{element.get_attribute("data-color")}', driver, prodDetails)


def getData(driver, PartNumber, usedNumber):
    try:
        productTitle = WebDriverWait(
            driver, 5).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "product-info__details")))
        productTitle = productTitle.text.split('\n')[0]
        productDescription = WebDriverWait(
            driver, 5).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "product-info__overview"))).text
        try:
            driver.find_element(By.CLASS_NAME, "product-size-options")
            sizeElements = driver.find_elements(
                By.CLASS_NAME, 'product-size-option')
            sizes = [
                f'Size-{i.get_attribute("data-size")}-({i.get_attribute("data-sku")})' for i in sizeElements]
        except:
            sizes = "Not Available"

        try:
            product_features_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-features')))
            child_elements = product_features_element.find_elements(
                By.XPATH, './*')
            productFeatures = [child.text for child in child_elements]
            combined_text = ', '.join(productFeatures)
            productFeatures = combined_text.split('\n')
        except:
            productFeatures = "Not available"

        try:
            specs = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-specs__table')))
            specs = specs.find_elements(By.CLASS_NAME, 'product-specs__row ')
            productSpecifications = [
                i.text.replace('\n', ' : ') for i in specs]
        except:
            productSpecifications = "Not available"

        productPageUrl = driver.current_url

        prodDetails = {
            'PartNumber': PartNumber,
            'UsedPartNumber': usedNumber,
            'ProductTitle': productTitle,
            'Description': productDescription,
            "productFeatures": productFeatures,
            "productSpecifications": productSpecifications,
            'productPageUrl': productPageUrl,
            "Sizes": sizes,
        }

        try:
            driver.find_element(By.CLASS_NAME, "product-color-options")
            colorElements = driver.find_elements(
                By.CLASS_NAME, 'product-color-option')
            colors = [i.get_attribute('data-color') for i in colorElements]
            prodDetails["Colors"] = colors
            getImageUrls(colorElements, PartNumber, driver, prodDetails)
        except:
            prodDetails["Colors"] = "Not Available"
            getImageSeries(PartNumber, driver, prodDetails)

        # print(prodDetails)

        return prodDetails

    except Exception as e:
        print("Error fetching details:", e)


def chunk_list(lst, chunk_size):
    """Yield successive chunk_size-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def searchPartNumber(number, driver):
    wait = WebDriverWait(driver, 5)
    searchBtn = driver.find_element(
        By.CSS_SELECTOR, '[jsname="pkjasb"]')
    searchBtn.click()
    search = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '[aria-label="Search"]')))
    search.send_keys(f'Milwaukee {number}')
    searchBtn = driver.find_element(
        By.CSS_SELECTOR, '[jsname="Tg7LZd"]')
    searchBtn.click()
    time.sleep(2)
    page = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'VuuXrf')))

    return page

def foundPage(driver, number, usedNumber):
    try:
        WebDriverWait(
            driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "lead-gen-pop-up")))
        closePopup(driver)
    except BaseException:
        pass

    product = getData(driver, number, usedNumber)
    url = "https://www.google.com/search?q=milwaukee+mxfxc406&oq=Milwaukee+MXFXC406&gs_lcrp=EgZjaHJvbWUqBwgAEAAYgAQyBwgAEAAYgAQyCggBEAAYogQYiQUyCggCEAAYogQYiQWoAgCwAgA&sourceid=chrome&ie=UTF-8"
    driver.get(url)
    return product
    

def scrapData(driver, partNumbers):
    all_products = []

    for part_chunk in chunk_list(partNumbers, 20):
        chunk_products = []
        product = None
        for number in part_chunk:
            print(number)
            try:
                usedNumber = number
                page = searchPartNumber(number, driver)

                if page.text != "Milwaukee Tool":
                    usedNumber = extract_number_from_code(number)
                    if usedNumber:
                        page = searchPartNumber(usedNumber, driver)
                        if page.text == "Milwaukee Tool":
                            page.click()
                            product= foundPage(driver, number, usedNumber)    
            
                elif page.text == "Milwaukee Tool":
                    page.click()
                    product= foundPage(driver, number, usedNumber)
                
                if product:
                    chunk_products.append(product)
                else:
                    print("No products found.")

                            
            except Exception as e:
                url = "https://www.google.com/search?q=milwaukee+mxfxc406&oq=Milwaukee+MXFXC406&gs_lcrp=EgZjaHJvbWUqBwgAEAAYgAQyBwgAEAAYgAQyCggBEAAYogQYiQUyCggCEAAYogQYiQWoAgCwAgA&sourceid=chrome&ie=UTF-8"
                driver.get(url)
                print(f"Error during job scraping: {e}")

        if chunk_products:
            write_to_csv1(chunk_products, "data", "milwaukeeProducts.csv")
            all_products.append(chunk_products)

    return all_products


def scraping():
    partNumbers = getPartNumbers(
        'milwaukee.xlsx', 'Part number', 'Selling Part Number')
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://www.google.com/search?q=milwaukee+mxfxc406&oq=Milwaukee+MXFXC406&gs_lcrp=EgZjaHJvbWUqBwgAEAAYgAQyBwgAEAAYgAQyCggBEAAYogQYiQUyCggCEAAYogQYiQWoAgCwAgA&sourceid=chrome&ie=UTF-8"
        driver.get(url)
        all_products = scrapData(driver, partNumbers)
        if all_products:
            write_to_csv1(all_products, "data", "All_Milwaukee_Products.csv")
        else:
            print("No products found.")
    except Exception as e:
        url = "https://www.google.com/search?q=milwaukee+mxfxc406&oq=Milwaukee+MXFXC406&gs_lcrp=EgZjaHJvbWUqBwgAEAAYgAQyBwgAEAAYgAQyCggBEAAYogQYiQUyCggCEAAYogQYiQWoAgCwAgA&sourceid=chrome&ie=UTF-8"
        driver.get(url)
        print(f"An error occurred: {e}")


scraping()
