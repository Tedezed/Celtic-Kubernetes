#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By https://github.com/Tedezed

from json import loads, load
from requests import get
from jinja2 import Environment, FileSystemLoader
from os import system, path

def get_kube_api(kube_api, version, get_type):
	request = get('http://%s/api/%s/%s/' % (kube_api, version, get_type))
	json_api = loads(request.text)
	return json_api

# Load configuration
def get_conf(directory):
	with open(directory+'configuration.json') as data_file:    
    		data = load(data_file)
    	return data

def reload():
	system('sh haproxy_reload')
