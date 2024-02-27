import requests

hearders = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2ODI2MzMxMCwianRpIjoiYTVhODk0OTctYWVlOC00Y2ZmLTkwNjYtZWY5MGNjNWI2OWVlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ikp1UVVOV0szeTRkcERYYnFTV3daWlUiLCJuYmYiOjE2NjgyNjMzMTAsImV4cCI6MTY2ODI2NDIxMH0.Iyt6GFYL1LPuBLunnG84tuRMUCxHyc7m8X7VYJlYQBg"
}

resp = requests.get("http://127.0.0.1:5000/cmsapi", headers=hearders)
print(resp.text)