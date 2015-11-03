import requests
import json
from bs4 import BeautifulSoup

BASE_URL = 'http://data.worldbank.org/indicator'

HTML = ''

jobsList = []

world_bank_data = []

#DIRTY access to WB data
try:

    doc = requests.get(BASE_URL)
    soup = BeautifulSoup(doc.text, 'html.parser')

    indicator_tables = soup.find_all("table")
    topics = soup.find_all("h3", {"class": 'view'})

    for table_index in range(0, 30):
        try:

            topic_data = {}

            topic_text = topics[table_index].text
            topic_data[topic_text] = []

            indicators_table = indicator_tables[table_index]
            indicators = indicators_table.find_all("a", href=True)
            for indicator in indicators:
                topic_data[topic_text].append({
                    'label': indicator.text,
                    'code': indicator['href'].split('/')[4]
                })

            world_bank_data.append(topic_data)
        except Exception, e:
            print e

except Exception, e:
    print e

# print world_bank_data

import json
with open('data.json', 'w') as outfile:
    json.dump(world_bank_data, outfile)

