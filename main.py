from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from extractor import Extractor
from selenium.webdriver.chrome.options import Options
import time

driver = None;

def main():
 chrome_options = Options()
 chrome_options.add_argument('--headless')
 chrome_options.add_argument('--start-maximized')

 executor_url = ""
 session_id = ""

 # Determine If we reuse chrome instance or create a new one
 if (executor_url):
  driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
  driver.session_id = session_id
 else:
  driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options);
  executor_url = driver.command_executor._url
  session_id = driver.session_id

  # Maximize chrome height to highest
  driver.set_window_size(1920, 8000)

  # driver.get(start_url)
  extractor = Extractor(driver)
  driver.close();

main()