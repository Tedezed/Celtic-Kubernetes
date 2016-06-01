[Index](1-Portada.md) - [Anterior](7-Explotando_kubernetes.md)

---------------------------------

Kubernetes Ansible
==================

Instalación de Kubernetes mediante Ansible con un nodo master simple

Configuración de nombres `sudo nano /etc/hosts`

	192.168.33.10	centos-master1
	192.168.33.11	centos-node1
	192.168.33.12	centos-node2

Clonamos el repositorio `git clone https://github.com/kubernetes/contrib.git`

Entramos al directorio con `cd contrib/ansible`

Editamos y añadimos los nodos

`nano inventory.example.single_master`

	[masters]
	192.168.33.10

	[etcd]
	192.168.33.10

	[nodes]
	192.168.33.11
	192.168.33.12


En los nodos añadimos una clave publica para poder acceder al usuario root por ssh

`mkdir .ssh`

`touch .ssh/authorized_keys`

`chmod 755 ~/.ssh`

`chmod 644 ~/.ssh/authorized_keys`

Editamos `all.yml` con la configuración siguiente

`nano group_vars/all.yml`

	ansible_ssh_user: root
	ssh-keygen
	source_type: packageManager
	# Red
	kube_service_addresses: 10.254.0.0/16
	cluster_logging: true
	cluster_monitoring: true
	dns_setup: true

**ERROR:**
`msg: mode needs to be something octalish`

**SOLUCION:** ansible>1.9.0

	apt-get -t jessie-backports install ansible

Ejecutamos con
	./setup.sh -i inventory.example.single_master

Listamos los minions:

`kubectl get nodes`

	NAME            LABELS                                 STATUS    AGE
	192.168.33.11   kubernetes.io/hostname=192.168.33.11   Ready     1m
	192.168.33.12   kubernetes.io/hostname=192.168.33.12   Ready     1m


----------------------

[Index](1-Portada.md) - [Anterior](7-Explotando_kubernetes.md)