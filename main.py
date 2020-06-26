import sys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from extractor import Extractor
from selenium.webdriver.chrome.options import Options
import time

driver = None;
arguments = sys.argv

print("\n")
def main():
  chrome_options = Options();
  chrome_options.add_argument('--headless');
  chrome_options.add_argument('--start-maximized');
  chrome_options.add_argument("enable-automation");
  chrome_options.add_argument("--disable-extensions");
  chrome_options.add_argument("--dns-prefetch-disable");
  chrome_options.add_argument("--no-sandbox");
  chrome_options.add_argument("--disable-dev-shm-usage");
  chrome_options.add_argument("--disable-gpu");
  chrome_options.add_argument("--force-device-scale-factor=1");

  executor_url = ""
  session_id = ""
  query = arguments[1]
  start_page = int(arguments[2]) if len(arguments) > 2 and type(arguments[2]) is int else 0
  stop_page = int(arguments[3]) if len(arguments) > 3 and type(arguments[3]) is int else 14

  if start_page < 0: start_page = 0 # If the user puts in 0, we auto make it one
  elif (stop_page - start_page) > 15:
    print("You cannot search more than 15 pages at a time")
  # elif (stop_page - start_page) > 15:
  #  print("You cannot be search more than 15 pages at a time")

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
    print(f"\nGoogle's Query: {query}")
    extractor = Extractor(driver, query, start_page, stop_page)
    driver.close();

if len(arguments) < 2: print("You didn't enter your search query")
else: main()
print("\n")