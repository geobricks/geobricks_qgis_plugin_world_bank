import urllib2
import json

def get_data_by_year(data, year):
    data_yearly = []
    for d in data:
        if d['date'] == year and d['value'] is not None:
            data_yearly.append(d)
    return data_yearly

def get_world_bank_data(indicator, from_year, to_year):
    request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + from_year + ':' + to_year+'&format=json&per_page=10000'
    req = urllib2.Request(request)
    response = urllib2.urlopen(req)
    json_data = response.read()
    if json_data:
        return json.loads(json_data)[1]
    else:
        return None

def get_world_bank_data_single_year(indicator, year):
    request = 'http://api.worldbank.org/countries/all/indicators/' + indicator + '?date=' + year + '&format=json&per_page=10000'
    req = urllib2.Request(request)
    response = urllib2.urlopen(req)
    json_data = response.read()
    if json_data:
        return json.loads(json_data)
    else:
        return None


def get_world_bank_topics():
    req = urllib2.Request('http://api.worldbank.org/topics/?per_page=1500&format=json')
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]

def get_world_bank_indicators(source_id):
    req = urllib2.Request('http://api.worldbank.org/source/' + str(source_id) + '/indicators?per_page=1500&format=json')
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]

def get_world_bank_indicators_by_topic(topic_id):
    req = urllib2.Request('http://api.worldbank.org/topic/' + str(topic_id) + '/indicator?per_page=1500&format=json')
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)[1]
    
    
