<div id="header"> 
 <ul>
  <li><a class="bar" href="1-Portada.md">Home</a></li>
  <li><a class="bar" href="2-Kube_simple.md">Kubernetes Simple</a></li>
  <li><a class="bar" href="3-Kube_HA_pcs.md">Kubernetes HA</a></li>
  <li><a class="bar" href="4-Addons.md">Addons</a></li>
  <li><a class="bar" href="5-Exponer_svc.md">Exponer servicios</a></li>
  <li><a class="bar" href="6-Almacenamiento.md">Almacenamiento persistente</a></li>
  <li><a class="bar" href="7-Explotando_kubernetes.md">Utilización</a></li>
  <li><a class="bar" href="8-Kubernetes_ansible.md">Kubernetes y Ansible</a></li>
  <li><a class="active" href="9-ElasticKube.md">ElasticKube</a></li>
  <li style="float:bottom"><a class="bar" href="Contacto.md">Contacto</a></li>
</ul>
</div>
<div id="control"> 
 <ul>
  <li><a class="next" href="8-Kubernetes_ansible.md">Anterior</a></li>
</ul>
</div>

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

#### Instalación:

* Metodo 1

		curl -s https://elastickube.com | bash

* Metodo 2

		curl -s https://elastickube.com | bash -s -- -u http://10.0.0.39:8080

* Metodo 3

		curl -s https://elastickube.com > deploy.sh
		sh deploy.sh -u http://10.0.0.39:8080

* Metodo 4

		curl -s https://raw.githubusercontent.com/ElasticBox/elastickube/master/build/deploy.sh | bash

* Mediante plantilla yaml

      apiVersion: v1
      kind: ReplicationController
      metadata:
        name: elastickube-mongo
        namespace: kube-system
        labels:
          name: elastickube-mongo
      spec:
        replicas: 1
        selector:
          name: elastickube-mongo
        template:
          metadata:
            labels:
              name: elastickube-mongo
          spec:
            containers:
              - image: mongo
                name: elastickube-mongo
                args:
                - --replSet=elastickube
                ports:
                - name: mongo
                  containerPort: 27017
                  hostPort: 27017
                volumeMounts:
                  - name: mongo-persistent-storage
                    mountPath: /data/mongodb
            volumes:
            - name: mongo-persistent-storage
              hostPath:
                path: /data/mongodb
      ----
      apiVersion: v1
      kind: Service
      metadata:
        name: elastickube-mongo
        namespace: kube-system
        labels:
          name: elastickube-mongo
      spec:
        ports:
          - port: 27017
            targetPort: 27017
        selector:
          name: elastickube-mongo
      ----
      apiVersion: v1
      kind: ReplicationController
      metadata:
        name: elastickube-server
        namespace: kube-system
        labels:
          name: elastickube-server
      spec:
        replicas: 1
        selector:
          name: elastickube-server
        template:
          metadata:
            labels:
              name: elastickube-server
          spec:
            containers:
            - name: elastickube-api
              image: elasticbox/elastickube-api:latest 
              resources:
                limits:
                  cpu: 100m
                  memory: 300Mi
              volumeMounts:
              - name: elastickube-run
                mountPath: /var/run
              env:
              - name: KUBERNETES_SERVICE_HOST
                value: http://10.0.0.39:8080
            - name: elastickube-charts
              image: elasticbox/elastickube-charts:latest 
              resources:
                limits:
                  cpu: 100m
                  memory: 300Mi
              volumeMounts:
              - name: elastickube-charts
                mountPath: /var/elastickube/charts
            - name: elastickube-nginx
              image: elasticbox/elastickube-nginx:latest 
              resources:
                limits:
                  cpu: 100m
                  memory: 300Mi
              volumeMounts:
              - name: elastickube-run
                mountPath: /var/run
              ports:
              - containerPort: 80
                hostPort: 80
                name: http
                protocol: TCP
            - name: elastickube-diagnostics
              image: elasticbox/elastickube-diagnostics:latest 
              resources:
                limits:
                  cpu: 10m
                  memory: 32Mi
              volumeMounts:
              - name: elastickube-run
                mountPath: /var/run
            volumes:
            - name: elastickube-charts
              hostPath:
                path: /var/elastickube/charts
            - name: elastickube-run
              hostPath:
                path: /var/run/elastickube
      ----
      apiVersion: v1
      kind: Service
      metadata:
        name: elastickube-server
        namespace: kube-system
        labels:
          domain: elastickube.test.com
          name: elastickube-server
      spec:
        type: NodePort
        ports:
        - port: 80
          protocol: TCP
          name: http
        selector:
          name: elastickube-server

#### Borrar Elastickube

	kubectl --namespace=kube-system delete rc elastickube-server; kubectl --namespace=kube-system delete rc elastickube-mongo; kubectl --namespace=kube-system delete svc elastickube-server; kubectl --namespace=kube-system delete svc elastickube-mongo

#### Ejecución

Salida del comando si instalamos con metodo 1/4

````
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
````

Podemos ver la información con

	kubectl --namespace=kube-system describe svc elastickube-server 

Diagnosticamos la aplicación, accedemos con la ip o nombre de los minions, ya que por defecto se establecera el el puerto 80.

http://artio/diagnostics/

#### Contenido:

* **Kubernetes Connection:** Comprueba si ElasticKube tiene acceso a la API Kubernetes..

* **Mongo Connection:** Comprueba si el rc de MongoDB se esta ejecutando.

* **Websocket Service and Chart Service:** Comprueba si el rc de ElasticKube Server se está ejecutando.

* **Internet Connection:** Comprueba la conexión con internet.

* **Heapster Connection:** Componente para la extración de datos.

* **Kubernetes DNS:** Comprueba si el DNS interno de KUbernetes se esta ejecutando.


Podremos entrar con: 

	kubectl exec -ti elastickube-server-pri32 --namespace=kube-system bash


Comienzo con Elastickube
------------------------

Al entrar por primera vez, nos permitira crear el usuario Administrador; admin/adminadmin


---------------

Diagnostico

docker ps | grep elastickube-server


`kubectl logs elastickube-server-0pz5j elastickube-diagnostics --namespace=kube-system`
```
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 2.58ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 1.96ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 1.44ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 9.05ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 3.79ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 1.80ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 3.93ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 1.60ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 3.46ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 2.06ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 4.08ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 1.54ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-90d3804f0231704c15ccc5861245e8ce.woff (0.0.0.0) 2.86ms
  WARNING:tornado.access:404 GET /assets/fonts/Roboto-Thin-cc85ce37b4256966e6f3a3559239c5c0.ttf (0.0.0.0) 1.25ms
```
`kubectl logs elastickube-server-0pz5j elastickube-api --namespace=kube-system`
```
  Initializing
  MongoDB shell version: 3.2.6
  connecting to: 10.254.101.14:27017/admin
  bye
  INFO:root:Reading token from '/var/run/secrets/kubernetes.io/serviceaccount/token'.
  DEBUG:root:Building available metrics
  INFO:root:Initializing database...
  DEBUG:root:Initial Settings document created, 57514c513313d60010e4f509
  INFO:root:Initializing SyncNamespaces
  INFO:root:start_sync SyncNamespaces
  INFO:root:Initializing SyncMetrics
  INFO:root:start_sync SyncMetrics
  INFO:root:Initializing watcher...
  INFO:root:Watching from timestamp: 2016-06-03 09:22:26+00:00
  DEBUG:root:Tailable cursor recreated.
  INFO:root:Initializing MainWebSocketHandler
  INFO:root:Initializing LogsActions
  INFO:root:Initializing InstancesActions
  INFO:root:Initializing NamespacesActions
  INFO:root:Initializing SettingsActions
  INFO:root:Initializing UsersActions
  INFO:root:Initializing InviteActions
  INFO:root:Closing MainWebSocketHandler
  WARNING:root:Disconnected from kubeclient in SyncNamespaces
  INFO:root:Initializing MainWebSocketHandler
  INFO:root:Initializing LogsActions
  INFO:root:Initializing InstancesActions
  INFO:root:Initializing NamespacesActions
  INFO:root:Initializing SettingsActions
  INFO:root:Initializing UsersActions
  INFO:root:Initializing InviteActions
  INFO:root:Closing MainWebSocketHandler
```
`printenv`
```
  HEAPSTER_SERVICE_PORT=80
  MONITORING_INFLUXDB_PORT_8083_TCP_PROTO=tcp
  HOSTNAME=elastickube-server-0pz5j
  GPG_KEY=C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF
  KUBE_DNS_PORT_53_UDP_ADDR=10.254.0.10
  ELASTICKUBE_SERVER_PORT_80_TCP_ADDR=10.254.51.59
  KUBE_DNS_PORT_53_UDP_PROTO=udp
  KUBERNETES_PORT_443_TCP_PORT=443
  ELASTICKUBE_SERVER_PORT_80_TCP_PROTO=tcp
  MONITORING_INFLUXDB_SERVICE_PORT_HTTP=8083
  KUBERNETES_PORT=tcp://10.254.0.1:443
  KUBE_DNS_SERVICE_PORT=53
  MONITORING_GRAFANA_PORT=tcp://10.254.42.145:80
  KUBERNETES_DASHBOARD_PORT_80_TCP_ADDR=10.254.8.75
  KUBERNETES_SERVICE_PORT=443
  HEAPSTER_SERVICE_HOST=10.254.138.182
  ELASTICKUBE_PATH=/opt/elastickube
  KUBERNETES_SERVICE_HOST=10.254.0.1
  ELASTICKUBE_MONGO_SERVICE_PORT=27017
  ELASTICKUBE_MONGO_PORT=tcp://10.254.101.14:27017
  MONITORING_INFLUXDB_PORT_8083_TCP_ADDR=10.254.150.183
  KUBERNETES_DASHBOARD_PORT=tcp://10.254.8.75:80
  HEAPSTER_PORT_80_TCP_PORT=80
  KUBE_DNS_SERVICE_PORT_DNS_TCP=53
  KUBE_DNS_PORT_53_TCP_PORT=53
  MONITORING_GRAFANA_PORT_80_TCP_PORT=80
  ELASTICKUBE_MONGO_PORT_27017_TCP_ADDR=10.254.101.14
  MONITORING_GRAFANA_PORT_80_TCP_PROTO=tcp
  KUBE_DNS_PORT_53_TCP_PROTO=tcp
  KUBERNETES_DASHBOARD_PORT_80_TCP_PORT=80
  HEAPSTER_PORT=tcp://10.254.138.182:80
  MONITORING_INFLUXDB_PORT_8083_TCP_PORT=8083
  KUBERNETES_DASHBOARD_SERVICE_HOST=10.254.8.75
  PYTHON_VERSION=2.7.11
  MONITORING_INFLUXDB_SERVICE_PORT=8083
  HEAPSTER_PORT_80_TCP_PROTO=tcp
  MONITORING_GRAFANA_SERVICE_HOST=10.254.42.145
  ELASTICKUBE_SERVER_PORT_80_TCP_PORT=80
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
  MONITORING_INFLUXDB_PORT_8086_TCP_ADDR=10.254.150.183
  ELASTICKUBE_SERVER_SERVICE_PORT=80
  KUBERNETES_DASHBOARD_PORT_80_TCP_PROTO=tcp
  HEAPSTER_PORT_80_TCP_ADDR=10.254.138.182
  MONITORING_INFLUXDB_SERVICE_HOST=10.254.150.183
  MONITORING_INFLUXDB_PORT_8086_TCP=tcp://10.254.150.183:8086
  PWD=/var/log
  KUBE_DNS_SERVICE_PORT_DNS=53
  LANG=C.UTF-8
  KUBE_DNS_PORT_53_UDP_PORT=53
  MONITORING_INFLUXDB_PORT_8083_TCP=tcp://10.254.150.183:8083
  KUBE_API_TOKEN_PATH=/var/run/secrets/kubernetes.io/serviceaccount/token
  HEAPSTER_PORT_80_TCP=tcp://10.254.138.182:80
  MONITORING_GRAFANA_SERVICE_PORT=80
  KUBE_DNS_PORT=udp://10.254.0.10:53
  PYTHON_PIP_VERSION=8.1.2
  ELASTICKUBE_MONGO_PORT_27017_TCP=tcp://10.254.101.14:27017
  MONITORING_INFLUXDB_PORT_8086_TCP_PORT=8086
  MONITORING_INFLUXDB_SERVICE_PORT_API=8086
  ELASTICKUBE_SERVER_PORT=tcp://10.254.51.59:80
  KUBE_DNS_PORT_53_UDP=udp://10.254.0.10:53
  KUBERNETES_DASHBOARD_PORT_80_TCP=tcp://10.254.8.75:80
  SHLVL=1
  HOME=/root
  ELASTICKUBE_MONGO_PORT_27017_TCP_PORT=27017
  KUBERNETES_DASHBOARD_SERVICE_PORT=80
  KUBERNETES_PORT_443_TCP_PROTO=tcp
  KUBERNETES_SERVICE_PORT_HTTPS=443
  ELASTICKUBE_SERVER_SERVICE_HOST=10.254.51.59
  PYTHONPATH=/opt/elastickube
  MONITORING_INFLUXDB_PORT_8086_TCP_PROTO=tcp
  ELASTICKUBE_MONGO_SERVICE_HOST=10.254.101.14
  KUBE_DNS_PORT_53_TCP_ADDR=10.254.0.10
  MONITORING_GRAFANA_PORT_80_TCP_ADDR=10.254.42.145
  ELASTICKUBE_MONGO_PORT_27017_TCP_PROTO=tcp
  ELASTICKUBE_SERVER_PORT_80_TCP=tcp://10.254.51.59:80
  KUBE_DNS_PORT_53_TCP=tcp://10.254.0.10:53
  KUBERNETES_PORT_443_TCP_ADDR=10.254.0.1
  MONITORING_GRAFANA_PORT_80_TCP=tcp://10.254.42.145:80
  MONITORING_INFLUXDB_PORT=tcp://10.254.150.183:8083
  KUBE_DNS_SERVICE_HOST=10.254.0.10
  KUBERNETES_PORT_443_TCP=tcp://10.254.0.1:443
  _=/usr/bin/printenv
  OLDPWD=/
```

`root@elastickube-server-0pz5j:/var/log# curl -s 10.0.0.39:8080`
```
  {
    "paths": [
      "/api",
      "/api/v1",
      "/apis",
      "/healthz",
      "/healthz/ping",
      "/logs/",
      "/metrics",
      "/resetMetrics",
      "/swaggerapi/",
      "/version"
    ]
  }
```

`kubectl exec busybox -- nslookup kubernetes`
```
Server:    10.254.0.10
Address 1: 10.254.0.10

Name:      kubernetes
Address 1: 10.254.0.1
```

----------------------

<div id="control"> 
 <ul>
  <li><a class="next" href="8-Kubernetes_ansible.md">Anterior</a></li>
</ul>
</div>