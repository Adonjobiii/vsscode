import urllib.request, urllib.error, json

req = urllib.request.Request(
    'http://localhost:5000/api/signup',
    data=json.dumps({'first_name':'Test', 'last_name':'User', 'email':'test@test.com'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
