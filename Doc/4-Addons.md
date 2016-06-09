[Index](1-Portada.md) - [Anterior](3-Kube_HA_pcs.md) | [Siguiente](5-Exponer_svc.md)

---------------------------------

Addons de Kubernetes
====================

En primer lugar para ordenar los componentes de Kubernetes de los que no lo son creamos un espacio de nombres para el sistema

`kubectl create -f kube-system.yaml`

	kind: "Namespace"
	apiVersion: "v1"
	metadata: 
	    name: "kube-system"
	    labels: 
	      name: "kube-system"

<div id='SkyDNS'/>

DNS interno SkyDNS
------------------

* [Fuente Profitbricks](https://devops.profitbricks.com/tutorials/setup-skydns-on-a-kubernetes-cluster/)
* [Fuente Accelazh](http://accelazh.github.io/kubernetes/Play-With-Kubernetes-On-CentOS-7)
* [Repositorio](https://github.com/kubernetes/kubernetes/tree/master/cluster/addons/dns)

Nuestro dominio dentro de kubernetes: cluster.local

Creamos el servicio

`kubectl create -f skydns-svc.yaml`

	apiVersion: v1
	kind: Service
	metadata:
	  name: kube-dns
	  namespace: kube-system
	  labels:
	    k8s-app: kube-dns
	    kubernetes.io/cluster-service: "true"
	    kubernetes.io/name: "KubeDNS"
	spec:
	  selector:
	    k8s-app: kube-dns
	  clusterIP: 10.254.0.10
	  ports:
	  - name: dns
	    port: 53
	    protocol: UDP
	  - name: dns-tcp
	    port: 53
	    protocol: TCP

Aquí tendremos que cambiar *replicas*,*kube_master_url*,*domain* y *cmd=nslookup kubernetes.default.svc.TU_DOMINIO.local*

`kubectl create -f skydns-rc.yaml`

	apiVersion: v1
	kind: ReplicationController
	metadata:
	  name: kube-dns-v9
	  namespace: kube-system
	  labels:
	    k8s-app: kube-dns
	    version: v9
	    kubernetes.io/cluster-service: "true"
	spec:
	  replicas: 1
	  selector:
	    k8s-app: kube-dns
	    version: v9
	  template:
	    metadata:
	      labels:
	        k8s-app: kube-dns
	        version: v9
	        kubernetes.io/cluster-service: "true"
	    spec:
	      containers:
	      - name: etcd
	        image: gcr.io/google_containers/etcd:2.0.9
	        resources:
	          limits:
	            cpu: 100m
	            memory: 50Mi
	        command:
	        - /usr/local/bin/etcd
	       # - --privileged=true
	       # - -data-dir
	       # - /home/data/etcd
	        - -listen-client-urls
	        - http://127.0.0.1:2379,http://127.0.0.1:4001
	        - -advertise-client-urls
	        - http://127.0.0.1:2379,http://127.0.0.1:4001
	        - -initial-cluster-token
	        - skydns-etcd
	        volumeMounts:
	        - mountPath: /home/data/etcd
	          name: etcd-storage
	      - name: kube2sky
	        image: gcr.io/google_containers/kube2sky:1.11
	        resources:
	          limits:
	            cpu: 100m
	            memory: 50Mi
	        args:
	        # command = "/kube2sky"
	        - -domain=cluster.local
	        - -etcd-server=http://127.0.0.1:4001
	        - -kube_master_url=http://10.0.0.39:8080
	      - name: skydns
	        image: gcr.io/google_containers/skydns:2015-03-11-001
	        resources:
	          limits:
	            cpu: 100m
	            memory: 50Mi
	        args:
	        # command = "/skydns"
	        - -machines=http://127.0.0.1:2379
	        - -addr=0.0.0.0:53
	       # - -ns-rotate=false
	        - -domain=cluster.local
	        ports:
	        - containerPort: 53
	          name: dns
	          protocol: UDP
	        - containerPort: 53
	          name: dns-tcp
	          protocol: TCP
	        livenessProbe:
	          httpGet:
	            path: /healthz
	            port: 8080
	            scheme: HTTP
	          initialDelaySeconds: 30
	          timeoutSeconds: 5
	        readinessProbe:
	          httpGet:
	            path: /healthz
	            port: 8080
	            scheme: HTTP
	          initialDelaySeconds: 1
	          timeoutSeconds: 5
	      - name: healthz
	        image: gcr.io/google_containers/exechealthz:1.0
	        resources:
	          limits:
	            cpu: 10m
	            memory: 20Mi
	        args:
	        - -cmd=nslookup kubernetes.default.svc.cluster.local 127.0.0.1 >/dev/null
	        - -port=8080
	        ports:
	        - containerPort: 8080
	          protocol: TCP
	      volumes:
	      - name: etcd-storage
	        emptyDir: {}
	      dnsPolicy: Default  # Don't use cluster DNS.

Modificamos la siguiente linea en Artio y Esus

`nano /etc/kubernetes/kubelet`

	KUBELET_ARGS="--register-node=true --cluster_dns=10.254.0.10 --cluster_domain=cluster.local"

Reiniciamos kubelet

	systemctl daemon-reload; systemctl restart kubelet


Utilizando un pod de [busybox](#utiles) verificamos el funcionamiento del DNS

* Test 0

		[root@morrigan config-kubernetes]# kubectl get pods --namespace=kube-system
		NAME                READY     STATUS    RESTARTS   AGE
		kube-dns-v9-2yxfh   4/4       Running   0          54s


* Test 1

		[root@morrigan config-kubernetes]# kubectl exec busybox -- traceroute 10.0.0.39
		traceroute to 10.0.0.39 (10.0.0.39), 30 hops max, 46 byte packets
		 1  10.80.65.1 (10.80.65.1)  0.010 ms  0.006 ms  0.002 ms
		 2  10.0.0.39 (10.0.0.39)  1.170 ms  0.389 ms  0.345 ms


* Test 2

	`kubectl create -f busybox.yaml`

		apiVersion: v1
		kind: Pod
		metadata:
		  name: busybox
		spec:
		  containers:
		  - image: busybox
		    command:
		      - sleep
		      - "3600"
		    name: busybox

	`kubectl exec busybox -- nslookup kubernetes`
	
		Server:    10.254.0.10
		Address 1: 10.254.0.10

		Name:      kubernetes
		Address 1: 10.254.0.1


<div id='dashboard'/>

DashBoard
---------

[Fuente GitHub](https://github.com/kubernetes/kubernetes/tree/master/cluster/addons/dashboard)

Especificamos la IP de la API de nuestro cluster en apiserver-host

`kubectl create -f kubernetes/cluster/addons/dashboard/dashboard-controller.yaml`

	apiVersion: v1
	kind: ReplicationController
	metadata:
	  # Keep the name in sync with image version and
	  # gce/coreos/kube-manifests/addons/dashboard counterparts
	  name: kubernetes-dashboard-v1.0.1
	  namespace: kube-system
	  labels:
	    k8s-app: kubernetes-dashboard
	    version: v1.0.1
	    kubernetes.io/cluster-service: "true"
	spec:
	  replicas: 1
	  selector:
	    k8s-app: kubernetes-dashboard
	  template:
	    metadata:
	      labels:
		k8s-app: kubernetes-dashboard
	        version: v1.0.1
	        kubernetes.io/cluster-service: "true"
	    spec:
	      containers:
	      - name: kubernetes-dashboard
	        image: gcr.io/google_containers/kubernetes-dashboard-amd64:v1.0.1
	        resources:
	          # keep request = limit to keep this container in guaranteed class
	          limits:
	            cpu: 100m
	            memory: 50Mi
	          requests:
	            cpu: 100m
	            memory: 50Mi
	        ports:
		- containerPort: 9090
	        args:
	          - --apiserver-host=10.0.0.39:8080
	        livenessProbe:
	          httpGet:
	            path: /
	            port: 9090
	          initialDelaySeconds: 30
	          timeoutSeconds: 30


Creamos el servicio añadiendo NodePort

`kubectl create -f kubernetes/cluster/addons/dashboard/dashboard-service.yaml`

	apiVersion: v1
	kind: Service
	metadata:
	  name: kubernetes-dashboard
	  namespace: kube-system
	  labels:
	    k8s-app: kubernetes-dashboard
	    kubernetes.io/cluster-service: "true"
	spec:
	  type: NodePort
	  selector:
	    k8s-app: kubernetes-dashboard
	  ports:
	  - port: 80
	    targetPort: 9090
	  args:
  		- --port=9090
  		- --apiserver-host=10.254.0.1:8080
  		command:
  		- /dashboard
  		- --port=9090
  		- --apiserver-host=10.254.0.1:8080


Responderá con el puerto

	You have exposed your service on an external port on all nodes in your
	cluster.  If you want to expose this service to the external internet, you may
	need to set up firewall rules for the service port(s) (tcp:31974) to serve traffic.

Resultado

	[root@morrigan centos]# kubectl get pod --namespace=kube-system
	NAME                                READY     STATUS    RESTARTS   AGE
	kube-dns-v9-0wxmo                   4/4       Running   5          23h
	kubernetes-dashboard-v1.0.1-xtlxr   1/1       Running   0          1m

	[root@morrigan centos]# kubectl get svc --namespace=kube-system
	NAME                   CLUSTER_IP       EXTERNAL_IP   PORT(S)         SELECTOR                       AGE
	kube-dns               10.254.0.10      <none>        53/UDP,53/TCP   k8s-app=kube-dns               4d
	kubernetes-dashboard   10.254.236.238   <none>        80/TCP          k8s-app=kubernetes-dashboard   57s

Entramos desde el navegador con `http://172.22.205.243:31974/`

---------------------------------

[Anterior](3-Kube_HA_pcs.md) | [Siguiente](5-Exponer_svc.md)

