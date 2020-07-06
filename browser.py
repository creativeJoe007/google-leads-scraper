#----------------------------------------------------------------------------------------------------
# Authur: creativeJoe007
# Website: https://creativejoe007.com
#----------------------------------------------------------------------------------------------------
# A Google bot that allows anyone search for business using a keyword
# We extract the website title, description, email (if any), mobile number (if any), web-link
# A ideal bot for marketers looking to find leads/prospects
#----------------------------------------------------------------------------------------------------
from selenium import webdriver
from webdriver_manager.utils import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException


def determine_browser(preferred_browser="chrome", binary_path=""):
  #----------------------------------------------------------------------------------------------
  # We would perform try and catch for multiple browser type until we find one that exits
  # ON the host system
  #----------------------------------------------------------------------------------------------
  supported_browser = ["chrome", "chromium"]

  try:
    if preferred_browser not in supported_browser:
      return f"This browser is not supported by this library, only supported browsers are {supported_browser}"
    else:
      if preferred_browser == "chrome" or preferred_browser == "chromium":
        return start_chrome(preferred_browser, binary_path)
  except WebDriverException as e:
    return f"Browser error: {str(e)}"
  except OSError as e:
   return f"OS Error: {str(e)}"

def start_chrome(_preferred_type, binary_path):
  from webdriver_manager.chrome import ChromeDriverManager
  from selenium.webdriver.chrome.options import Options
  from webdriver_manager.utils import ChromeType

  options = Options()
  options.add_argument('--headless')
  options.add_argument('start-maximized')
  options.add_argument("enable-automation")
  options.add_argument("--disable-extensions")
  options.add_argument("--window-size=1920,8000");
  options.add_argument("enable-features=NetworkServiceInProcess");
  options.add_argument("disable-features=NetworkService");
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-infobars")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-gpu")
  options.add_argument("--disable-browser-side-navigation")
  options.add_argument("--force-device-scale-factor=1")

  # If binary path was passed
  if binary_path: options.binary_location=binary_path

  if _preferred_type == "chrome":
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)
  else:
    return webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=options)

def start_firefox(binary_path):
  from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
  from selenium.webdriver.firefox.options import Options

  options = Options()
  options.set_headless()

  binary = FirefoxBinary(binary_path)
  return webdriver.Firefox(firefox_binary=binary, options=options)
