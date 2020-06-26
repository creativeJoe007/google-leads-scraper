import json
import re
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

class Extractor():
 #------------------------------------------------------------------------
 # This is where we extract all the data we need while scrapping
 # We take our screenshots here, get titles, find social media pages
 #  Of users we extract
 #------------------------------------------------------------------------
 def __init__(self, driver, query, start_page, stop_page):
  self._driver = driver
  self._data_extract = []
  self._page = start_page # start counting from zero due to google's seek algorithm
  self._stop_page = stop_page # start counting from zero due to google's seek algorithm

  # We loop through the enter data wrapped under pagination
  self.paginate_page(query)

 def paginate_page(self, query):
    #------------------------------------------------------------------------
    # We are going to fetch all first 10 pages
    # Of google's result
    #------------------------------------------------------------------------
    start_url = f"https://www.google.com/search?q={query}&oq=&aqs=chrome.0.35i39l8.13736357j0j1&sourceid=chrome&ie=UTF-8"
    seek_number = 0
    seek_url_query = f"&start={seek_number}"

    # while self._page <= 9:
    while self._page <= self._stop_page:
      self._driver.get(start_url + f"&start={(self._page * 10)}")
      self.extract_page_content()
      self._page += 1

      # Save extracted files into JSOn format after ever page is processed
      with open('extracts.json', 'w') as outfile:
        json.dump(self._data_extract, outfile)
        outfile.close()

 def words_in_string(self, word_list, a_string):
    return set(word_list).intersection(a_string.lower().split())

 def extract_page_content(self):
    #------------------------------------------------------------------------
    # We are going to get all major links in a page
    # Match that they do not contain the words
    # "english", "translate" or "translation"
    # Any item that passes this page would be considered for scrapping
    #------------------------------------------------------------------------
    dictionary_words = ["english", "translate", "translation", "dictionary", "Thesaurus", "translations"]
    _site_content = {
      'title': '',
      'url': '',
      'description': '',
      'site_description': '',
      'screen_shot': '',
      'contact_email': '',
      'contact_number': ''
    }
    response = self._driver.find_elements_by_css_selector("div.g")

    # Now we look through all search results
    for result in response:
      google_result = result.find_element_by_css_selector("div.rc")

      _site_content['title'] = google_result.find_element_by_css_selector("div.r")\
        .find_element_by_css_selector("h3.LC20lb.DKV0Md").text

      _site_content['description'] = google_result.find_element_by_css_selector("div.s")\
        .find_element_by_css_selector("span.st").text

      _site_content['url'] = google_result.find_element_by_css_selector("div.r")\
        .find_element_by_tag_name("a").get_attribute("href")

      if(not self.words_in_string(dictionary_words, _site_content['title']) and \
        not self.words_in_string(dictionary_words, _site_content['description'])):
          #------------------------------------------------------------------------
          # This website is not a dictionary, now we can start 
          # scanning through to extract just
          # The data we need
          #------------------------------------------------------------------------
          if "youtube" in _site_content['url']:
            continue;
          elif "facebook" in _site_content['url']:
            #------------------------------------------------------------------------
            # First we split by "/"
            # We check if the last "/" is empty in case the URL ended with "/"
            # If its empty we use the second to last
            # If its not empty we check if the value contains "?" meaning a query
            # If it does, we still use second to last
            #------------------------------------------------------------------------
            split_page_url_list = _site_content['url'].split("/")
            page_name = ""

            if split_page_url_list[len(split_page_url_list) - 1] == "":
              page_name = split_page_url_list[len(split_page_url_list) - 2]
            else:
              if "?" in split_page_url_list[len(split_page_url_list) - 1]:
                page_name = split_page_url_list[len(split_page_url_list) - 2]
              else:
                page_name = split_page_url_list[len(split_page_url_list) - 1]
            
            _site_content['url'] = f"https://web.facebook.com/pg/{page_name}/about/";

          print("\n")
          print(_site_content['url'])
          self.extract_info_from_link(_site_content)

      # print("\n")
      # print(_site_content['title'])

 def extract_info_from_link(self, _content):
    #------------------------------------------------------------------------
    # We will access all the different websites, and
    # extract every email address, and phone number
    # Found in them
    #------------------------------------------------------------------------

    # Load up a new tab to handle this
    self._driver.execute_script("window.open('');")
    self._driver.switch_to.window(self._driver.window_handles[len(self._driver.window_handles) - 1])

    self._driver.get(_content['url'])
    time.sleep(5)
    
    html_source = self._driver.find_element_by_tag_name('body').get_attribute('innerHTML')
    extracted_numbers = ""
    extracted_emails = ""

    # Now we use regex to match all occurrences of email or phone numbers in the page source
    # print(html_source)
    try:
      # _content['title'] = self._driver.find_element_by_tag_name('title').text
      _content['site_description'] = self._driver.find_element_by_xpath("//meta[@name='description']")\
        .get_attribute("content")
    except NoSuchElementException as e:
      print("There is an issue with the social media pages")

    screen_shot_name = 'static/' + _content["title"].replace("[,\.!\*- ]", "_") + '.png'

    found_numbers = self.scan_for_numbers(html_source)
    found_emails = self.scan_for_emails(html_source)
    verified_numbers = self.extract_mobile_number(found_numbers)
    print(f"verified_numbers {verified_numbers}")
    print(f"found_numbers {found_numbers}")
    
    if len(verified_numbers) or len(found_emails):
      # Increase the size of the page for our screenshot
      self._driver.set_window_size(1920, 8000)
      self.screengrab(screen_shot_name);
      _content['screen_shot'] = screen_shot_name;

      # We are done with processing now lets add to our list
      self._data_extract.append(_content)

    # Close new tab first
    self._driver.close()
    self._driver.switch_to.window(self._driver.window_handles[len(self._driver.window_handles) - 1])

 def scan_for_numbers(self, source, index=0):
    found_numbers = []
    phone_regex = [
      "\+[\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]", # Priority 1
      "((tel|p|t|phone|call|dial|ring)[: -]?[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9])", # Priority 2
      # "[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]" # Priority 3
    ]

    for regex in phone_regex:
      is_found = re.findall(regex, source, re.IGNORECASE)
      if len(is_found) > 0:
        if type(is_found[0]) is tuple:
          # Our second regex returns a tuple instead of a string like the other one
          # I haven't figured how to resolve that but this is just a work around
          found_numbers = [is_found[0][0]]
        else: found_numbers = is_found
        break;
    
    return found_numbers

 def scan_for_emails(self, source):
   extracted_email_addresses = []
   email_regex = "[a-zA-Z0-9.#$%&'*+=?^_`|~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
   emails_found = re.findall(email_regex, source, re.IGNORECASE)

   return emails_found

 def screengrab(self, file_name):
   try:
    # Close every modal should any arise
    ActionChains(self._driver).send_keys(Keys.ESCAPE).perform()

    # self._driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    self._driver.find_element_by_tag_name('body').screenshot(file_name)

   except NoSuchElementException as e:
    print("There is an issue with the social media pages")


 def extract_mobile_number(self, found_numbers):
    number_list = []
    final_phone_regex = "[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]"
    reg =  r"[\-\(\)\+ .]"
    for number in found_numbers:
      print(f'number {number}')
      number = re.search(final_phone_regex, number, re.IGNORECASE)
      if number:
        number = number.group(0)
        total_count = len(re.sub(reg, "", number))
        if total_count > 9 and total_count < 14:
          if(number not in number_list): number_list.append(number)
    
    return number_list