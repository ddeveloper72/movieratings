# Quick Fix Commands for Movie Rater Backend Issues

## 🚨 IMMEDIATE COMMANDS TO RUN

### 1. Check the Exact Error (Run this first!)
```bash
heroku logs --tail -a ddeveloper72-movie-rater-api
```
**Look for:** Python tracebacks, database errors, import errors

### 2. Check Database Status
```bash
heroku pg:info -a ddeveloper72-movie-rater-api
```

### 3. Check and Apply Migrations
```bash
# See migration status
heroku run python manage.py showmigrations -a ddeveloper72-movie-rater-api

# Apply any pending migrations
heroku run python manage.py migrate -a ddeveloper72-movie-rater-api
```

### 4. Test User Model in Django Shell
```bash
heroku run python manage.py shell -a ddeveloper72-movie-rater-api
```

Then in the shell:
```python
# Test basic User operations
from django.contrib.auth.models import User

# Try to list users (this is failing with 500)
try:
    users = User.objects.all()
    print(f"Found {len(users)} users")
    print(users)
except Exception as e:
    print(f"Error listing users: {e}")

# Try to create a user (this is failing with 500)
try:
    user = User.objects.create_user(username='testuser123', password='testpass123')
    print(f"Created user: {user}")
except Exception as e:
    print(f"Error creating user: {e}")

# Check if your custom serializers work
try:
    from api.serializers import UserSerializer
    data = {'username': 'test456', 'password': 'testpass123'}
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        print(f"Serializer created user: {user}")
    else:
        print(f"Serializer errors: {serializer.errors}")
except Exception as e:
    print(f"Serializer error: {e}")
```

### 5. Test Locally (Compare behavior)
```bash
cd "C:\Users\Duncan\Visual_Studio_Projects\MovieRaterApi"
python manage.py runserver
```

Then test the same endpoints locally:
```bash
# In another terminal
curl -X GET http://127.0.0.1:8000/api/users/
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "localtest", "password": "testpass123"}'
```

## 🔍 WHAT TO LOOK FOR IN LOGS

Common error patterns that cause 500s on user endpoints:

1. **Database Connection Errors:**
   ```
   django.db.utils.OperationalError
   connection to server at "xxx" failed
   ```

2. **Migration Errors:**
   ```
   django.db.utils.ProgrammingError: relation "auth_user" does not exist
   no such table: auth_user
   ```

3. **Import Errors:**
   ```
   ImportError: cannot import name 'xxx'
   ModuleNotFoundError: No module named 'xxx'
   ```

4. **Serializer Errors:**
   ```
   AttributeError: 'UserSerializer' object has no attribute 'xxx'
   KeyError: 'password'
   ```

5. **Settings Errors:**
   ```
   django.core.exceptions.ImproperlyConfigured
   ```

## 🛠️ LIKELY QUICK FIXES

Based on common issues:

### Fix 1: Reset Migrations (if migration issues)
```bash
# CAUTION: Only if no important data will be lost
heroku run python manage.py migrate --fake-initial -a ddeveloper72-movie-rater-api
```

### Fix 2: Update Requirements (if import errors)
```bash
# Make sure all dependencies are in requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push heroku master
```

### Fix 3: Check Environment Variables
```bash
heroku config -a ddeveloper72-movie-rater-api
```
Make sure you have:
- `SECRET_KEY`
- `DATABASE_URL`
- Any other required environment variables

### Fix 4: Restart Heroku App
```bash
heroku restart -a ddeveloper72-movie-rater-api
```

## 📋 MOST LIKELY CULPRITS

Based on the diagnostic results, the issue is probably:

1. **User model migration problem** (70% likely)
2. **UserSerializer configuration issue** (20% likely)  
3. **Database connection/permission issue** (10% likely)

## ✅ SUCCESS INDICATORS

You'll know it's fixed when:
- `heroku logs` shows no 500 errors
- `GET /api/users/` returns 200 or 401 (not 500)
- `POST /api/users/` accepts registration data
- Frontend registration works at https://angular-movie-rater.web.app

---

**After running the commands above, check the logs and update this document with your findings!**