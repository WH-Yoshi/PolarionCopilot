import requests
import json

url = "https://marketplace.tensordock.com/api/v0/client/deploy/hostnodes"

payload = "curl --location --request GET 'https://marketplace.tensordock.com/api/v0/client/deploy/hostnodes'"
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

json_response = json.loads(response.text)
print(json.dumps(json_response, indent=2))
