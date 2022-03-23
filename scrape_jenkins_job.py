#!/usr/bin/python3

"""
SIMPLE PYTHONIC SCRIPT TO SCRAP DATA IN JENKINS by Given Jenkins Job URL 

JENKINS JOB URL Example: http://localhost:8080/job/portal/job/publish/job/master/

NOTE: SCRIPT PRODUCES OUTPUT in CSV

"""


import datetime
import json
import math
import requests
import csv
import argparse
import os
import logging
import copy 
import xlsxwriter
from collections import OrderedDict 

__author__ = "Kumar Pratik"


#All variables
_main_api="api/json? tree=builds[number,status,timestamp,id,result,duration]"
_build_api="api/json?pretty=true"
_workflow_api="wfapi/"

# millisecs = 1584984095151
# https://stackoverflow.com/questions/39780403/python3-read-json-file-from-url
# https://stackoverflow.com/questions/748491/how-do-i-create-a-datetime-in-python-from-milliseconds
# https://stackoverflow.com/questions/10624937/convert-datetime-object-to-a-string-of-date-only-in-python
# https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python

def argument_formator():
    """
    :return: Return formatted arguments
    """
    parser = argparse.ArgumentParser(description='Scrap Jenkins Job Metrics from API endpoints')
    parser.add_argument('--job', '-j', help='Please enter jenkins Job URL Example: http://localhost:8080/job/portal/job/publish/job/master/  Note: forward slash in the end is needed', required=True)
    parser.add_argument('--filename', '-f', help='File name is used for creating CSV files in the current folder script running Example: portal_cube0branhch', required=True)
    parser.add_argument('--step', '-s', help='This is used for pipeline step duration calucation, add -s if you want to calculate timestamp for each pipeline steps Note: Your jenkins should be pipeline job', action='store_true', default=False)
    return parser.parse_args()

def get_job_data():
    arg = argument_formator()
    _top_level_url= "{0}{1}".format(arg.job,_main_api)
    logging.info('Entering into the job "+_top_level_url+"')
    _res_json=json.loads(requests.get(_top_level_url).text)
    return _res_json
    
def get_build_urls():
    _build_urls = []
    _res_js = get_job_data()
    for build in _res_js['builds']:
        _build_urls.append(build['url'])
    if _build_urls:
      logging.info("We found some jenkins build urls from given jenkins job")
    return _build_urls

def get_build_data_nostep():
    _builds = get_build_urls()
    _build_duration_timestamp = []
    for each_build in _builds:
      _each_build_api = "{0}{1}".format(each_build,_build_api)
      response = json.loads(requests.get(_each_build_api).text)  # response is a dict
      millisecs = response['timestamp']
      _date_cal = datetime.datetime.fromtimestamp(millisecs/1000.0)
      mystr = _date_cal.strftime('%Y-%m-%d_%H:%M')
      duration_in_msec = response['duration'] 
      duration_in_mi = duration_in_msec / 60000   # 60,000 ms == 1 min
      # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
      duration_in_min = round(duration_in_mi, 2)
      result = response['result']
      output_dict_for_excel = {'build_no': each_build,'duration':duration_in_min,'timestamp':mystr, 'result':result}
      _build_duration_timestamp.append(output_dict_for_excel)
      logging.info(output_dict_for_excel)
      # all data will be returned in the format {'build_no': each_build,'duration':duration_in_min,'timestamp':mystr}
    
    return  _build_duration_timestamp

def get_build_data_withstep():
    _builds = get_build_urls()
    _build_duration_timestamp = []
    _workflow_list = []
    for each_build in _builds:
      _each_build_api = "{0}{1}".format(each_build,_build_api)
      resip = requests.get(_each_build_api)
      response = resip.json()  # response is a dict
      millisecs = response['timestamp']
      _date_cal = datetime.datetime.fromtimestamp(millisecs/1000.0)
      mystr = _date_cal.strftime('%Y-%m-%d_%H:%M')
      duration_in_msec = response['duration'] 
      duration_in_mi = duration_in_msec / 60000   # 60,000 ms == 1 min
      # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
      duration_in_min = round(duration_in_mi, 2)
      output_dict_for_excel = {'build_no': each_build,'duration':duration_in_min,'timestamp':mystr}
      _each_wf_api = "{0}{1}".format(each_build,_workflow_api) 
      reps = requests.get(_each_wf_api)
      response_wf = reps.json()
      logging.info("Validating things for Workflow API starting loops")
      for stage in response_wf['stages']:
        stage_name = stage['name']
        status_result = stage['status']
        duration_in_msecs = stage['durationMillis']
        duration_in_mix = duration_in_msecs / 60000
        duration_in_min = round(duration_in_mix, 2)
        workflow_final = (stage_name, duration_in_min, status_result)
        _workflow_list.append(workflow_final)
      output_dict_for_excel.update({'stages': copy.deepcopy(_workflow_list)})
      _build_duration_timestamp.append(output_dict_for_excel)
      del _workflow_list[:]
      logging.info(output_dict_for_excel)
      # all data will be returned in the format {'build_no': each_build,'duration':duration_in_min,'timestamp':mystr}
    return  _build_duration_timestamp
      
def write_csv():
    arg = argument_formator()
    #if its not for pipeline validation returns only each build duration and timestamp
    if not arg.step:
      #{'build_no': each_build,'duration':duration_in_min,'timestamp':mystr} is all data
      all_data_formatted = get_build_data_nostep()
      with open(arg.filename+".csv", 'w') as _file:
          _fields = ['Jenkins Build URL', 'Duration', 'Time Stamp', 'Status']
          writer = csv.DictWriter(_file, _fields)
          writer.writeheader()
          for each in all_data_formatted:
              writer.writerow({'Jenkins Build URL': str(each['build_no']) , 'Duration':str(each['duration']), 'Time Stamp': str(each['timestamp']), 'Status': str(each['result'])})
          
    if arg.step:
       all_data_formatted = get_build_data_withstep()
       #with open(arg.filename+".csv", 'w') as _file:
       #{'build_no': 'ssdsd', 'duration': 'sdsd', 'timestamp': 'sd', 'stages': [('deploy', 111), ('create', 233)]}
       val = []
       shet = 1
       workbook = xlsxwriter.Workbook(arg.filename+".xlsx") 
       for each in all_data_formatted:
          worksheet = workbook.add_worksheet("Job"+str(shet))
          val.append(each['build_no'])
          val.append(each['duration'])
          val.append(each['timestamp'])
          
          for x in each['stages']:
            sta = (x[0], x[1], x[2])
            val.append(sta)
         
          value = copy.deepcopy(val)
          writes = (value)
          row = 0
          col = 0
           
          for a in (writes):
            worksheet.write(row, col, str(a))
            col+=1
          del val[:]
          shet+=1
          
       workbook.close() 
               
if __name__ == "__main__":
    write_csv()
