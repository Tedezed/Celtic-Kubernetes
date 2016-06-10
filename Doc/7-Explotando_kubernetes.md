<div id="header"> 
 <ul>
  <li><a class="active" href="1-Portada.md">Home</a></li>
  <li><a class="bar" href="https://github.com/Tedezed/Celtic-Kubernetes">Github</a></li>
  <li style="float:bottom"><a class="bar" href="Contacto.md">Contacto</a></li>
</ul>
</div>
<div id="control"> 
 <ul>
  <li><a class="next" href="6-Almacenamiento.md">Anterior</a></li>
  <li style="float:right"><a class="next" href="8-Kubernetes_ansible.md">Siguiente</a></li>
</ul>
</div>

Explotando Kubernetes
=====================

Indice de contenidos
--------------------

* [MySQL dentro de Kubernetes](#kube-mysql)
* [Galera Cluster dentro de Kubernetes](#kgalera)
* [Desplegando Wordpres con Galera](#kgalera-wordpress)

<div id='kube-mysql'/>

#### Kubernetes y MySQL

Si tienes cualquier error relacionado con el pod 

* [Fuente GitHub Kubernetes](https://github.com/kubernetes/kubernetes/issues/12746)

**ERROR**

`kubectl logs mysql --previous`
	
	chown: cannot read directory '/var/lib/mysql/': Permission denied

**SOLUCION**

	securityContext:
      capabilities: {}
      privileged: true #privileged required for mount

**MySQL como pod con pvc**

`kubectl create -f mysql-pod-pvc.yaml`

	apiVersion: v1
	kind: Pod
	metadata:
	  name: mysql
	  labels:
	    name: mysql
	spec:
	  containers:
	    - image: mysql:5.6
	      name: mysql
	      args:
	        - "--ignore-db-dir"
	        - "lost+found"
	      env:
	        - name: MYSQL_ROOT_PASSWORD
	          value: root
	      securityContext:
	        capabilities: {}
	        privileged: true #privileged required for mount
	      ports:
	        - containerPort: 3306
	          name: mysql
	      volumeMounts:
	        - name: mysql-persistent-storage
	          mountPath: /var/lib/mysql
	  volumes:
	    - name: mysql-persistent-storage
	      persistentVolumeClaim:
	       claimName: myclaim1-db


**MySQL como RC**

De forma basica

`kubectl create -f mysql-rc.yaml`

	apiVersion: v1
	kind: ReplicationController
	metadata:
	  name: mysql-controller
	spec:
	  replicas: 1
	  template:
	    metadata:
	      labels:
	        name: mysql
	    spec:
	      containers:
	        - image: mysql
	          name: mysql
	          ports:
	            - containerPort: 3306
	          env:
	            - name: MYSQL_ROOT_PASSWORD
	              value: root

Con almacenamiento persistente

`kubectl create -f mysql-rc-pvc.yaml`

	apiVersion: v1
	kind: ReplicationController
	metadata:
	  name: mysql-controller
	spec:
	  replicas: 1
	  template:
	    metadata:
	      labels:
	        name: mysql
	    spec:
	      containers:
	        - image: mysql:5.6
	          name: mysql
	          args:
	            - "--ignore-db-dir"
	            - "lost+found"
	          ports:
	            - containerPort: 3306
	              name: mysql
	          env:
	            - name: MYSQL_ROOT_PASSWORD
	              value: root
	          securityContext:
	            capabilities: {}
	            privileged: true #privileged required for mount
	          volumeMounts:
	          - name: mysql-persistent-storage
	            mountPath: /var/lib/mysql
	      volumes:
	      - name: mysql-persistent-storage
	        persistentVolumeClaim:
	          claimName: myclaim-1-db

Servicio para MySQL

	apiVersion: v1
	kind: Service
	metadata:
	  name: mysql
	  labels:
	    node: mysql
	spec:
	  ports:
	    - port: 3306
	      name: mysql-port
	  selector:
	    node: mysql



<div id='kgalera'/>

#### Cluster Galera dentro de Kubernetes

* [Planet MySQL](http://planet.mysql.com/entry/?id=5989823)
* [Github Kubernetes](https://github.com/kubernetes/kubernetes/tree/master/examples/mysql-galera)
* [Mas información](http://patg.net/galera,percona,kubernetes,coreos,docker,vmware/2015/04/21/galera-cluster-kubernetes/)

En un principio realice una instalación de un cluster Galera en tres nodos en el exterior del cluster de Kubernetes, en el cual los pods guardaban sus bases de datos mediante un ClusterIP auto-balanceado. 

Después de esto pense que simplificaría él escenario insertando el cluster Galaera en el interior de Kubernetes. Cada nodo es un rc con un servicio con su nombre, el cluster da servicio de forma interna a las aplicaciones web.

Desplegamos el escenario de la siguiente forma

En primer lugar especificar que la configuración de usuarios, contraseñas de mysql se realiza en los ficheros yaml de cada nodo, tiene que ser coherente para que funcione. Si quieres cambiar el contraseña de root, por ejemplo, tienes que cambiarla en los tres ficheros yaml de los pxc-nodes.

Ejemplo

	- name: GALERA_CLUSTER
	  value: "true"
	- name: WSREP_CLUSTER_ADDRESS
	  value: gcomm://
	- name: WSREP_SST_USER
	  value: sst
	- name: WSREP_SST_PASSWORD
	  value: sst
	- name: MYSQL_USER
	  value: mysql
	- name: MYSQL_PASSWORD
	  value: mysql
	- name: MYSQL_ROOT_PASSWORD
	  value: c-krit

Creamos el servicio para el cluster galera

	kubectl create -f pxc-cluster-service.yaml

Creamos pxc-node1 y verificamos que este Rinning y sin Restarts que puedan indicar algun tipo de error.

	kubectl create -f pxc-node1.yaml

En cuanto este Running pxc-node1 creamos los dos nodos restantes

	kubectl create -f pxc-node2.yaml
	kubectl create -f pxc-node3.yaml

Consultamos el estado

	NAME                     READY     STATUS        RESTARTS   AGE
	nginx-controller-1jpzv   1/1	   Running	 0          23h
	nginx-controller-x77a3   1/1	   Running	 0          6m
	pxc-node1-lah1g          1/1	   Running	 0          3m
	pxc-node2-ru7op          1/1	   Running	 0          2m
	pxc-node3-ugt8o          1/1	   Running	 0          2m


**ERROR**

	2016-05-05 06:35:09 1 [Note] WSREP: Service thread queue flushed.
	2016-05-05 06:35:09 1 [Note] WSREP: Assign initial position for certification: -1, protocol version: -1
	2016-05-05 06:35:09 1 [Note] WSREP: wsrep_sst_grab()
	2016-05-05 06:35:09 1 [Note] WSREP: Start replication
	2016-05-05 06:35:09 1 [Note] WSREP: Setting initial position to 00000000-0000-0000-0000-000000000000:-1
	2016-05-05 06:35:09 1 [Note] WSREP: protonet asio version 0
	2016-05-05 06:35:09 1 [Note] WSREP: Using CRC-32C for message checksums.
	2016-05-05 06:35:09 1 [Note] WSREP: backend: asio
	2016-05-05 06:35:09 1 [Warning] WSREP: access file(/var/lib/mysql//gvwstate.dat) failed(No such file or directory)
	2016-05-05 06:35:09 1 [Note] WSREP: restore pc from disk failed
	2016-05-05 06:35:09 1 [Note] WSREP: GMCast version 0
	2016-05-05 06:35:09 1 [Warning] WSREP: Failed to resolve tcp://pxc-node1:4567
	2016-05-05 06:35:09 1 [Note] WSREP: (835a058a, 'tcp://0.0.0.0:4567') listening at tcp://0.0.0.0:4567
	2016-05-05 06:35:09 1 [Note] WSREP: (835a058a, 'tcp://0.0.0.0:4567') multicast: , ttl: 1
	2016-05-05 06:35:09 1 [Note] WSREP: EVS version 0
	2016-05-05 06:35:09 1 [Note] WSREP: gcomm: connecting to group 'galera_kubernetes', peer 'pxc-node1:'
	2016-05-05 06:35:09 1 [ERROR] WSREP: failed to open gcomm backend connection: 131: No address to connect (FATAL)
		 at gcomm/src/gmcast.cpp:connect_precheck():282
	2016-05-05 06:35:09 1 [ERROR] WSREP: gcs/src/gcs_core.cpp:long int gcs_core_open(gcs_core_t*, const char*, const char*, bool)():206: Failed to open backend connection: -131 (State not recoverable)
	2016-05-05 06:35:09 1 [ERROR] WSREP: gcs/src/gcs.cpp:long int gcs_open(gcs_conn_t*, const char*, const char*, bool)():1379: Failed to open channel 'galera_kubernetes' at 'gcomm://pxc-node1': -131 (State not recoverable)
	2016-05-05 06:35:09 1 [ERROR] WSREP: gcs connect failed: State not recoverable
	2016-05-05 06:35:09 1 [ERROR] WSREP: wsrep::connect(gcomm://pxc-node1) failed: 7
	2016-05-05 06:35:09 1 [ERROR] Aborting
	2016-05-05 06:35:09 1 [Note] WSREP: Service disconnected.
	2016-05-05 06:35:10 1 [Note] WSREP: Some threads may fail to exit.
	2016-05-05 06:35:10 1 [Note] Binlog end
	2016-05-05 06:35:10 1 [Note] mysqld: Shutdown complete

**SOLUCION**

Esto es problema de kube2sky, que bien, no funciona correctamente o no esta instalado, mas información:

* [kube2sky](https://github.com/kubernetes/kubernetes/tree/master/cluster/addons/dns)

Podemos probar si funciona la resolucion de nombres de servicios con 

`kubectl exec busybox -- nslookup pxc-node1`


#### Galera Cluster con almacenamiento persistente

En primer lugar creamos un volumen persistente para Galera
`kubectl create -f glusterfs-galera.yaml`

	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  name: pv-5g-galera
	spec:
	  capacity:
	    storage: 5Gi
	  accessModes:
	    - ReadWriteMany
	  glusterfs:
	    path: dist-volume
	    endpoints: glusterfs-cluster
	    readOnly: false
	  persistentVolumeReclaimPolicy: Recycle

Creamos una reserva de ejemplo de 2Gi

`kubectl create -f claim-galera.yaml`

	kind: PersistentVolumeClaim
	apiVersion: v1
	metadata:
	  name: claim-galera
	spec:
	  accessModes:
	    - ReadWriteMany
	  resources:
	    requests:
	      storage: 4Gi

Por ultimo tendremos que crear el servicio de nuestro galera y los nodos del mismo. Como termine haciéndolo muchas veces para los test, termine haciendo un script, con la ventaja que si cambias el rango del por puedes crear cuantos nodos quieras.

Plantilla a utilizar: `galera-cluster-nodes.yaml`

	apiVersion: v1
	kind: Service
	metadata:
	  name: {{node}}
	  labels:
	    node: {{node}}
	spec:
	  ports:
	    - port: 3306
	      name: mysql
	    - port: 4444
	      name: state-snapshot-transfer
	    - port: 4567
	      name: replication-traffic 
	    - port: 4568
	      name: incremental-state-transfer 
	  selector:
	    node: {{node}} 
	---
	apiVersion: v1
	kind: ReplicationController
	metadata:
	  name: {{node}} 
	spec:
	  replicas: 1
	  template:
	    metadata:
	      labels:
	        node: {{node}} 
	        unit: pxc-cluster
	    spec:
	      containers:
	        - resources:
	            limits: 
	              cpu: 0.3
	          image: capttofu/percona_xtradb_cluster_5_6:beta
	          name: {{node}}
	          ports:
	            - containerPort: 3306
	            - containerPort: 4444
	            - containerPort: 4567
	            - containerPort: 4568
	          env:
	            - name: GALERA_CLUSTER
	              value: "true"
	            - name: WSREP_CLUSTER_ADDRESS
	              value: gcomm://
	            - name: WSREP_SST_USER
	              value: sst
	            - name: WSREP_SST_PASSWORD
	              value: sst
	            - name: MYSQL_USER
	              value: mysql
	            - name: MYSQL_PASSWORD
	              value: {{pass_mysql}}
	            - name: MYSQL_ROOT_PASSWORD
	              value: {{pass_root}}
	          securityContext:
	            capabilities: {}
	            privileged: true #privileged required for mount
	          volumeMounts:
	          - name: mysql-persistent-storage
	            mountPath: /var/lib/mysql
	      volumes:
	      - name: mysql-persistent-storage
	        persistentVolumeClaim:
	          claimName: {{claim}}

`nano create_nodes.sh`

	# By Tedezed
	kubectl create -f pxc-cluster-service.yaml; \
	var_pass_mysql="mysql"; \
	var_pass_root="root"; \
	var_claim="claim-galera"; \
	\
	for i in {1..3}; \
	do \
		sed -e "s/{{node}}/pxc-node"$i"/g" \
		-e "s/{{pass_mysql}}/"$var_pass_mysql"/g" \
		-e "s/{{pass_root}}/"$var_pass_root"/g" \
		-e "s/{{claim}}/"$var_claim"/g" \
		galera-cluster-nodes.yaml > bridge_file;
		kubectl create -f bridge_file
	done; \
	rm -rf bridge_file; \
	unset var_pass_root; unset var_pass_mysql; unset var_claim

Lo ejecutamos con `sh create_nodes.sh`, si copias y pegas el codigo también funcionara.
*Nota; si los nodos no terminan de crearse puede que tengas que revisar los endpoint de GlusterFS.*

Comprobamos el estado de los nodos y como podemos ver estan totalmente operativos

	[root@morrigan galera-pvc]# kubectl get pods | grep pxc
	pxc-node1-5hwwi          1/1       Running   0          1m
	pxc-node2-iiss3          1/1       Running   0          1m
	pxc-node3-uo0is          1/1       Running   0          1m


---------------------------------

<div id="control"> 
 <ul>
  <li><a class="next" href="6-Almacenamiento.md">Anterior</a></li>
  <li style="float:right"><a class="next" href="8-Kubernetes_ansible.md">Siguiente</a></li>
</ul>
</div>
