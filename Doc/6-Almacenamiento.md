[Index](1-Portada.md) - [Anterior](5-Exponer_svc.md) | [Siguiente](7-Explotando_kubernetes.md)

---------------------------------

Almacenamiento para Kubernetes
==============================

* [Fuente severalnines](http://severalnines.com/blog/wordpress-application-clustering-using-kubernetes-haproxy-and-keepalived)

Para dar almacenamiento persistente a Kubernetes podemos utilizar dos tecnologías; NFS y GlusterFS. Para cualquiera de ellas en Kubernetes tendremos que crear:

* PersistentVolume -- Donde especificamos el volumen persistente
* PersistentVolumeClaim -- Donde reclamamos espacio en el volumen

Modos de acceso:

* ReadWriteOnce -- read-write solo para un nodo (RWO)
* ReadOnlyMany -- ead-only para muchos nodos (ROX)
* ReadWriteMany -- read-write para muchos nodos (RWX)

Servidor NFS Angus
------------------

En el servidor Angus, procedemos a montar el almacenamiento

	yum install nfs-utils

El directorio que compartiremos sera `/shared/kubernetes`

Creamos dos directorios dentro para el almacenamiento de los sitios web y para las bases de datos

	mkdir -p /shared/kubernetes/www
	mkdir -p /shared/kubernetes/db

Añadimos la siguiente linea para dar acceso a la red privada de OpenStack del resto de maquinas

`/etc/exports`

	/shared 10.0.0.0/24(rw,sync,no_root_squash,no_all_squash)

Habilitamos y arrancamos las siguientes unidades para dar el servicio de NFS

	systemctl enable rpcbind; systemctl enable nfs-server; systemctl restart rpcbind; systemctl restart nfs-server


#### Clientes NFS Artio y Esus

Instamalos el cliente NFS en los minions
	
	yum install nfs-utils

Comprobamos que la configuración anterior en Angus funciona

	[root@artio centos]# showmount -e 10.0.0.52
	Export list for 10.0.0.52:
	/shared 10.0.0.0/24

Podemos montarlo con

	mount -t nfs4 10.0.0.52:/shared /tu_directorio

#### Creando almacenamiento persistente con NFS

En uno de los nodos master del cluster de Kubernetes creamos el siguientes ficheros

Creamos el volumen persistente para los sitios web
`kubectl create -f nfs-www.yaml`

	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  name: pv-5g-www
	spec:
	  capacity:
	    storage: 5Gi
	  accessModes:
	    - ReadWriteMany
	  persistentVolumeReclaimPolicy: Recycle
	  nfs:
	    path: /shared/kubernetes/www
	    server: 10.0.0.52

Creamos el volumen persistente para la base de datos
`kubectl create -f nfs-db.yaml`

	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  name: pv-5g-db
	spec:
	  capacity:
	    storage: 5Gi
	  accessModes:
	    - ReadWriteMany
	  persistentVolumeReclaimPolicy: Recycle
	  nfs:
	    path: /shared/kubernetes/db
	    server: 10.0.0.52

* Si queremos borrarlo solo tendremos que ejecutar `kubectl delete pv pv-5g-www`

Podemos ver el estado con

	[root@morrigan config-kubernetes]# kubectl get pv
	NAME        LABELS    CAPACITY   ACCESSMODES   STATUS      CLAIM     REASON    AGE
	pv-3g-www   <none>    3Gi        RWX           Available                       1m
	pv-5g-db    <none>    5Gi        RWX           Available                       1m


#### Reclamando almacenamiento

En uno de los nodos master del cluster de Kubernetes realizamos claim de 1Gi para nuestro servicio web

`kubectl create -f claim1-www.yaml`

	kind: PersistentVolumeClaim
	apiVersion: v1
	metadata:
	  name: myclaim1-www
	spec:
	  accessModes:
	    - ReadWriteMany
	  resources:
	    requests:
	      storage: 1Gi

Tambien creamos una reclamación de alamacenamiento para db

`kubectl create -f claim1-db.yaml`

	kind: PersistentVolumeClaim
	apiVersion: v1
	metadata:
	  name: myclaim1-db
	spec:
	  accessModes:
	    - ReadWriteMany
	  resources:
	    requests:
	      storage: 2Gi

Podemos consultar el estado de la siguiente forma

	[root@morrigan config-kubernetes]# kubectl get pv,pvc
	NAME           LABELS    CAPACITY   ACCESSMODES   STATUS     CLAIM                  REASON    AGE
	pv-5g-db       <none>    5Gi        RWX           Bound      default/myclaim1-db              12m
	pv-5g-www      <none>    5Gi        RWX           Bound      default/myclaim1-www             5m
	NAME           LABELS    STATUS     VOLUME        CAPACITY   ACCESSMODES            AGE
	myclaim1-db    <none>    Bound      pv-5g-db      5Gi        RWX                    20s
	myclaim1-www   <none>    Bound      pv-5g-www     5Gi        RWX                    3m

<div id='glusterfs'/>

GlusterFS en Angus y Dagda
--------------------------

Una vez funcionando NFS tendremos un unico punto de fallo, para solucionar esto montaremos GlusterFS para proporcionar HA.

* [Fuente CentOS WIKI](https://wiki.centos.org/SpecialInterestGroup/Storage/gluster-Quickstart)
* [Fuente unixmen](http://www.unixmen.com/install-glusterfs-server-client-centos-7/)
* [Fuente digitalocean](https://www.digitalocean.com/community/tutorials/how-to-create-a-redundant-storage-pool-using-glusterfs-on-ubuntu-servers)

Eliminamos el servicio NFS y todos sus ficheros para tener un escenario limpio

	yum remove nfs-utils

Añadimos los siguientes repositorios

	yum install epel-release centos-release-gluster

Instalamos GLusterFS en Angus y Dagna

	yum -y install glusterfs glusterfs-fuse glusterfs-server

En mi caso, asosiare un volumen de 10G a cada una de las maquinas virtuales

Listamos los volumenes

`lsblk`

	NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
	vda    253:0    0   8G  0 disk 
	└─vda1 253:1    0   8G  0 part /
	vdb    253:16   0  10G  0 disk 

Damos formato

	mkfs.xfs /dev/vdb

Creamos el directorio donde montaremos el volumen

	mkdir -p /bricks/brick1

Montamos el volumen y le damos formato:

	mount /dev/vdb /bricks/brick1

Comprobamos el estadpo del volumen

`df -h`

	S.ficheros     Tamaño Usados  Disp Uso% Montado en
	/dev/vda1        8,0G   1,5G  6,6G  19% /
	devtmpfs         227M      0  227M   0% /dev
	tmpfs            245M      0  245M   0% /dev/shm
	tmpfs            245M   8,3M  237M   4% /run
	tmpfs            245M      0  245M   0% /sys/fs/cgroup
	tmpfs             49M      0   49M   0% /run/user/1000
	/dev/vdb          10G    33M   10G   1% /bricks/brick1

Por ultimo ara que se monte automáticamente lo añadimos a /etc/fstab

`nano /etc/fstab`

	/dev/vdb 	/bricks/brick1 	xfs 	defaults 	1 	2

Arrancamos y habilitamos GlusterFS

	systemctl start glusterd.service; systemctl enable glusterd.service

Añadimos Angus y Dagda

* Angus

		[root@angus centos]# gluster peer probe dagda
		peer probe: success. 
		[root@angus centos]# gluster peer status
		Number of Peers: 1

		Hostname: dagda
		Uuid: 3fd499e0-75c7-4552-b8c0-5b77851288d3
		State: Peer in Cluster (Connected)
		[root@angus centos]# 

* Dagda

		[root@dagda centos]# gluster peer probe angus
		peer probe: success. Host angus port 24007 already in peer list
		[root@dagda centos]# gluster peer status
		Number of Peers: 1

		Hostname: angus
		Uuid: 27cbd79a-e8fa-4102-a6e3-d7e5e3d770d9
		State: Peer in Cluster (Connected)

Vemos el estado de pool

	[root@angus centos]# gluster pool list
	UUID					Hostname 	State
	3fd499e0-75c7-4552-b8c0-5b77851288d3	dagda    	Connected 
	27cbd79a-e8fa-4102-a6e3-d7e5e3d770d9	localhost	Connected

	[root@angus centos]# gluster volume status
	No volumes present

Creamos el voluen distribuido

	gluster volume create dist-volume angus:/bricks/brick1 dagda:/bricks/brick1 force

	gluster volume create dist-volume replica 2 angus:/bricks/brick1 dagda:/bricks/brick1 force
	
Iniciamos el voluemn distribuido

	gluster volume start dist-volume

Con esto ya tendremos nuestro servidor listo, podemos ver la información de los volúmenes

	[root@angus centos]# gluster volume info
	Volume Name: dist-volume
	Type: Distribute
	Volume ID: a271e529-023a-4be8-89be-e17108979b2c
	Status: Started
	Number of Bricks: 2
	Transport-type: tcp
	Bricks:
	Brick1: angus:/bricks/brick1
	Brick2: dagda:/bricks/brick1
	Options Reconfigured:
	performance.readdir-ahead: on

	[root@angus centos]# gluster volume status
	Status of volume: dist-volume
	Gluster process                             TCP Port  RDMA Port  Online  Pid
	------------------------------------------------------------------------------
	Brick angus:/bricks/brick1                  49152     0          Y       9409 
	Brick dagda:/bricks/brick1                  49152     0          Y       9218 
	NFS Server on localhost                     2049      0          Y       9429 
	NFS Server on dagda                         2049      0          Y       9238 
	 
	Task Status of Volume dist-volume
	------------------------------------------------------------------------------
	There are no active volume tasks


#### Clientes de GlusterFS (Artio y Eusus)

El primer paso es añadir los siguientes epositorios

	yum install epel-release centos-release-gluster

Instalamos el siguiente software

	yum -y install glusterfs glusterfs-fuse

Creamos el directorio donde añadiremos el volumen distribuido

	mkdir  /mnt/gluster-v-dist

Montamos el volumen distribuido

	mount.glusterfs  angus:/dist-volume   /mnt/gluster-v-dist/

Podemos ver el resultado con

	[root@artio centos]# df  -h 
	S.ficheros         Tamaño Usados  Disp Uso% Montado en
	/dev/vda1             20G    13G  8,0G  61% /
	devtmpfs             902M      0  902M   0% /dev
	tmpfs                920M      0  920M   0% /dev/shm
	tmpfs                920M    17M  904M   2% /run
	tmpfs                920M      0  920M   0% /sys/fs/cgroup
	tmpfs                920M   4,0K  920M   1% /var/lib/kubelet/pods/8fe$
	tmpfs                184M      0  184M   0% /run/user/1000
	tmpfs                184M      0  184M   0% /run/user/0
	angus:/dist-volume    20G    65M   20G   1% /mnt/gluster-v-dist

Para que se monte automáticamente añadimos la sigueinte linea a `/etc/fstab`

	angus:/dist-volume   /mnt/gluster-v-dist  glusterfs defaults,_netdev 0 0


#### Test de funcionamiento de GlusterFS

Creamos dos ficheros de ejemplo en Artio

	touch /mnt/gluster-v-dist/file1
	touch /mnt/gluster-v-dist/file2

Paramos Angus

	halt

Borramos un fichero en Artio

	rm -rf /mnt/gluster-v-dist/file2

Listamos el directorio en Esus

	[root@esus centos]# ls /mnt/gluster-v-dist
	file1

Como podemos ver el cambio esta sincronizado gracias a Dagda ya que Angus esta parado.



#### Creando almacenamiento persistente con GlusterFS

En uno de los nodos master del cluster de Kubernetes creamos los siguientes ficheros

Lo primero que tenemos que hacer es crear un endpoint de nuestro nodos de GlusterFS con el puerto que queramos dentro del rango que acepta Kubernetes y sin namespace.

`kubectl create -f glusterfs-endpoint.yaml`

	kind: Endpoints
	apiVersion: v1
	metadata: 
	  labels:
	    name: glusterfs-cluster
	  name: glusterfs-cluster
	subsets: 
	  - addresses: 
	      - ip: 10.0.0.52
	    ports:
	      - port: 1
	  - addresses:   
	      - ip: 10.0.0.50
	    ports:
	      - port: 1

Este endpoint puede dar problemas de persistencia
* [Endpoints are not persistented #12964](https://github.com/kubernetes/kubernetes/issues/12964)
* [Glusterfs volumes are unstable #13511](https://github.com/kubernetes/kubernetes/issues/13511)

Para consegir tener nuestro endpoint persistente creamos el siguiente pod

	{
	    "apiVersion": "v1",
	    "kind": "Pod",
	    "metadata": {
	        "name": "glusterfs"
	    },
	    "spec": {
	        "containers": [
	            {
	                "name": "glusterfs",
	                "image": "kubernetes/pause",
	                "volumeMounts": [
	                    {
	                        "mountPath": "/mnt/glusterfs-v-dist",
	                        "name": "glusterfsvol"
	                    }
	                ]
	            }
	        ],
	        "volumes": [
	            {
	                "name": "glusterfsvol",
	                "glusterfs": {
	                    "endpoints": "glusterfs-cluster",
	                    "path": "dist-volume",
	                    "readOnly": true
	                }
	            }
	        ]
	    }
	}

Podemos ver el estado de los endpoint con

	[root@morrigan config-kubernetes]# kubectl get endpoints | grep glusterfs-cluster
	glusterfs-cluster   10.0.0.50:1,10.0.0.52:1       38s


Creamos un servicio para el endpoint anterior

`kubectl create -f glusterfs-service.yaml`

	apiVersion: "v1"
	kind: "Service"
	metadata:
	  labels:
	    name: glusterfs-cluster
	  name: "glusterfs-cluster"
	spec:
	  ports:
	  - port: 1

Con esto tendremos nuestro endpoint persistente

Creamos el volumen persistente de ejemplo para una base de datos
`kubectl create -f glusterfs-db.yaml`

	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  name: pv-5g-db-1
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

`kubectl create -f claim-1-db.yaml`

	kind: PersistentVolumeClaim
	apiVersion: v1
	metadata:
	  name: myclaim-1-db
	spec:
	  accessModes:
	    - ReadWriteMany
	  resources:
	    requests:
	      storage: 2Gi


-----------------------------------

[Anterior](5-Exponer_svc.md) | [Siguiente](7-Explotando_kubernetes.md)