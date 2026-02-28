import requests, re

BASE = "http://127.0.0.1:8000"
s = requests.Session()

# Debug register
r = s.get(f"{BASE}/register/")
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
print("CSRF found:", bool(csrf))

r = s.post(f"{BASE}/register/", data={
    "csrfmiddlewaretoken": csrf.group(1) if csrf else "",
    "username": "debuguser2",
    "email": "debuguser2@test.com",
    "password1": "Str0ngP@ss99!",
    "password2": "Str0ngP@ss99!",
    "role": "author",
}, allow_redirects=False)
print(f"Register status: {r.status_code}")
print(f"Register location: {r.headers.get('Location', 'none')}")
if r.status_code == 200:
    errors = re.findall(r'<ul class="errorlist">(.*?)</ul>', r.text, re.DOTALL)
    print(f"Error lists: {errors[:5]}")
    # Also dump form section
    form_section = re.search(r'<form(.*?)</form>', r.text, re.DOTALL)
    if form_section:
        # Get just error parts
        for line in form_section.group(0).split('\n'):
            if 'error' in line.lower() or 'alert' in line.lower():
                print("ERR LINE:", line.strip()[:200])

# Debug login
print("\n--- LOGIN DEBUG ---")
s2 = requests.Session()

# First check: does the user exist?
# Try login with email
r = s2.get(f"{BASE}/login/")
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)

# Extract form fields to see what the login form expects
inputs = re.findall(r'<input[^>]*name="([^"]+)"', r.text)
print(f"Login form fields: {inputs}")

r = s2.post(f"{BASE}/login/", data={
    "csrfmiddlewaretoken": csrf.group(1) if csrf else "",
    "username": "admin@example.com",
    "password": "admin123",
}, allow_redirects=False)
print(f"Login status: {r.status_code}")
print(f"Login location: {r.headers.get('Location', 'none')}")

if r.status_code == 200:
    errors = re.findall(r'<ul class="errorlist">(.*?)</ul>', r.text, re.DOTALL)
    print(f"Login errors: {errors[:3]}")
    for line in r.text.split('\n'):
        if 'error' in line.lower() and '<' in line:
            print("ERR:", line.strip()[:200])
