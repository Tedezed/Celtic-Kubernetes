<<<<<<< HEAD
kubectl get pods --all-namespaces=true -o wide
kubectl cluster-info

utenticación y autorización
============================

* [Fuente](http://kubernetes.io/docs/admin/authentication/)
* [Fuente](http://www.dasblinkenlichten.com/kubernetes-authentication-plugins-and-kubeconfig/)

    Generate a ca.key with 2048bit:

      openssl genrsa -out ca.key 2048

    According to the ca.key generate a ca.crt (use -days to set the certificate effective time):

      openssl req -x509 -new -nodes -key ca.key -subj "/CN=${MASTER_IP}" -days 10000 -out ca.crt

    Generate a server.key with 2048bit

      openssl genrsa -out server.key 2048

    According to the server.key generate a server.csr:

      openssl req -new -key server.key -subj "/CN=${MASTER_IP}" -out server.csr

    According to the ca.key, ca.crt and server.csr generate the server.crt:

      openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 10000

    View the certificate.

      openssl x509  -noout -text -in ./server.crt
=======
kubectl get pods --all-namespaces=true
kubectl cluster-info
>>>>>>> 324fe55465cb37533e0d50a571dbc2358458b4b4
