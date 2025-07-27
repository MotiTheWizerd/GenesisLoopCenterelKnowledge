import requests

response = requests.get("http://localhost:8000/")
print(response.status_code)  # Should print 200
print(response.json())       # Should print {"message": "Hello World"}