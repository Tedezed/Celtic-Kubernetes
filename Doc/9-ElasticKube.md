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

* elastickube-server
* elastickube-mongo

Necesitas:

* Funcionamiento correcto de kubectl
* Tener disponible namespace kube-system.
* Ingress o en su defecto NodePort.

Instalación:
	
	curl -s https://elastickube.com | bash
