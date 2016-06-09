Documentación
http://blog.kubernetes.io/2016/04/introducing-kubernetes-openstack-sig.html
https://www.mirantis.com/blog/magnum-vs-murano-openstack-container-strategy/

Openstack y Kubernetes
http://www.tcpcloud.eu/en/blog/2016/02/12/kubernetes-and-openstack-multi-cloud-networking/

Autoescalado:
https://github.com/metral/corekube/blob/master/corekube-openstack.yaml
http://superuser.openstack.org/articles/simple-auto-scaling-environment-with-heat/
https://keithtenzer.com/2015/10/05/auto-scaling-applications-with-openstack-heat/

Magnum:
http://egonzalez.org/magnum-in-rdo-openstack-liberty-manual-installation-from-source-code/

Usar Kubernetes para gestionar las cargas de trabajo de contenedores que se ejecuten en OpenStack

Usar Kubernetes para gestionar los servicios de OpenStack en contenedores propios

Kolla - OpenStack proporciona servicio de contenedores y herramientas de despliegue para el funcionamiento de las nubes OpenStack

Kuryr - Proporciona puentes entre los modelos contenedores de redes/almacenamiento  y la infraestructura de servicios de OpenStack

Magnum - Proporciona contenedores como un servicio para OpenStack

Murano - Proporciona un catálogo de aplicaciones para OpenStack incluyendo soporte para Kubernetes, y para aplicaciones en contenedores, gestionados por Kubernetes.

----------------------

http://hap-vip/kubernetes-dashboard/

watch -n 5 "ssh centos@artio free -h; ssh centos@esus free -h"

for file in $(ls | grep "\.yaml"); do kubectl create -f $file; done
for file in $(ls | grep "\.yaml"); do kubectl delete -f $file; done

apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-3g-db
spec:
  capacity:
    storage: 3Gi
  accessModes:
    - ReadWriteMany
  glusterfs:
    path: dist-volume
    endpoints: glusterfs-cluster
    readOnly: false
  persistentVolumeReclaimPolicy: Retain
----
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: claim-db
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 3Gi
----
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-3g-web
spec:
  capacity:
    storage: 3Gi
  accessModes:
    - ReadWriteMany
  glusterfs:
    path: dist-volume
    endpoints: glusterfs-cluster
    readOnly: false
  persistentVolumeReclaimPolicy: Retain
----
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: claim-web
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 3Gi
----
apiVersion: v1
kind: ReplicationController
metadata:
  name: mysql
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
          - name: mysql
            containerPort: 3306
            hostPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              value: root
          securityContext:
            capabilities: {}
            privileged: true
          volumeMounts:
          - name: mysql-persistent-storage
            mountPath: /var/lib/mysql
      volumes:
      - name: mysql-persistent-storage
        persistentVolumeClaim:
          claimName: claim-db
----
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    node: mysql
spec:
  clusterIP: 10.254.200.20
  ports:
    - port: 3306
      targetPort: 3306
  selector:
    name: mysql
----
apiVersion: v1
kind: ReplicationController
metadata:
  name: wordpress
  labels:
    name: wordpress
spec:
  replicas: 1
  selector:
    name: wordpress
  template:
    metadata:
      labels:
        name: wordpress
    spec:
      containers:
      - name: wordpress
        image: wordpress
        ports:
        - containerPort: 80
          name: wordpress
        env:
          - name: WORDPRESS_DB_PASSWORD
            value: root
          - name: WORDPRESS_DB_HOST
            value: 10.254.200.20
        securityContext:
          capabilities: {}
          privileged: true
        volumeMounts:
        - name: wordpress-persistent-storage
          mountPath: /var/www/html
      volumes:
      - name: wordpress-persistent-storage
        persistentVolumeClaim:
          claimName: claim-web
----
apiVersion: v1
kind: Service
metadata:
  labels:
    name: wordpress
    domain: wordpress.test.com
  name: wordpress
spec:
  type: NodePort
  clusterIP: 10.254.200.10
  ports:
    - port: 80
      protocol: TCP
      name: http
  selector:
    name: wordpress


Almacenamiento:

/mnt/gluster-v-dist