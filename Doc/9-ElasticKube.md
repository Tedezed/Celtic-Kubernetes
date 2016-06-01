ElasticKube
===========

Características de ElasticKube
------------------------------

ElasticKube trae las siguientes características:

* Autenticación: Esta interfaz nos permite tener un control de acceso para Kubernetes, permitiendo establecer permisos y visibilidad sobre el cluster a usuarios específicos.
* Catálogo de plantillas: ElasticKube nos ofrece un conjunto de plantillas de recursos comunes para facilitarnos el despliegue de nuestros servicios.
* Reportes en tiempo real: Nos permite monitorizar las actividades que se realizan en los contenedores.
* Colaboración: Permite que los desarrolladores puedan definir, desplegar y administrar aplicaciones y servicios en producción.
* Rolling Updates: La trazabilidad y control sobre la aplicación nos permiten entregar valor constantemente.
* Administración: Desde la interfaz se pueden desplegar servicios, manejar usuarios, namespaces, plantillas y recursos.


Servicios
---------

* elastickube-mongo
* elastickube-server
* elastickube-api
* elastickube-charts
* elastickube-nginx
* elastickube-diagnostics

Necesitas:

* Funcionamiento correcto de kubectl
* Tener disponible namespace kube-system.
* Ingress o en su defecto NodePort.

Instalación:
	
	curl -s https://elastickube.com | bash

Salida del comando

	[root@morrigan centos]# curl -s https://elastickube.com | bash
	  _____ _           _   _      _  __     _
	 | ____| | __ _ ___| |_(_) ___| |/ /   _| |__   ___
	 |  _| | |/ _` / __| __| |/ __| ' / | | | '_ \ / _ \
	 | |___| | (_| \__ \ |_| | (__| . \ |_| | |_) |  __/
	 |_____|_|\__,_|___/\__|_|\___|_|\_\__,_|_.__/ \___| by ElasticBox

	Checking kubectl is available           [ ✓ ]
	Verifying Kubernetes cluster            [ ✓ ]
	Setting up elastickube-server svc       [ ✓ ]
	Setting up elastickube-mongo svc        [ ✓ ]
	Setting up elastickube-mongo            [ ✓ ] 
	Setting up elastickube-server           [ ✓ ] 
	WARNING: LoadBalancer Ingress not detected, please ensure the address is accessible from outside the cluster. Check http://kubernetes.io/docs/user-guide/ingress/ for more information.
	Waiting for LB to be ready              [ ✓ ] 

	ElasticKube has been deployed!
	Please complete the installation here: http://10.254.96.57


En mi caso para acceder utilizare NodePort

	kubectl --namespace=kube-system describe svc elastickube-server | grep NodePort

Si tenemos funcionando HAProxy dinamico, podremos entrar con la IP del ClusterIP del balanceador y el nombre del servicio elastickube-server.

	apiVersion: v1
	kind: Service
	metadata:
	  name: kubernetes-elastickube
	  namespace: kube-system
	  labels:
	    name: kubernetes-elastickube
	spec:
	  type: NodePort
	  ports:
	  - port: 80
	    protocol: TCP
	    targetPort: 80
	  selector:
	    name: elastickube-server

Podriamos entrar con `tanaris/kubernetes-elastickube/`

Creamos el usuario Administrador; admin/adminadmin

