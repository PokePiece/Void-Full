from selenium import webdriver
from fastapi import APIRouter
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time

auto_router = APIRouter()

@auto_router.get('/hello-auto')
def hello_auto():
    service = Service()
    driver = webdriver.Chrome(service=service)

    url = 'http://localhost:3000/ships/hello-world'
    driver.get(url)
    time.sleep(2)
    try:
        button = driver.find_element(By.ID, 'hello-button')
        button.click()
        print("Button clicked.")
    except Exception as e:
        print("Button not found or error:", e)

    input("Press Enter to close...")
    driver.quit()
    
@auto_router.get('/harrell-auto')
def harrell_auto():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # Use your real Chrome profile path here (uncomment and edit)
    # options.add_argument(r"user-data-dir=C:\Users\YourUser\AppData\Local\Google\Chrome\User Data")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    driver.get('http://localhost:3000/ships/harrell')
    time.sleep(7)  # Wait for page, ads, UI to load

    # Accept cookies if prompted
    try:
        consent = driver.find_element(By.XPATH, "//ytd-button-renderer//tp-yt-paper-button[@aria-label='Accept all']")
        consent.click()
        time.sleep(2)
    except Exception:
        pass

    # Click the video player to start playback
    video_player = driver.find_element(By.CLASS_NAME, "html5-video-player")
    actions = ActionChains(driver)
    actions.move_to_element(video_player).click().perform()
    time.sleep(1)

    # Fullscreen via "f" key
    video_player.send_keys("f")

    return {"status": "YouTube video launched, playing, and fullscreened"}
    
    