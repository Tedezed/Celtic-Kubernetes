<div id="header"> 
 <ul>
  <li><a class="active" href="1-Portada.md">Home</a></li>
  <li><a class="bar" href="https://github.com/Tedezed/Celtic-Kubernetes">Github</a></li>
  <li style="float:bottom"><a class="bar" href="Contacto.md">Contacto</a></li>
</ul>
</div>
<div id="control"> 
 <ul>
  <li><a class="next" href="4-Addons.md">Anterior</a></li>
  <li style="float:right"><a class="next" href="6-Almacenamiento.md">Siguiente</a></li>
</ul>
</div>


Exponer servicios
=================

Exponer servicions con HAProxy
------------------------------

* [Fuente Github](https://github.com/kubernetes/contrib/tree/master/service-loadbalancer)
* [Modo 1. por puerto](http://www.dasblinkenlichten.com/kubernetes-101-external-access-into-the-cluster/)
* [Modo 2. por IP](http://severalnines.com/blog/wordpress-application-clustering-using-kubernetes-haproxy-and-keepalived)
* [Exponer con OpenStack](http://docs.openstack.org/developer/magnum/dev/dev-kubernetes-load-balancer.html)

Creamos un rc para nginx, este es el que utilizaremos de ejemplo

`kubectl create -f nginx.yaml`

	apiVersion: v1
	kind: ReplicationController
	metadata:
	 name: nginx-controller
	spec:
	 replicas: 2
	 selector:
	   name: nginx
	 template:
	   metadata:
	     labels:
	       name: nginx
	   spec:
	     containers:
	       - name: nginx
	         image: nginx
	         ports:
	           - containerPort: 80


El siguiente paso, es crear un servicio para nuestro rc de nginx

`kubectl create -f nginx-service.yaml`

	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-service
	  labels:
	    app: nginx
	spec:
	  type: NodePort
	  ports:
	  - port: 80
	    protocol: TCP
	    name: http
	  selector:
	    name: nginx

Cuando lo creamos nos especificara el puerto de la siguiente forma

	You have exposed your service on an external port on all nodes in your
	cluster.  If you want to expose this service to the external internet, you may
	need to set up firewall rules for the service port(s) (tcp:30630) to serve traffic.

Ya podremos acceder con la IPs de los minions y el puerto anterior
	
	http://172.22.205.242:30630/
	http://172.22.205.243:30630/

Creamos servicios para realizar un breve test, apuntando a nginx para prueba, un segundo servicio con un nuevo puerto y el tercero con cluster IP.

`kubectl create -f nginx-service2.yaml`

	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-service2
	  labels:
	    app: nginx
	spec:
	  type: NodePort
	  ports:
	  - port: 80
	    protocol: TCP
	    name: http
	  selector:
	    name: nginx

	You have exposed your service on an external port on all nodes in your
	cluster.  If you want to expose this service to the external internet, you may
	need to set up firewall rules for the service port(s) (tcp:30357) to serve traffic.

`kubectl create -f nginx-service3.yaml`

	apiVersion: v1
	kind: Service
	metadata:
	  name: nginx-service3
	  labels:
	    app: nginx
	spec:
	  clusterIP: 10.254.10.10
	  ports:
	  - port: 80
	    protocol: TCP
	    name: http
	  selector:
	    name: nginx

Configuración de HAProxy externo (Tanaris)

En primer lugar copiamos la configuración por defecto

	cp /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.old

#### Configuración de HAProxy

`nano /etc/haproxy/haproxy.cfg`

	##--------------------------##
	# 	Configuracion HAproxy 	 #
	##--------------------------##
	global
	    log 127.0.0.1   local0
	    log 127.0.0.1   local1 notice
	    maxconn 4096
	    user haproxy
	    group haproxy
	    daemon

	defaults
	  mode http
	  log  global
	  option  redispatch
	  maxconn 65535
	  contimeout 5000
	  clitimeout 50000
	  srvtimeout 50000
	  retries  3
	  log 127.0.0.1 local3
	  timeout  http-request 6s
	  timeout  queue 6s
	  timeout  connect 5s
	  timeout  client 5s
	  timeout  server 5s
	  timeout  check 5s
	  option httpclose

	frontend all
	    bind *:80

	    # Definiendo hosts
	    acl host_nginx1 hdr(host) -i www.nginx1.example.kubernetes
	    acl host_nginx2 hdr(host) -i www.nginx2.example.kubernetes
	    acl url_nginx1 path_beg -i /nginx1
	    acl url_nginx2 path_beg -i /nginx2

	    # Punteros if a backend
	    use_backend nginx1_back if host_nginx1
	    use_backend nginx2_back if host_nginx2
	    use_backend nginx1_back if url_nginx1
	    use_backend nginx2_back if url_nginx2

	    # Por defecto para el puerto 80
	    default_backend nomatch

	backend nginx1_back
	    balance roundrobin
	    option forwardfor
	    option httpchk HEAD /index.html HTTP/1.0
	    server artio 172.22.205.242:30630 check
	    server esus 172.22.205.243:30630 check
	    
	backend nginx2_back
	    balance roundrobin
	    server artio 172.22.205.242:30357 check
	    server esus 172.22.205.243:30357 check

	backend nomatch
	    errorfile 503 /var/www/404.html

Reiniciamos la unidad
		
	systemctl restart haproxy

<div id='hap_manager'/>

HAProxy externo sincronizado con Kubernetes
-------------------------------------------

Partiendo de tener dos servidores configurados y funcionando con **external_loadbalancer_hap**

Seria recomendable instalar **NTP** en Belenus y Tanaris como en [despliegue de kubernetes en HA con PCS](3-Kube_HA_pcs.md#previo)

Instalación de pcs
	
	yum install pcs

[Configuración con PCS](3-Kube_HA_pcs.md#conf-pcs)

Configuramos el cluster (Belenus)

	pcs cluster setup --name PCS-HAP-Kubernetes belenus tanaris

Podemos ver el estado actual con

	[root@taranis external_loadbalancer_hap]# pcs status
	Cluster name: PCS-HAP-Kubernetes
	Last updated: Tue May 17 09:45:16 2016		Last change: Tue May 17 09:45:02 2016 by root via cibadmin on tanaris
	Stack: corosync
	Current DC: belenus (version 1.1.13-10.el7_2.2-44eb2dd) - partition with quorum
	2 nodes and 0 resources configured

	Online: [ belenus tanaris ]

	Full list of resources:


	PCSD Status:
	  belenus: Online
	  tanaris: Online

	Daemon Status:
	  corosync: active/enabled
	  pacemaker: active/enabled
	  pcsd: active/enabled

#### Configuración de recursos en PCS

###### Cluster IP con PCS para HAP

Añadimos un recurso cluster con la ip fija reservada a la vip.
		
	pcs resource create ClusterIP ocf:heartbeat:IPaddr2 \
     ip=10.0.0.38 cidr_netmask=24 op monitor interval=30s

Clonamos el recurso para que este en los dos nodos
    	
    	pcs resource clone ClusterIP \
     	 globally-unique=true clone-max=2 clone-node-max=2

Comprobamos el recurso

	[root@taranis external_loadbalancer_hap]# pcs resource show
	 Clone Set: ClusterIP-clone [ClusterIP] (unique)
	     ClusterIP:0	(ocf::heartbeat:IPaddr2):	Started belenus
	     ClusterIP:1	(ocf::heartbeat:IPaddr2):	Started tanaris


###### Cluster con recursos de los balanceadores

Creamos los siguientes recursos para que pcs controle los balanceadores

	pcs resource create HAProxy systemd:haproxy master-max=2 --group kubernetes-loadbalancer
	pcs resource create HAPManager systemd:hap_manager master-max=2 --group kubernetes-loadbalancer

Comprobamos el estado

	[root@taranis external_loadbalancer_hap]# pcs resource show
	 Clone Set: ClusterIP-clone [ClusterIP] (unique)
	     ClusterIP:0	(ocf::heartbeat:IPaddr2):	Started belenus
	     ClusterIP:1	(ocf::heartbeat:IPaddr2):	Started tanaris
	 Resource Group: kubernetes-loadbalancer
	     HAProxy	(systemd:haproxy):	Started belenus
	     HAPManager	(systemd:hap_manager):	Started belenus

Clonamos los recursos

		pcs resource clone kubernetes-loadbalancer

Resultado final

	[root@taranis external_loadbalancer_hap]# pcs resource show
	 Clone Set: ClusterIP-clone [ClusterIP] (unique)
	     ClusterIP:0	(ocf::heartbeat:IPaddr2):	Started belenus
	     ClusterIP:1	(ocf::heartbeat:IPaddr2):	Started tanaris
	 Clone Set: kubernetes-loadbalancer-clone [kubernetes-loadbalancer]
	     Started: [ belenus tanaris ]

Podemos ver que funciona desde una de las maquinas de OpenStack con

	curl 10.0.0.38:80/nginx-service/

#### Para poder acceder desde fuera tendremos que relizar una asociación con una IP flotante a la VIP

En primer lugar listamos las redes con neutron

	(cli-openstack)debian-user@debian:~/Descargas$ neutron net-list
	+--------------------------------------+--------------------------+--------------------------------------------------+
	| id                                   | name                     | subnets                                          |
	+--------------------------------------+--------------------------+--------------------------------------------------+
	| 9734556d-XXXX-XXXX-XXXX-fdad435fff18 | red de juanmanuel.torres | 56693ca1-XXXX-XXXX-XXXX-ee8074bb13b1 10.0.0.0/24 |
	| a86fc437-XXXX-XXXX-XXXX-f37a7b05537f | ext-net                  | 3c8cdfb0-XXXX-XXXX-XXXX-c6c3e228b81c             |
	+--------------------------------------+--------------------------+--------------------------------------------------+

Creamos un puerto para la ip de la subred que utilizaremos

`neutron port-create {net-id} --fixed-ip ip_address={ip}`

	neutron port-create 9734556d-XXXX-XXXX-XXXX-fdad435fff18 --fixed-ip ip_address=10.0.0.38

Podremos ver el resultado con

	(cli-openstack)debian-user@debian:~/Descargas$ neutron port-list | grep 10.0.0.38
	2821603c-POPP-POPP-POPP-bd2349b29e63 | | fa:16:3e:94:a9:bd | {"subnet_id":"56693ca1-XXXX-XXXX-XXXX-ee8074bb13b1","ip_address":"10.0.0.38"}

Para poder asociar la IP flotante necesitaremos su id, para ello podemos listar las existentes con

	(cli-openstack)debian-user@debian:~/Descargas$ neutron floatingip-list
	+--------------------------------------+------------------+---------------------+--------------------------------------+
	| id                                   | fixed_ip_address | floating_ip_address | port_id                              |
	+--------------------------------------+------------------+---------------------+--------------------------------------+
	| 03eeacd9-XXXX-XXXX-XXXX-71a1182ee838 |                  | 172.22.205.249      |                                      |
	| 0f36bd32-XXXX-XXXX-XXXX-e41867c5b8d4 | 10.0.0.50        | 172.22.205.246      | 0a10a744-XXXX-XXXX-XXXX-b8ecdcd8bac0 |
	| 1f8d124a-XXXX-XXXX-XXXX-101c148a348d | 10.0.0.44        | 172.22.205.241      | 8c306c2b-ZZZZ-ZZZZ-ZZZZ-b64bb5753e6f |
	| 2cc63597-XXXX-XXXX-XXXX-45e8e85034fa | 10.0.0.46        | 172.22.205.243      | 2f56c5a4-YYYY-YYYY-YYYY-541916af4b92 |
	| 61b53f55-XXXX-XXXX-XXXX-4ca9c90479d5 | 10.0.0.45        | 172.22.205.242      | 8b628bdc-VVVV-VVVV-VVVV-b1608f29624d |
	| 75619867-CCCC-CCCC-CCCC-2ac0907329ee | 10.0.0.48        | 172.22.205.244      | 469b1a30-XXXX-XXXX-XXXX-ba487da79e3f |
	| acd9ba03-RRRR-RRRR-RRRR-f535dcf0c769 | 10.0.0.43        | 172.22.205.240      | 40f6ad24-JJJJ-JJJJ-JJJJ-7be049772175 |
	| d6f96986-EEEE-EEEE-EEEE-563823df3216 |                  | 172.22.205.248      |                                      |
	| e4d55da9-WWWW-WWWW-WWWW-308d9b147b13 | 10.0.0.53        | 172.22.205.247      | 8da8d613-BBBB-BBBB-BBBB-96e89e31d8f5 |
	| ea9033b1-XXXX-XXXX-XXXX-6dc56a6b9cea | 10.0.0.52        | 172.22.205.245      | c219e492-NNNN-NNNN-NNNN-62ee771c5700 |
	+--------------------------------------+------------------+---------------------+--------------------------------------+

Finalmente la asociamos con

`neutron floatingip-associate --fixed-ip-address {ip} {float-ip-uuid} {port-uuid}`

	neutron floatingip-associate --fixed-ip-address 10.0.0.38 d6f96986-EEEE-EEEE-EEEE-563823df3216 2821603c-POPP-POPP-POPP-bd2349b29e63

	+--------------------------------------+------------------+---------------------+--------------------------------------+
	| id                                   | fixed_ip_address | floating_ip_address | port_id                              |
	+--------------------------------------+------------------+---------------------+--------------------------------------+
	| 03eeacd9-XXXX-XXXX-XXXX-71a1182ee838 |                  | 172.22.205.249      |                                      |
	| 0f36bd32-XXXX-XXXX-XXXX-e41867c5b8d4 | 10.0.0.50        | 172.22.205.246      | 0a10a744-XXXX-XXXX-XXXX-b8ecdcd8bac0 |
	| 1f8d124a-XXXX-XXXX-XXXX-101c148a348d | 10.0.0.44        | 172.22.205.241      | 8c306c2b-ZZZZ-ZZZZ-ZZZZ-b64bb5753e6f |
	| 2cc63597-XXXX-XXXX-XXXX-45e8e85034fa | 10.0.0.46        | 172.22.205.243      | 2f56c5a4-YYYY-YYYY-YYYY-541916af4b92 |
	| 61b53f55-XXXX-XXXX-XXXX-4ca9c90479d5 | 10.0.0.45        | 172.22.205.242      | 8b628bdc-VVVV-VVVV-VVVV-b1608f29624d |
	| 75619867-CCCC-CCCC-CCCC-2ac0907329ee | 10.0.0.48        | 172.22.205.244      | 469b1a30-XXXX-XXXX-XXXX-ba487da79e3f |
	| acd9ba03-RRRR-RRRR-RRRR-f535dcf0c769 | 10.0.0.43        | 172.22.205.240      | 40f6ad24-JJJJ-JJJJ-JJJJ-7be049772175 |
	| d6f96986-EEEE-EEEE-EEEE-563823df3216 | 10.0.0.38        | 172.22.205.248      | 2821603c-POPP-POPP-POPP-bd2349b29e63 |
	| e4d55da9-WWWW-WWWW-WWWW-308d9b147b13 | 10.0.0.53        | 172.22.205.247      | 8da8d613-BBBB-BBBB-BBBB-96e89e31d8f5 |
	| ea9033b1-XXXX-XXXX-XXXX-6dc56a6b9cea | 10.0.0.52        | 172.22.205.245      | c219e492-NNNN-NNNN-NNNN-62ee771c5700 |
	+--------------------------------------+------------------+---------------------+--------------------------------------+

Para terminar de desplegar configuramos los nodos con [GlusterFS](6-Almacenamiento.md#glusterfs)


Exponer servicios con Ingress
-----------------------------

[Fuente k-user-guide](http://kubernetes.io/docs/user-guide/ingress/#what-is-ingress)
[GitHub Ingress](https://github.com/kubernetes/contrib/tree/master/ingress)
[GitHub GCE](https://github.com/kubernetes/contrib/tree/master/ingress/controllers/gce)

`kubectl create -f rc.yaml --namespace=kube-system`

	You have exposed your service on an external port on all nodes in your
	cluster.  If you want to expose this service to the external internet, you may
	need to set up firewall rules for the service port(s) (tcp:31959) to serve traffic.

	See http://releases.k8s.io/HEAD/docs/user-guide/services-firewalls.md for more details.
	service "default-http-backend" created
	replicationcontroller "l7-lb-controller" created

Podemos ver el pod con

	kubectl get pods -o wide --all-namespaces


LoadBalancer HAProxy interno
----------------------------

[Fuente GitHub](https://github.com/kubernetes/contrib/tree/master/service-loadbalancer)
[CoreOS GitHub](https://github.com/coreos/bootkube/tree/9d019a6729601003f48294b71ee6d96dfc4d32ce/vendor/k8s.io/kubernetes/test/e2e/testing-manifests/serviceloadbalancer)
[Nginx-Plus](https://www.nginx.com/blog/load-balancing-kubernetes-services-nginx-plus/)

Creamos el balanceador de carga, este no se iniciara por que espera que definamos los nodos
	
`kubectl create -f ./rc.yaml`

	apiVersion: v1
	kind: ReplicationController
	metadata:
	  name: service-loadbalancer
	  labels:
	    app: service-loadbalancer
	    version: v1
	spec:
	  replicas: 1
	  selector:
	    app: service-loadbalancer
	    version: v1
	  template:
	    metadata:
	      labels:
	        app: service-loadbalancer
	        version: v1
	    spec:
	      nodeSelector:
	        role: loadbalancer
	      containers:
	      - image: gcr.io/google_containers/servicelb:0.4
	        imagePullPolicy: Always
	        livenessProbe:
	          httpGet:
	            path: /healthz
	            port: 8080
	            scheme: HTTP
	          initialDelaySeconds: 30
	          timeoutSeconds: 5
	        name: haproxy
	        ports:
	        # All http services
	        - containerPort: 80
	          hostPort: 80
	          protocol: TCP
	        # nginx https
	        - containerPort: 443
	          hostPort: 8080
	          protocol: TCP
	        # mysql
	        - containerPort: 3306
	          hostPort: 3306
	          protocol: TCP
	        # haproxy stats
	        - containerPort: 1936
	          hostPort: 1936
	          protocol: TCP
	        resources: {}
	        args:
	        - --tcp-services=mysql:3306,nginxsvc:80
	        - --server=10.0.0.39:8080


Definimos los nodos que usara como loadbalancer
	
	kubectl label node artio role=loadbalancer

Resultado 

	[root@morrigan centos]# kubectl get nodes
	NAME      LABELS                                           STATUS    AGE
	artio     kubernetes.io/hostname=artio,role=loadbalancer   Ready     2m

Podemos tener el siguiente error dentro del pod

	Failed to create client: open /var/run/secrets/kubernetes.io/serviceaccount/token: permission denied

Este problema lo causa SeLinux en los minions, podemos desactivarlo o realizar los siguiente

	chcon -Rt svirt_sandbox_file_t /var/lib/kubelet

Podemos ventrar en el pod desde el minion donde se ejecuta

	docker exec -i -t $(docker ps | grep gcr.io/google_containers/servicelb:0.4 | awk '{ print $1 }' | sed q) bash


------------------------------------

<div id="control"> 
 <ul>
  <li><a class="next" href="4-Addons.md">Anterior</a></li>
  <li style="float:right"><a class="next" href="6-Almacenamiento.md">Siguiente</a></li>
</ul>
</div>

