from selenium import webdriver
from webdriver_manager.utils import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException


def determine_browser(preferred_browser="chrome", binary_path=""):
  #----------------------------------------------------------------------------------------------
  # We would perform try and catch for multiple browser type until we find one that exits
  # ON the host system
  #----------------------------------------------------------------------------------------------
  supported_browser = ["chrome", "chromium", "firefox"]

  try:
    if preferred_browser not in supported_browser:
      return "This browser is supported by this library"
    else:
      if preferred_browser == "chrome" or preferred_browser == "chromium":
        return start_chrome(preferred_browser, binary_path)
      elif preferred_browser == "firefox":
        return start_firefox(binary_path)
  except WebDriverException as e:
    return f"We couldn't find a {preferred_browser} browser on your computer, \
      kindly pass a binary path should we not have gotten the path right"
  except OSError as e:
   return "Seems, there is an issue with your browser binary path"

def start_chrome(_preferred_type, binary_path):
  from webdriver_manager.chrome import ChromeDriverManager
  from selenium.webdriver.chrome.options import Options
  from webdriver_manager.utils import ChromeType

  options = Options();
  options.add_argument('--headless');
  options.add_argument('--start-maximized');
  options.add_argument("enable-automation");
  options.add_argument("--disable-extensions");
  options.add_argument("--dns-prefetch-disable");
  options.add_argument("--no-sandbox");
  options.add_argument("--disable-dev-shm-usage");
  options.add_argument("--disable-gpu");
  options.add_argument("--force-device-scale-factor=1");

  # If binary path was passed
  if binary_path: options.binary_location = binary_path;

  if _preferred_type == "chrome":
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)
  else:
    return webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=options)

def start_firefox(binary_path):
  from webdriver_manager.firefox import GeckoDriverManager
  from selenium.webdriver.firefox.options import Options

  options = Options();
  options.set_headless();

  if binary_path: options.binary_location = binary_path;

  return webdriver.Firefox(GeckoDriverManager().install(), options=options)
