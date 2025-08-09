import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# The two key variables for the script
URL = "https://service.berlin.de/dienstleistung/351180/"
NO_APPOINTMENT_TEXT = "keine Termine verfügbar"

def setup_driver():
    """Sets up the Chrome browser to run in the cloud (GitHub Actions)."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run without a visible browser window
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def check_for_appointment():
    """
    This function performs all the browser actions:
    1. Clicks the 'select all' checkbox.
    2. Clicks the 'book appointment' button.
    3. Checks the result page for the "no appointments" text.
    Returns True if an appointment is found, False otherwise.
    """
    driver = setup_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        
        # Click the "Select All" checkbox
        select_all_checkbox = wait.until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(., 'Alle Standorte auswählen')]"))
        )
        select_all_checkbox.click()
        
        # Wait for the "Termin buchen" button to be clickable, then click it
        book_appointment_button = wait.until(
            EC.element_to_be_clickable((By.NAME, 'g-select-termin'))
        )
        book_appointment_button.click()
        
        # On the results page, wait for the calendar to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'calendar-table')))
        
        # Check if the "no appointment" text exists.
        if NO_APPOINTMENT_TEXT in driver.page_source:
            return False # No appointment found
        else:
            return True # The text is missing, so an appointment IS available!

    except TimeoutException:
        # This happens on an error page or if the calendar doesn't load. Treat as no appointment.
        print("Landed on an error page or the calendar page did not load in time.")
        return False
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
        print("APPOINTMENT FOUND! The script will now 'fail' to trigger a notification.")
        # Exit with an error code. This makes GitHub send you an email.
        sys.exit(1)
    else:
        print("No appointments found. The script will exit successfully.")
        # Exit gracefully. GitHub will show a green checkmark and do nothing.
        sys.exit(0)