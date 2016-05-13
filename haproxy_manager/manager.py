#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By https://github.com/Tedezed

from json import loads, load
from requests import get
from time import sleep
from deepdiff import DeepDiff
from manager_tools import *
from write_template import *

data = get_conf()
kube_api = data["kube_api"]
version = data["version"]
time_sleep = data["sleep"]

dic_svc_old = {}
while True:
	dic_svc_actives = {}
	get_json_svcs = get_kube_api(kube_api, version, 'services')['items']
	for svc in get_json_svcs:
		try:
			svc_node_port = svc['spec']['ports'][0]['nodePort']
			svc_name = svc['metadata']['name']
			if svc_name not in dic_svc_actives:
				dic_svc_actives[svc_name] = svc_node_port
		except KeyError:
			pass
	ddiff = DeepDiff(dic_svc_actives, dic_svc_old)
 	if ddiff:
	 	print "Reload HAProxy"
	 	write_template_conf()
	dic_svc_old = dic_svc_actives
	sleep(time_sleep)l