from kubernetes import client, config, utils
import yaml
from yaml.loader import BaseLoader

aToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ik9GM3lpQVVVdXhJeXN4V0o5QjNOeWFNR29vaXZqa2I0RnVVTW91M1E0V1EifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJsa2UtYWRtaW4tdG9rZW4tcHI2NnoiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibGtlLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNDBjNTE0YTctZTBkZi00MTBkLWJmYTMtYWM5MWYyZDc3MzBiIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmxrZS1hZG1pbiJ9.pyuZTjQrstZ0NxtH7FxZuE5LIbhu5KsnfX5KLUg4-8KASEf3IaLi3IWfkK-f9TUSL9yD3HB2Zmp7UDQALO4l2sz9JIkM2bnAFfSUOzyYD45fLRh1w9L3jdjZArfm0OxcGTpLpaSO3RZ4dWX5i2jISv28gdI3dlZhswp0h64leYVD1nJVToE0FSRtDL6cs8C1ovCUgtqLxKKSgIbMspbQGcmWtSbAV9SqWkogD8zWGcDvst-wmun0vpV1VNzq7-XwvDKSgtx_9UpUwx38nPEoOa3g-5jB29Pq4K1kwyw3PUBq4rwB3vAlM_Co-VBMSVMHwqHr8dgQ1_EIN4qRsl4v4Q"


aConfiguration = client.Configuration()

aConfiguration.host = "https://a23acc63-1573-45f4-b926-acb7b99d65de.ap-south-2.linodelke.net:443"


aConfiguration.verify_ssl = False


aConfiguration.api_key = {"authorization": "Bearer " + aToken}

aApiClient = client.ApiClient(aConfiguration)

v1 = client.CoreV1Api(aApiClient)

img = """apiVersion: kpack.io/v1alpha2
kind: Image
metadata:
  name: tutorial-image-1
  namespace: default
spec:
  tag: jimjuniorb/default-kpack
  serviceAccountName: kpack-sva
  builder:
    name: default-builder
    kind: ClusterBuilder
  source:
    git:
      url: https://github.com/Blazity/next-saas-starter
      revision: 4233a52c7d5441e1582479c0f087c262d92a112d
"""

di = yaml.load(img, BaseLoader)
# print(di)

api = client.CustomObjectsApi(aApiClient)

api.create_namespaced_custom_object(
    group="kpack.io",
    version="v1alpha2",
    namespace="default",
    plural="images",
    body=di,
)
