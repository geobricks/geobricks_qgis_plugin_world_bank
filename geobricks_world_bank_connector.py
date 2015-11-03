import urllib2
import json
import datetime

# per_page worldbank limit
PER_PAGE = '10000'

def get_data_by_year(data, year):
    data_yearly = []
    for d in data:
        if d['date'] == year and d['value'] is not None:
            data_yearly.append(d)
    return data_yearly

def get_world_bank_data(indicator, from_year, to_year):
    request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + from_year + ':' + to_year+'&format=json&per_page=' + PER_PAGE
    print request
    req = urllib2.Request(request)
    response = urllib2.urlopen(req)
    json_data = response.read()
    if json_data:
        return json.loads(json_data)[1]
    else:
        return None

def get_world_bank_data_single_year(indicator, year):
    request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + year + '&format=json&per_page=' + PER_PAGE
    req = urllib2.Request(request)
    response = urllib2.urlopen(req)
    json_data = response.read()
    if json_data:
        return json.loads(json_data)
    else:
        return None


def get_world_bank_topics():
    req = urllib2.Request('http://api.worldbank.org/topics/?per_page=' + PER_PAGE + '&format=json')
    print req
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]

def get_world_bank_indicators(source_id):
    req = urllib2.Request('http://api.worldbank.org/source/' + str(source_id) + '/indicators?per_page=' + PER_PAGE + '&format=json')
    print req
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]

def get_world_bank_indicators_by_topic(topic_id):
    req = urllib2.Request('http://api.worldbank.org/topic/' + str(topic_id) + '/indicator?per_page=' + PER_PAGE + '&format=json')
    print req
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]


def get_all_topics():
    data = get_all_indicators()
    per_page = 100
    topics = {}
    topics_list = []
    for index, d in enumerate(data):
        if len(d['topics']) > 0:
            if 'value' in d['topics'][0]:
                topic_value = d['topics'][0]['value'].strip()
                indicator_id = d['id']
                indicator_name = d['name']

                if topic_value in topics:
                    if len(topics[topic_value]['indicators']) > per_page:
                        page = page+1 if 'page' in topics[topic_value] else 2
                        topic_value = (topic_value + ' (' + str(page) + ')').strip()
                        topics[topic_value] = {
                            'indicators': [],
                            'page': page
                        }
                        topics_list.append(topic_value)



                elif topic_value not in topics:
                    topics[topic_value] = {
                        'indicators': [],
                        'pages': 1
                    }
                    topics_list.append(topic_value)

                print indicator_id, indicator_name, topic_value

                topics[topic_value]['indicators'].append({
                    'id':  indicator_id,
                    'name':  indicator_name
                })
    return topics_list, topics

def get_all_indicators():
    a = datetime.datetime.now()
    req = urllib2.Request('http://api.worldbank.org/indicators?per_page=10000&format=json')
    response = urllib2.urlopen(req)
    json_data = response.read()
    b = datetime.datetime.now()
    c = b - a
    print c.seconds
    return json.loads(json_data)[1]

