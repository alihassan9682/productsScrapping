import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import os
import csv
import shutil

# Set custom WebDriver Manager cache directory
custom_cache_dir = os.path.expanduser("~/.custom_wdm")
os.environ["WEBDRIVER_MANAGER_CACHE"] = custom_cache_dir

import re


def extract_number_from_code(code):
    pattern = re.compile(r"(\D*)(\d+(?:-\d+)*)(\D*)")
    match = pattern.match(code)

    if match:
        left_side = match.group(1)
        number = match.group(2)
        right_side = match.group(3)

        if not left_side:
            return number
        elif not right_side:
            return number
        else:
            return left_side + number
    return None


def write_to_csv1(data, directory, filename):
    try:
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
        print("File Updated .......")
    except:
        print("Nothing to save .....")


def downloadImageSeries(urls, partNumber):
    if not os.path.exists("images"):
        os.makedirs("images")
    for i, image_url in enumerate(urls, start=1):
        path = os.path.join(os.getcwd(), f"milwakeImages/{partNumber}_image{i}.jpg")
        download_image(image_url, path)


def download_image(image_url, save_path, timeout=10):
    try:
        response = requests.get(image_url, stream=True, timeout=timeout)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            # print(f"Image successfully downloaded: {save_path}")
        else:
            print("Failed to retrieve the image")
    except requests.exceptions.Timeout:
        print("Download skipped due to timeout")


def getPartNumbers(excel_file_path, sheet_name, column_name):
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    if column_name in df.columns:
        return df[column_name].tolist()
    else:
        raise ValueError(f"Column '{column_name}' not found in sheet '{sheet_name}'")


def write_to_csv(data, directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    fieldnames = list({key for item in data for key in item.keys()})
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def configure_webdriver(
    open_browser=False, block_media=False, block_elements=["css", "img", "js"]
):
    options = webdriver.ChromeOptions()
    if not open_browser:
        options.add_argument("--headless")
    if block_media:
        hide_elements = {
            element: 2
            for element in [
                "plugins",
                "popups",
                "geolocation",
                "notifications",
                "auto_select_certificate",
                "fullscreen",
                "mouselock",
                "mixed_script",
                "media_stream",
                "media_stream_mic",
                "media_stream_camera",
                "protocol_handlers",
                "ppapi_broker",
                "automatic_downloads",
                "midi_sysex",
                "push_messaging",
                "ssl_cert_decisions",
                "metro_switch_to_desktop",
                "protected_media_identifier",
                "app_banner",
                "site_engagement",
                "durable_storage",
            ]
        }
        if "cookies" in block_elements:
            hide_elements["cookies"] = 2
        if "js" in block_elements:
            hide_elements["javascript"] = 2
        if "img" in block_elements:
            hide_elements["images"] = 2
        prefs = {"profile.default_content_setting_values": hide_elements}
        options.add_argument("--disable-features=EnableNetworkService")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option("prefs", prefs)
    options.add_argument("window-size=1200,1100")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    )

    try:
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
    except Exception as e:
        print(f"Error occurred while initializing WebDriver: {e}")
        raise

    if block_media:
        driver.execute_cdp_cmd("Page.enable", {})
        driver.execute_cdp_cmd("Network.enable", {})
        blocked_patterns = []
        if "img" in block_elements:
            blocked_patterns.extend(["*.jpg", "*.jpeg", "*.png", "*.gif"])
        if "css" in block_elements:
            blocked_patterns.append("*.css")
        if "js" in block_elements:
            blocked_patterns.append("*.js")
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": blocked_patterns})
    return driver


def configure_undetected_chrome_driver(open_browser=False):
    options = uc.ChromeOptions()
    my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    if not open_browser:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={my_user_agent}")
    options.add_experimental_option("prefs", {"extensions.ui.developer_mode": True})
    options.add_argument("--remote-debugging-port=9222")
    driver_executable = r"C:\Users\aliha\.wdm\drivers\chromedriver\win64\127.0.6533.72\chromedriver-win32\chromedriver.exe"

    try:
        driver = uc.Chrome(
            driver_executable_path=driver_executable,
            options=options,
            use_subprocess=False,
        )
    except Exception as e:
        print(f"Error occurred while initializing undetected ChromeDriver: {e}")
        raise

    return driver
