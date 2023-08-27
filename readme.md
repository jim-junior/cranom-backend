# Cranom Backend

## Setting Up Docker

Redis

```bash
docker run --name cranom-redis -p 6379:6379 -d redis
docker run --name cranom-celery-redis -p 6380:6379 -d redis
```

Database

```sh
# Create volume
docker volume create cranom-pg-data


docker run --name cranom-postgres -v cranom-pg-data:/var/lib/postgresql/data -p 5455:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=cranom -e POSTGRES_DB=cranom -e PGDATA=/var/lib/postgresql/data/pgdata -d postgres
```

## Setting up KPACK

```sh
kubectl apply -f .config/kpack-secrets.yml 

kubectl apply -f .config/serviceaccount.yml 

kubectl apply -f .config/clusterstore.yml

kubectl apply -f .config/clusterstack.yml

kubectl apply -f .config/clusterbuilder.yml

```

## Running

```bash
# development
python manage.py runserver

# Produnction
daphne backend.asgi:application --port $PORT --bind 0.0.0.0 -v2

# Celery
celery -A backend worker -l INFO

```

### Environment Variable (.env)

```sh
DJANGO_SECRET_KEY=55pd&v_pb@nax%ar@pm&k2%dvlo3qn+^0@lo$=6
DEBUG=True
DEFAULT_FROM_EMAIL=jimjunior854@gmail.com
SERVER_EMAIL=jimjunior854@gmail.com
CHANNELS_REDIS_URL=redis://localhost:6379
CELERY_BROKER_REDIS_URL=redis://localhost:6380
DB_HOST=127.0.0.1
DB_PORT=5455
DB_NAME=cranom
DB_USER=cranom
DB_PASSWORD=password
MAILGUN_API_KEY=5665624917222649a8cd6d5bcc644cf7-2bab6b06-ef64d8fd
MAILGUN_SENDER_DOMAIN=sandbox1bab856e0f3d46a3a39af5b09cc0e948.mailgun.org
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-c103ae5a1628c16c68bc77451af5c1f1-X
FLUTTERWAVE_SECRET=FLWSECK_TEST-9dbffbbda5a3746b8e37eb4456886097-X
FLUTTERWAVE_HASH=9dbffbbda5a3746b8e37eb4456886097
FLUTTERWAVE_ENCRYPTION_KEY=FLWSECK_TEST5b63f3a70b92
GITHUB_WEBHOOK_SECRET=b3d9b3b0b3d9b3b0b3d9b3b0b3b0b3d9b3bb3d9
GITHUB_SECRET_HASH=b3d9b3b0b3d9b3b0b3d9b3b0b3b0b3d9b3bb3d9
KUBE_CLUSTER_TOKEN=
KUBE_CLUSTER_HOST=https://127.0.0.1:53707
```

### Kubernetes

To get the Access token for the kubernetes cluster you should do the following:

- Create a Service Account Secret

```yml
apiVersion: v1
kind: Secret
metadata:
  name: backend-token
  annotations:
    kubernetes.io/service-account.name: default
type: kubernetes.io/service-account-token
```

> You van also apply the secret which is found in the `.config/cluster-access-token.yml`

- Collect Access token and host

```bash
# Run this and Copy the token fron the Output
kubectl describe secret backend-token

# Copy the host fron the Output
kubectl config view --minify
```
