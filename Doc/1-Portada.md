<div id="header"> 
 <ul>
  <li><a class="active" href="1-Portada.md">Home</a></li>
  <li><a class="bar" href="2-Kube_simple.md">Kubernetes Simple</a></li>
  <li><a class="bar" href="3-Kube_HA_pcs.md">Kubernetes HA</a></li>
  <li><a class="bar" href="4-Addons.md">Addons</a></li>
  <li><a class="bar" href="5-Exponer_svc.md">Exponer servicios</a></li>
  <li><a class="bar" href="6-Almacenamiento.md">Almacenamiento persistente</a></li>
  <li><a class="bar" href="7-Explotando_kubernetes.md">Utilización</a></li>
  <li><a class="bar" href="8-Kubernetes_ansible.md">Kubernetes y Ansible</a></li>
  <li><a class="bar" href="9-ElasticKube.md">ElasticKube</a></li>
  <li><a class="bar" href="10-Conclusion.md">Conclusión</a></li>
  <li style="float:bottom"><a class="bar" href="Contacto.md">Contacto</a></li>
</ul>
</div>
<div id="control"> 
 <ul>
  <li style="float:right"><a class="next" href="2-Kube_simple.md">Siguiente</a></li>
</ul>
</div>

Kubernetes Cluster HA sobre OpenStack
=====================================

Proyecto Celtic Kubernetes de fin de ciclo de ASIR (sysadmin) IES Gonzalo Nazareno (Dos Hermanas, España)

El escenario tiene sus nombres tomados de los dioses Celtas de la siguiente entrada de la Wikipedia [enlace](https://es.wikipedia.org/wiki/Categor%C3%ADa:Dioses_celtas) donde podrás consultar su descripción.

* [Autor](Contacto.md)

Índice de contenido
-------------------
*******************
1. [Portada proyecto](1-Portada.md)
2. [Despliegue simple Kubernetes](2-Kube_simple.md)
3. [Despliegue Kubernetes cluster en HA masters y minions](3-Kube_HA_pcs.md)
4. [Addons para Kubernetes](4-Addons.md)
5. [Exponer servicios internos de Kubernetes](5-Exponer_svc.md)
6. [Almacenamiento persistente para Kubernetes](6-Almacenamiento.md)
7. [Explotando Kubernetes](7-Explotando_kubernetes.md)
8. [Kubernetes con Ansible](8-Kubernetes_ansible.md)
9. [ElasticKube](9-ElasticKube.md)
10. [Conclusión](10-Conclusion.md)

#### Los nombres elegidos para los nodos del cluster HA son

| Nombre      | Función         | Numero  |
|-------------------|-----------------------|-----------|
| [**Taranis**](https://es.wikipedia.org/wiki/Taranis)    | Proxy         | 1     |
| [**Belenus**](https://es.wikipedia.org/wiki/Belenus)    | Proxy         | 2     |
| [**Morrigan**](https://es.wikipedia.org/wiki/Morrigan)    | KMaster         | 1     | 
| [**Balar**](https://es.wikipedia.org/wiki/Balar)      | KMaster         | 2     |
| [**Artio**](https://es.wikipedia.org/wiki/Artio)      | KMinion       | 1     |
| [**Esus**](https://es.wikipedia.org/wiki/Esus)    | KMinion         | 2     |
| [**Angus**](https://es.wikipedia.org/wiki/Angus_(mitología))      | Almacenamiento    | 1     |
| [**Dagda**](https://es.wikipedia.org/wiki/Dagda)      | Almacenamiento    | 2     | 


#### Presentación

[Presentación Cluster Kuberentes HA](http://slides.com/tedezed/deck-1#/)

<iframe src="http://slides.com/tedezed/deck-1#/" width="99%" height="400"></iframe>

-----------------------------

## Definiendo Kubernetes

<hr>

Kubernetes es un orquestador de [contenedores](https://github.com/kubernetes/kubernetes/wiki/Why-Kubernetes%3F#why-containers) open source a través de múltiples hosts, proporcionar mecanismos básicos para el despliegue, mantenimiento y escalado de aplicaciones.

Kubernetes es:

* **liviano**: ligero, sencillo, accesible
* **portable**: publico, privado, hibrido, multi cloud
* **extensible**: modular
* **Autonomo**: gestion de contenedores de forma autonoma

Kubernetes se basa en una [década y media de experiencia en Google para ejecutar cargas de trabajo de producción](https://research.google.com/pubs/pub43438.html), combinado con las ideas y las mejores prácticas de la comunidad.

<hr>

## Conceptos

Kubernetes trabaja con los siguientes conceptos:

[**Cluster**](https://github.com/kubernetes/kubernetes/blob/master/docs/admin/README.md)
Un cluster es un conjunto de máquinas virtuales o físicas de infraestructura y otros recursos utilizados por Kubernetes para ejecutar los contenedores. 

[**Node**](https://github.com/kubernetes/kubernetes/blob/master/docs/admin/node.md)
Un nodo es un equipo físico o virtual con Kubernetes, en la que las pods pueden ejecutarse.

[**Pod**](https://github.com/kubernetes/kubernetes/blob/master/docs/user-guide/pods.md)
Los pods son un grupo contenedores de aplicaciones con volúmenes compartidos. Son las unidades de despliegue más pequeñas que se pueden crear, programadas y gestionadas con Kubernetes. Los pods se pueden crear de forma individual, pero se recomienda que utilice un controlador de replica incluso si la creación es de un sola pod.

[**Replication controller**](docs/user-guide/replication-controller.md)
Los controladores de replicación gestionar el ciclo de vida de los pods. Se aseguran de que un determinado número de pods están ejecutando en cualquier momento dado, creando o matando los pods que se definan.

[**Service**](https://github.com/kubernetes/kubernetes/blob/master/docs/user-guide/services.md)
Los servicios proporcionan un unico, nombre estable y dirección para un conjunto de pods.
Ellos actúan como balanceadores de carga entre los pods del servicio.

[**Label**](https://github.com/kubernetes/kubernetes/blob/master/docs/user-guide/labels.md)
Las etiquetas se utilizan para organizar y seleccionar grupos de objetos en función de clave: valor.

-------------------------------

Enlaces de interes
------------------

* http://www.aventurabinaria.es/external-load-balancer-haproxy-kubernetes/
* http://www.aventurabinaria.es/asociar-vip-a-ip-flotante-openstack/
* http://www.aventurabinaria.es/anadir-volumen-una-instancia-openstack/
* http://www.aventurabinaria.es/cluster-galera-on-debian-8/
* http://www.aventurabinaria.es/kubernetes-desplegado-centos/
* http://kubernetes.io/docs/user-guide/debugging-pods-and-replication-controllers/
* http://docs.openstack.org/developer/magnum/
* http://docs.openstack.org/developer/magnum/dev/dev-kubernetes-load-balancer.html

Openstack y Kubernetes

* http://www.tcpcloud.eu/en/blog/2016/02/12/kubernetes-and-openstack-multi-cloud-networking/
* http://blog.kubernetes.io/2016/04/introducing-kubernetes-openstack-sig.html
* https://www.mirantis.com/blog/magnum-vs-murano-openstack-container-strategy/

Autoescalado

* https://github.com/metral/corekube/blob/master/corekube-openstack.yaml
* http://superuser.openstack.org/articles/simple-auto-scaling-environment-with-heat/
* https://keithtenzer.com/2015/10/05/auto-scaling-applications-with-openstack-heat/

-------------------------------

<div id="control"> 
 <ul>
  <li style="float:right"><a class="next" href="2-Kube_simple.md">Siguiente</a></li>
</ul>
</div>