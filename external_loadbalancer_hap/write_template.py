#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By https://github.com/Tedezed

from json import loads, load
from requests import get
from jinja2 import Environment, FileSystemLoader
from manager_tools import *

def write_template_conf(directory):
	data = get_conf(directory)
	kube_api = data["kube_api"]
	version = data["version"]
	file_conf = data["file_conf"]
	stats = data["stats"]

	get_json_svcs = get_kube_api(kube_api, version, 'services')['items']
	get_json_nodes = get_kube_api(kube_api, version, 'nodes')['items']

	j2_env = Environment(loader=FileSystemLoader(directory+'templates'),
                         trim_blocks=True)
	template_render = j2_env.get_template(file_conf).render(
    	json_svcs=get_json_svcs, 
    	json_nodes=get_json_nodes,
    	stats=stats
	)

	file_conf =open('/etc/haproxy/template.cfg','w')
	file_conf.write(template_render)
	file_conf.close()