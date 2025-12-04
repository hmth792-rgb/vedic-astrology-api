import urllib.request
import json

url = "http://127.0.0.1:5000/api/v1/d1-chart-refined"

data = {
    "name": "Hemant Rathore",
    "datetime": "1987-05-04T19:43:00",
    "latitude": 26.14093550,
    "longitude": 91.79102650,
    "timezone": 5.5,
    "place": "Dispur",
    "religion": "Hindu"
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
