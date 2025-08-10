import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---
URL = "https://service.berlin.de/dienstleistung/351180/"
# Define the known text phrases for the two failure pages
FAILURE_TEXT_1 = "keine Termine für Ihre Auswahl verfügbar"
FAILURE_TEXT_2 = "Zu Ihrer Suche konnten keine Daten ermittelt werden"

def setup_driver():
    """Sets up the Chrome browser."""
    options = webdriver.ChromeOptions()
    # To run on GitHub, this MUST be enabled. To test locally, comment it out.
    
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1200)
    return driver

def check_for_appointment():
    """Performs all browser actions to check for appointments."""
    driver = setup_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        
        initial_h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        
        select_all_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(., 'Alle Standorte auswählen')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_all_checkbox)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", select_all_checkbox)
        print("Clicked 'Alle Standorte auswählen' checkbox.")
        
        book_appointment_button = wait.until(EC.element_to_be_clickable((By.ID, 'appointment_submit')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_appointment_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", book_appointment_button)
        print("Clicked the submit button.")
        
        print("Verifying page transition...")
        wait.until(EC.staleness_of(initial_h1))
        print("Page successfully transitioned.")

        print("Checking result page for known failure patterns...")
        # --- THIS IS THE KEY CHANGE ---
        # Get all text and convert it to lower case for case-insensitive matching.
        page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
        
        # Check if either lowercase failure phrase exists in the lowercase text.
        if FAILURE_TEXT_1.lower() in page_text or FAILURE_TEXT_2.lower() in page_text:
            print("Result: A known 'no appointment' or error page was found.")
            return False
        else:
            print("Result: Page does not match known failure patterns. APPOINTMENT FOUND!")
            page_title = driver.title
            print(f"  Success Page Title: '{page_title}'")
            return True

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    finally:
        driver.quit()

# --- Main script logic ---
if __name__ == "__main__":
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running appointment check...")
    
    is_available = check_for_appointment()
    
    if is_available:
        print