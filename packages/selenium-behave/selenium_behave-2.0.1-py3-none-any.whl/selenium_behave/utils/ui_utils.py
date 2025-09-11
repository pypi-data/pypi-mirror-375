from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://copilot.microsoft.com/"

def launch_copilot():
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    time.sleep(10)
    return driver

def click_mic_button(driver):
    mic_button = WebDriverWait(driver, 40).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Talk to Copilot']"))
    )
    time.sleep(2)
    mic_button.click()
