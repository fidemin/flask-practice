


# install ingress-nginx
#kubectl create namespace ingress-nginx
#helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
#helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx

minikube addons enable ingress

# install metric-server
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server -f metric-server-values.yaml

