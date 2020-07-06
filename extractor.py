#----------------------------------------------------------------------------------------------------
# Authur: creativeJoe007
# Website: https://creativejoe007.com
#----------------------------------------------------------------------------------------------------
# A Google bot that allows anyone search for businesses using a keyword
# We extract the website title, description, email (if any), mobile number (if any), web-link
# An ideal bot for marketers looking to find leads/prospects
#----------------------------------------------------------------------------------------------------
import json
import re
import time
import csv
from pathlib import Path
from selenium.common.exceptions import NoSuchElementException,\
  TimeoutException,\
  WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from println import println

extracted_data_sample = {
  'title': '',
  'url': '',
  'description': '',
  'site_description': '',
  'screen_shot': '',
  'contact_email': '',
  'contact_number': ''
}
class Extractor():
  #------------------------------------------------------------------------
  # This is where we extract all the data we need while scrapping
  # We take our screenshots here, get titles, find social media pages
  #  Of users we extract
  #------------------------------------------------------------------------
  def __init__(self, driver, query: str, start_page: int, stop_page: int, file_name: str):
    self._driver = driver
    self._file_name = file_name
    self._page = start_page # start counting from zero due to google's seek algorithm
    self._stop_page = stop_page # start counting from zero due to google's seek algorithm
    self._site_content = extracted_data_sample

    # We loop through the enter data wrapped under pagination
    self.paginate_page(query)

  def paginate_page(self, query):
    #------------------------------------------------------------------------
    # We are going to fetch all first 10 pages
    # Of google's result
    #------------------------------------------------------------------------
    start_url = f"https://www.google.com/search?q={query}&sourceid=chrome&ie=UTF-8"
    seek_number = 0
    seek_url_query = f"&start={seek_number}"

    # while self._page <= 9:
    while self._page <= self._stop_page:
      self._driver.get(start_url + f"&start={(self._page * 10)}")
      try:
        self.extract_page_content()
      except WebDriverException as e:
        println(f"Selenium error: {str(e)}", "warn")
      except TimeoutException as e:
        println(f"Timeout error: {str(e)}", "warn")

      self._page += 1
      self._data_extract = []

    println("Congratulations, scraping complete", "normal")

  def words_in_string(self, word_list, a_string):
    return set(word_list).intersection(a_string.lower().split())

  def extract_page_content(self):
    #------------------------------------------------------------------------
    # We are going to get all major links in a page
    # Match that they do not contain the words
    # "english", "translate" or "translation"
    # Any item that passes this page would be considered for scrapping
    #------------------------------------------------------------------------
    dictionary_words = ["english", "translate", "translation", "dictionary", "Thesaurus", "translations", "definition"]
    response = self._driver.find_elements_by_css_selector("div.g")

    # Now we look through all search results
    for result in response:
      self._site_content = extracted_data_sample

      google_result = result.find_element_by_css_selector("div.rc")

      self._site_content['title'] = google_result.find_element_by_css_selector("div.r")\
        .find_element_by_css_selector("h3.LC20lb.DKV0Md").text

      self._site_content['description'] = google_result.find_element_by_css_selector("div.s")\
        .find_element_by_css_selector("span.st").text

      self._site_content['url'] = google_result.find_element_by_css_selector("div.r")\
        .find_element_by_tag_name("a").get_attribute("href")

      if(not self.words_in_string(dictionary_words, self._site_content['title']) and \
        not self.words_in_string(dictionary_words, self._site_content['description'])):
          #------------------------------------------------------------------------
          # This website is not a dictionary, now we can start 
          # scanning through to extract just
          # The data we need
          #------------------------------------------------------------------------
          if "youtube" in self._site_content['url']:
            continue
          elif "facebook" in self._site_content['url']:
            #------------------------------------------------------------------------
            # First we split by "/"
            # We check if the last "/" is empty in case the URL ended with "/"
            # If its empty we use the second to last
            # If its not empty we check if the value contains "?" meaning a query
            # If it does, we still use second to last
            #------------------------------------------------------------------------
            split_page_url_list = self._site_content['url'].split("/")
            page_name = ""

            if split_page_url_list[len(split_page_url_list) - 1] == "":
              page_name = split_page_url_list[len(split_page_url_list) - 2]
            else:
              if "?" in split_page_url_list[len(split_page_url_list) - 1]:
                page_name = split_page_url_list[len(split_page_url_list) - 2]
              else:
                page_name = split_page_url_list[len(split_page_url_list) - 1]
            
            self._site_content['url'] = f"https://web.facebook.com/pg/{page_name}/about/"

          try:
            self.extract_info_from_link()
            println(f"Finished Scrapping, {self._site_content['url']}", "normal")
          except NoSuchElementException as e:
            # Had cases where body element was empty, meaning the website didn't exist
            # So since a new window was launched before that error,
            # We have to close the window and switch back to the search result
            self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[len(self._driver.window_handles) - 1])
            println(f"This website ({self._site_content['url']}) has an issue and could not be parsed", "warn")

  def extract_info_from_link(self):
    #------------------------------------------------------------------------
    # We will access all the different websites, and
    # extract every email address, and phone number
    # Found in them
    #------------------------------------------------------------------------

    # Load up a new tab to handle this
    self._driver.execute_script("window.open('')")
    self._driver.switch_to.window(self._driver.window_handles[len(self._driver.window_handles) - 1])

    self._driver.get(self._site_content['url'])
    println("-----------------------------------------------------------------------------------------", "bold")
    println(f"Currently Scrapping, {self._site_content['url']}", "bold")
    time.sleep(5)
    
    html_source = self._driver.find_element_by_tag_name('body').get_attribute('innerHTML')
    extracted_numbers = ""
    extracted_emails = ""

    #------------------------------------------------------------------------
    # Now we use regex to match all occurrences of email or phone numbers
    # in the page source
    #------------------------------------------------------------------------
    try:
      self._site_content['site_description'] = self._driver.find_element_by_xpath("//meta[@name='description']")\
        .get_attribute("content")
    except NoSuchElementException as e:
      println(f"Opps, we couldn't find a meta description for this website ({self._site_content['url']})", "warn")

    screen_shot_name = 'static/' + re.sub(r"[\-\(\)\+ .*]", "", self._site_content["title"]) + '.png'

    found_numbers = self.scan_for_numbers(html_source)
    found_emails = self.scan_for_emails(html_source)
    verified_numbers = self.extract_mobile_number(found_numbers)
    verified_emails = self.extract_real_email_address(found_emails)

    self._site_content['contact_number'] = verified_numbers
    self._site_content['contact_email'] = verified_emails
    
    if len(verified_numbers) or len(verified_emails):
      # Increase the size of the page for our screenshot
      # self._driver.set_window_size(1920, 8000)
      self.screengrab(screen_shot_name)
      self._site_content['screen_shot'] = screen_shot_name

      # We are done with processing now lets add to our csv
      # Save extracted files
      self.write_to_file(self._site_content)

    # Close new tab first
    self._driver.close()
    self._driver.switch_to.window(self._driver.window_handles[len(self._driver.window_handles) - 1])

  def scan_for_numbers(self, source: str) -> list:
    found_numbers: list = []
    phone_regex = [
      "\+[\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]", # Priority 1
      "((tel|p|t|phone|call|dial|ring)[: -]?[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9])", # Priority 2
      # "[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]" # Priority 3
    ]

    for regex in phone_regex:
      is_found = re.findall(regex, source, re.IGNORECASE)
      if len(is_found) > 0:
        if type(is_found[0]) is tuple:
          #------------------------------------------------------------------------
          # Our second regex returns a tuple instead of a string like the other one
          # I haven't figured how to resolve that but this is just a work around
          #------------------------------------------------------------------------
          found_numbers = [is_found[0][0]]
        else: found_numbers = is_found
        break
    
    return found_numbers

  def scan_for_emails(self, source: str) -> list:
   extracted_email_addresses: list = []
   email_regex = "[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*"
   emails_found = re.findall(email_regex, source, re.IGNORECASE)

   return emails_found

  def screengrab(self, file_name: str):
   try:
    # Close every modal should any arise
    ActionChains(self._driver).send_keys(Keys.ESCAPE).perform()

    self._driver.find_element_by_tag_name('body').screenshot(file_name)

   except NoSuchElementException as e:
    println(f"We experienced an issue while trying to screenshot this website ({self._site_content['url']})", "warn")


  def extract_mobile_number(self, found_numbers: list) -> list:
    number_list: list = []
    final_phone_regex = "[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]"
    strip_regex =  r"[\-\(\) .]"
    for number in found_numbers:
      number = re.search(final_phone_regex, number, re.IGNORECASE)
      if number:
        number = re.sub(strip_regex, "", number.group(0))
        total_count = len(number)
        if total_count > 10 and total_count < 15:
          if(number not in number_list): number_list.append(number)

    return number_list

  def extract_real_email_address(self, found_emails: list) -> list:
    # Sometimes images take the form of an email address
    email_list: list = []
    check_against_strings = (".png", ".jpg", ".jpeg", ".mv", ".mp3", ".mp4", ".gif", ".webp")
    for email in found_emails:
      if email.endswith(check_against_strings) is False:
        if(email not in email_list): email_list.append(email)

    return email_list

  def write_to_file(self, data: dict):
    #------------------------------------------------------------------------
    # We check if the file already exist before we being, if the file
    # Exist, we simply append the new data as the header for the CSV file has
    # Already be created
    # Else we add CSV header first before adding the data to file
    #------------------------------------------------------------------------
    extracted_path = Path("extracted/")
    save_file_to = extracted_path / f"{self._file_name}.csv"
    file_path_object = Path(save_file_to)
    file_exist = file_path_object.is_file()
    if file_exist is False:
      Path(save_file_to).touch()

    with open(save_file_to, 'a', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        # Add header only if the file doesn't exist
        if file_exist is False: writer.writerow(data.keys())
        # Add new data 
        writer.writerow(data.values())
        file.close()
