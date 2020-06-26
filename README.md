# google-scraper
 A simple web scraper that makes it easy for marketers to extract emails and phone numbers (leads) from google search results.
 
# Process
Quite a simple process, you simply enter your search query with optional start and stop pages. The system will load up your query headlessly, meaning you wouldn't even see it while it does its scrapping.
This scraper will scrape phone numbers and email addresses including a full screenshot of the webpages and navigate google search pages until it gets to page 15 (if you didn't sent a stop number).

# How to run it
To start you would need to activate the local environment
 ## For linux/Mac:
   source env/bin/activate
 ## For Windows (not supported):
   Windows is not supported for now
##
1. Then you install the requirements in "requirements.txt"
2. run: python3 main.py "(query)" (start page) (stop page)
 
