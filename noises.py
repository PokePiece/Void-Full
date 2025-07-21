from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

def run_noises():
    
    
    #To run headless (no GUI), e.g., in a Linux setup
    #options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # Run without GUI
    #options.add_argument('--no-sandbox')  # Required on some servers
    #options.add_argument('--disable-dev-shm-usage')  # Prevents shared memory errors
    #service = Service()
    #driver = webdriver.Chrome(service=service, options=options)
    
    service = Service()
    driver = webdriver.Chrome(service=service)

    url = 'https://noises.online/'
    driver.get(url)
    time.sleep(2)

    try:
        element = driver.find_element(By.ID, 'paper')
        driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, element)
        print("Div removed.")
    except Exception as e:
        print("Div not found or error:", e)

    input("Press Enter to close...")  # Optional, remove if you don't want blocking
    driver.quit()
