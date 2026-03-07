import requests
s = requests.Session()
base = "http://localhost:5000"
results = []
routes = [
    ("GET", "/"), ("GET", "/signin.html"), ("GET", "/homepage.html"),
    ("GET", "/api/user_profile"), ("GET", "/api/profile_options"),
    ("GET", "/api/v2/course_catalogue"), ("GET", "/api/engineering_tasks"),
    ("GET", "/api/aptitude_questions"), ("GET", "/api/personality_questions"),
    ("GET", "/homepage"), ("GET", "/favicon.ico"),
]
for method, path in routes:
    try:
        r = s.get(base + path)
        code = r.status_code
        ok = "PASS" if code in (200, 204, 302, 401) else "FAIL"
        results.append(f"  {ok} {code:>3} {method} {path}")
    except Exception as e:
        results.append(f"  FAIL --- {method} {path} -> {e}")
with open("d:/vsscode/verify_results.txt", "w") as f:
    f.write("\n".join(results))
print("\n".join(results))
