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
  <li><a class="bar" href="9-ElasticKube.md">ElasticKube</a></li>
  <li><a class="active" href="10-Conclusion.md">Conclusión</a></li>
  <li style="float:bottom"><a class="bar" href="Contacto.md">Contacto</a></li>
</ul>
</div>
<div id="control"> 
 <ul>
  <li><a class="next" href="9-ElasticKube.md">Anterior</a></li>
</ul>
</div>


Conclusión Kuernetes y OpenStack
================================

Después de desplegar un cluster a mano de Kubernetes en completo HA sobre OpenStack e investigar el futuro de como planean se relacionaran estas dos tecnologías, se establecen dos formas de utilización:

* ##### Usar Kubernetes para gestionar las cargas de trabajo de contenedores que se ejecuten en OpenStack

* ##### Usar Kubernetes para gestionar los servicios de OpenStack en contenedores propios

Los componentes a utilizar podrían ser:

* **Kolla** - OpenStack proporciona servicio de contenedores y herramientas de despliegue para el funcionamiento de las nubes OpenStack

* **Kuryr** - Proporciona puentes entre los modelos contenedores de redes/almacenamiento  y la infraestructura de servicios de OpenStack

* **Magnum** - Proporciona contenedores como un servicio para OpenStack

* **Murano** - Proporciona un catálogo de aplicaciones para OpenStack incluyendo soporte para Kubernetes, y para aplicaciones en contenedores, gestionados por Kubernetes.

--------------------

Por ultimo, muestro el componente que pienso que es el que pienso que marcara la utilización de Kubernetes en un entorno para producción sobre OpenStack.

--------------------

Magnum OpenStack
================

* http://egonzalez.org/magnum-in-rdo-openstack-liberty-manual-installation-from-source-code/
* http://docs.openstack.org/developer/magnum/dev/manual-devstack.html
* http://docs.openstack.org/developer/magnum/dev/dev-quickstart.html

#### Despliege de Magnum sobre RDO en CentOS

Cargamos la variables del sistema:

    source /root/keystonerc_admin; source /root/virtualenv/v-magnum/bin/activate; cd /root/virtualenv/v-magnum/git/magnum/
  
    source /root/keystonerc_admin

Instalamos lo siguiente 

   yum install -y gcc python-setuptools python-devel git libffi-devel openssl-devel wget python-pip python-docker-py python-virtualenv

Realizamos un upgrade de pip

    pip install --upgrade pip

Clonamos el repositorio de Magnum

    git clone https://git.openstack.org/openstack/magnum -b stable/liberty

Instalamos magnum

    cd magnum
    sudo pip install -e .

Creamos la base de datos de Magnum y su usuario

````
mysql -u root
CREATE DATABASE IF NOT EXISTS magnum DEFAULT CHARACTER SET utf8;
GRANT ALL PRIVILEGES ON magnum.* TO'magnum'@'localhost' IDENTIFIED BY 'temporal';
GRANT ALL PRIVILEGES ON magnum.* TO'magnum'@'%' IDENTIFIED BY 'temporal';
exit
````

Copiamos la configuración de Magnum

````
mkdir /etc/magnum
sudo cp etc/magnum/magnum.conf.sample /etc/magnum/magnum.conf
sudo cp etc/magnum/policy.json /etc/magnum/policy.json
````

Configuración de Magnum

````
sed -i -e 's$#host = 127.0.0.1$host = 0.0.0.0$g' \
        -e 's$#rpc_backend = rabbit$rpc_backend = rabbit$g' \
        -e 's$#notification_driver =$notification_driver = messaging$g' \
        -e 's$#rabbit_host = localhost$rabbit_host = 192.168.122.212$g' \
        -e 's$#rabbit_userid = guest$rabbit_userid = guest$g' \
        -e 's$#rabbit_password = guest$rabbit_password = guest$g' \
        -e 's$#rabbit_virtual_host = /$rabbit_virtual_host = /$g' \
        -e 's$#connection = <None>$connection = mysql://magnum:temporal@192.168.122.212/magnum$g' \
        -e 's$#cert_manager_type = barbican$cert_manager_type = local$g' \
        /etc/magnum/magnum.conf
````

````
nano /etc/magnum/magnum.conf
````

````
[keystone_authtoken]
auth_uri=http://192.168.122.212:5000/v2.0
identity_uri=http://192.168.122.212:35357
auth_strategy=keystone
admin_user=magnum
admin_password=temporal
admin_tenant_name=services
````

El fichero deberá quedar de la siguiente forma:

````
nano /etc/magnum/magnum.conf
````

````
[DEFAULT]
notification_driver = messaging
rpc_backend = rabbit

[api]
host = 0.0.0.0

[barbican_client]
[bay]
[bay_heat]

[certificates]
cert_manager_type = local


[conductor]
[database]
connection = mysql://magnum:temporal@192.168.122.212/magnum


[docker]
[glance_client]
[heat_client]

[keystone_authtoken]
auth_uri=http://192.168.122.212:5000/v2.0
identity_uri=http://192.168.122.212:35357
auth_strategy=keystone
admin_user=magnum
admin_password=temporal
admin_tenant_name=services

[magnum_client]
[matchmaker_redis]
[matchmaker_ring]
[nova_client]
[oslo_concurrency]
[oslo_messaging_amqp]
[oslo_messaging_qpid]

[oslo_messaging_rabbit]
rabbit_host = 192.168.122.212
rabbit_userid = guest
rabbit_password = guest
rabbit_virtual_host = /

[oslo_policy]
[x509]
````

Creamos la siguiente carpeta para los certificados

````
mkdir -p /var/lib/magnum/certificates/
````

Instalamos python-magnumclient

````
git clone https://git.openstack.org/openstack/python-magnumclient -b stable/liberty
cd python-magnumclient
sudo pip install -e .
````

Creamos el servicio

````
(v-magnum)[root@localhost python-magnumclient(keystone_admin)]# openstack user create --password temporal magnum
+----------+----------------------------------+
| Field    | Value                            |
+----------+----------------------------------+
| email    | None                             |
| enabled  | True                             |
| id       | 48123575864f4dd299bec1701a619e83 |
| name     | magnum                           |
| username | magnum                           |
+----------+----------------------------------+
````

````
(v-magnum)[root@localhost python-magnumclient(keystone_admin)]# openstack role add --project services --user magnum admin
+-----------+----------------------------------+
| Field     | Value                            |
+-----------+----------------------------------+
| domain_id | None                             |
| id        | 421f5809823e4ea99bee48cd944712d4 |
| name      | admin                            |
+-----------+----------------------------------+
````

````
(v-magnum)[root@localhost python-magnumclient(keystone_admin)]# openstack service create --name magnum --description "Magnum Container Service" container
+-------------+----------------------------------+
| Field       | Value                            |
+-------------+----------------------------------+
| description | Magnum Container Service         |
| enabled     | True                             |
| id          | 33d77d45bc9c43f28cd1fec9a4e7243d |
| name        | magnum                           |
| type        | container                        |
+-------------+----------------------------------+
````

Creamos el endpoint para Magnum

````
(v-magnum)[root@localhost python-magnumclient(keystone_admin)]# openstack endpoint create --region RegionOne --publicurl 'http://192.168.122.212:9511/v1' --adminurl 'http://192.168.122.212:9511/v1' --internalurl 'http://192.168.122.212:9511/v1' magnum
+--------------+----------------------------------+
| Field        | Value                            |
+--------------+----------------------------------+
| adminurl     | http://192.168.122.212:9511/v1   |
| id           | 32f56bf311914a30ad3434f4bbd7bfb6 |
| internalurl  | http://192.168.122.212:9511/v1   |
| publicurl    | http://192.168.122.212:9511/v1   |
| region       | RegionOne                        |
| service_id   | 33d77d45bc9c43f28cd1fec9a4e7243d |
| service_name | magnum                           |
| service_type | container                        |
+--------------+----------------------------------+
````

Sincronizamos la base de datos de magnum

````
magnum-db-manage --config-file /etc/magnum/magnum.conf upgrade
````

Abrimos dos terminales ejecutando un comando en cada terminal, para realizar un test:

````
magnum-api --config-file /etc/magnum/magnum.conf
magnum-conductor --config-file /etc/magnum/magnum.conf
````

Ya que estamos en un entorno de pruebas podemos borrar la siguiente linea de `/etc/magnum/policy.json`

  "admin_api": "rule:context_is_admin",

Realizamos un test con

````
(v-magnum)[root@localhost magnum(keystone_admin)]# magnum service-list
+----+-----------------------+------------------+-------+
| id | host                  | binary           | state |
+----+-----------------------+------------------+-------+
| 1  | localhost.localdomain | magnum-conductor | up    |
+----+-----------------------+------------------+-------+
````

Podemos bajar la siguiente imagen de Fedora preparada para magnum

````
wget https://fedorapeople.org/groups/magnum/fedora-21-atomic-5.qcow2
````

Añadimos la imagen

````
glance image-create --name fedora-21-atomic-5 \
                    --visibility public \
                    --disk-format qcow2 \
                    --os-distro fedora-atomic \
                    --container-format bare < fedora-21-atomic-5.qcow2
````

Creamos un par de claves si no tenemos estas

````
test -f ~/.ssh/id_rsa.pub || ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
````

Añadimos la nueva clave

````
nova keypair-add --pub-key ~/.ssh/id_rsa.pub kube-test
````

Creamos una nueva baymodel

````
magnum baymodel-create --name k8sbaymodel \
                       --image-id fedora-21-atomic-5 \
                       --keypair-id kube-test \
                       --external-network-id public \
                       --dns-nameserver 8.8.8.8 \
                       --flavor-id m1.small \
                       --docker-volume-size 5 \
                       --network-driver flannel \
                       --coe kubernetes
````

```
+---------------------+--------------------------------------+
| Property            | Value                                |
+---------------------+--------------------------------------+
| http_proxy          | None                                 |
| updated_at          | None                                 |
| master_flavor_id    | None                                 |
| fixed_network       | None                                 |
| uuid                | dd0a910e-4553-4b51-b6a2-1d106811a869 |
| no_proxy            | None                                 |
| https_proxy         | None                                 |
| tls_disabled        | False                                |
| keypair_id          | kube-test                            |
| public              | False                                |
| labels              | {}                                   |
| docker_volume_size  | 5                                    |
| external_network_id | public                               |
| cluster_distro      | fedora-atomic                        |
| image_id            | fedora-21-atomic-5                   |
| registry_enabled    | False                                |
| apiserver_port      | None                                 |
| name                | k8sbaymodel                          |
| created_at          | 2016-06-15T11:19:51+00:00            |
| network_driver      | flannel                              |
| ssh_authorized_key  | None                                 |
| coe                 | kubernetes                           |
| flavor_id           | m1.small                             |
| dns_nameserver      | 8.8.8.8                              |
+---------------------+--------------------------------------+
```

Creamos una nueva bay para Kubernetes

````
magnum bay-create --name k8sbay --baymodel k8sbaymodel --master-count 1 --node-count 1
````

--------------

<div id="control"> 
 <ul>
  <li><a class="next" href="9-ElasticKube.md">Anterior</a></li>
</ul>
</div>