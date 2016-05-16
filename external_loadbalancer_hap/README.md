External Loadbalancer for HAProxy
=================================

Inspired by [service-loadbalancer](https://github.com/kubernetes/contrib/tree/master/service-loadbalancer)

#### Instalation

Clone repository

	git clone https://github.com/Tedezed/Celtic-Kubernetes.git

Install basic sowftware

	yum install epel-release
	yum install haproxy
	yum install python-pip
	pip install jija2
	pip install deepdiff

Create errors html

	mkdir /etc/haproxy/errors/
	cp /Celtic-Kubernetes/haproxy_manager/errors/* /etc/haproxy/errors/

Create state global

	mkdir -p /var/state/haproxy/
	touch  /var/state/haproxy/global

Modify configuration.json
	
	{
	"kube_api": "morrigan:8080",
	"version": "v1",
	"file_conf": "template.cfg",
	"stats": true,
	"sleep": 3
	}

* Kube API master
	
		"kube_api": "10.0.0.39:8080"

#### Test

	python hap_manager_daemon.py start
	python hap_manager_daemon.py stop

#### Unit for systemd

Copy file hap_manager.service

	cp /Celtic-Kubernetes/external_loadbalancer_hap/system/hap_manager.service /lib/systemd/system/hap_manager.service

Modify permissions

	chmod 644 /lib/systemd/system/hap_manager.service

Reload daemon systemctl

	systemctl daemon-reload

Start hap_manager.service

	systemctl start hap_manager.service

	systemctl enable hap_manager.service