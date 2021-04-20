
# Google-Leads-Scraper
 A simple web scraper that makes it easy for marketers to extract emails and phone numbers (leads) from google search results.
 
# Process
Quite a simple process, you simply enter your search query, file-name to store the data, start and stop to denote number of pages to scrape. The system will load up your query headlessly, meaning you wouldn't even see it while it does its scrapping.
This scraper will scrape phone numbers and email addresses including a full screenshot of the webpages and navigate google search pages until it gets to your inputed stop page.

# Get Started:
To start you would need to activate the virtual environment
 ## For linux/Mac:

       source env/bin/activate

 ## For Windows (not supported):
	

    .\env\Scripts\activate

 ##
   
   
1. `python3 --version (supports 3.7 and above)`
2. `pip3 install -r requirements.txt`
3. `python3 main.py "my query" --start=1 --stop=5 --file="a_file_name_to_save_data"`

# Note:
A screenshot of websites the scraper visits is taken and stored in the STATIC folder.



***Please share and support this libary with your code contributions.***
