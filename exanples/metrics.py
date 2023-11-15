import httpx
import json
query = """
container_memory_usage_bytes{namespace="qjnvahegmv", pod="mydb-1-56fd9744fd-7vrh7"}[10h]
"""
url = "http://127.0.0.1:9090/api/v1/query"
params = {
    "query": query
}
r = httpx.get(url, params=params)

print(json.dumps(r.json(), indent=4))
