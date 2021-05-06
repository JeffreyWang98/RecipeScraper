How to use this crawler

Open command line

Set up virtual environment with the command (this should already be created)
python -m venv recipe-env

Activate the virtual environment for this session
recipe-env\Scripts\activate.bat

Run the crawler, which saves each recipe to individual json files
> scrapy crawl chefspider

Test the html parser
:run genius_kitchen_parser.py and replace url in main()

Combine the json files to one collective
:run combine_jsons.py
The result is in 'combined.json'