import requests
import json
from copy import deepcopy
import pandas
from string import Template

def read_file(filename):
  return open(str(filename), 'r').read()

def cross_join(left, right):
    new_rows = []
    for left_row in left:
        for right_row in right:
            temp_row = deepcopy(left_row)
            for key, value in right_row.items():
                temp_row[key] = value
            new_rows.append(deepcopy(temp_row))
    return new_rows


def flatten_list(data):
    for elem in data:
        if isinstance(elem, list):
            yield from flatten_list(elem)
        else:
            yield elem

def insert_space(word, index):
  return word[:index] + ' ' + word[index:]

def capitalize_headers(headers):
  return headers[:1].capitalize() + headers[1:]

def clean_headers(prev_heading):
  filter_heading = prev_heading.rindex('.')
  prev_heading = prev_heading[filter_heading + 1:]
  for i in prev_heading:
    if i.isupper() == True:
      num = prev_heading.index(i)
      prev_heading = insert_space(prev_heading, num)
  prev_heading = capitalize_headers(prev_heading)
  return prev_heading

def json_to_dataframe(data_in):
    def flatten_json(data, prev_heading=''):
        if isinstance(data, dict):
            rows = [{}]
            for key, value in data.items():
                rows = cross_join(rows, flatten_json(value, prev_heading + '.' + key))
        elif isinstance(data, list):
            rows = []
            for i in range(len(data)):
                [rows.append(elem) for elem in flatten_list(flatten_json(data[i], prev_heading))]
        else:
            prev_heading = clean_headers(prev_heading)
            rows = [{prev_heading: data}]
        return rows

    return pandas.DataFrame(flatten_json(data_in))


cursor = "Y3Vyc29yOjM="
final = pandas.DataFrame()
has_next_page = True

while has_next_page == True:
  json_query = read_file("GitHub_activity.graphql")
  url = 'https://api.github.com/graphql'
  headers = {"Authorization": "Bearer 533a0bf06c327c57484f177a1bb0f7922a2e849a"}
  json_query = json_query.replace("MYCURSOR", cursor)
  r = requests.post(url, json={'query': json_query}, headers=headers)
  json_data = json.loads(r.text)

  
  AJ_data = json_data['data']['nodes']
  spreadsheet = json_to_dataframe(AJ_data)
  print(spreadsheet)
  final = final.append(spreadsheet, ignore_index=True)
  if len(spreadsheet.index) == 3:
    has_next_page = spreadsheet.iloc[2]['Has Next Page']
    cursor = spreadsheet.iloc[2]['Cursor']
  else:
    has_next_page = False
final.to_csv('test_Pandaspreadsheet11.csv')
