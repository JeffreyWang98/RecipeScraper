How to use this crawler

Run the crawler, which saves each recipe to individual json files
> scrapy crawl chefspider

Test the html parser
:run genius_kitchen_parser.py and replace url in main()

Combine the json files to one collective
:run combine_jsons.py
The result is in 'combined.json'