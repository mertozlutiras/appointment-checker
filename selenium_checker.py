import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

URL = "https://service.berlin.de/dienstleistung/351180/"
NO_APPOINTMENT_TEXT = "keine Termine verfügbar"

def setup_driver():
    """Sets up the Chrome browser to run in the cloud (GitHub Actions)."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def check_for_appointment():
    """
    This function performs all the browser actions and now includes detailed logging.
    """
    driver = setup_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        
        select_all_checkbox = wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(., 'Alle Standorte auswählen')]"))
        )
        select_all_checkbox.click()
        print("Clicked 'Alle Standorte auswählen' checkbox.")
        
        book_appointment_button = wait.until(
            EC.element_to_be_clickable((By.NAME, 'g-select-termin'))
        )
        
        # --- THIS IS THE UPDATED PART ---
        # Instead of a standard click, we use a JavaScript click, which is more robust.
        print("Clicking 'Termin buchen' button using JavaScript...")
        driver.execute_script("arguments[0].click();", book_appointment_button)
        
        print("Waiting for calendar page to load...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'calendar-table')))
        
        if NO_APPOINTMENT_TEXT in driver.page_source:
            print("Successfully loaded calendar page. No appointments available.")
            return False
        else:
            print("Successfully loaded calendar page. APPOINTMENT FOUND!")
            return True

    except TimeoutException:
        print("\n---")
        print("Timeout: The calendar page did not load. Here's what the script saw instead:")
        try:
            page_title = driver.title
            body_text = driver.find_element(By.TAG_NAME, 'body').text
            print(f"  Page Title: '{page_title}'")
            print(f"  Page Preview:\n---\n{body_text[:600]}...\n---")
        except Exception as e:
            print(f"  Could not retrieve page details. Error: {e}")
        
        print("Assuming no appointment due to this error.")
        print("---\n")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    finally:
        driver.quit()

# --- Main script logic (No changes needed here) ---
if __name__ == "__main__":
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running appointment check...")
    
    is_available = check_for_appointment()
    
    if is_available:
        print("APPOINTMENT FOUND! The script will now 'fail' to trigger a notification.")
        sys.exit(1)
    else:
        print("No appointments found. The script will exit successfully.")
        sys.exit(0)