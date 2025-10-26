#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movierater.settings')
django.setup()

from django.contrib.auth.models import User

print("Testing User model operations...")

try:
    print("1. Testing User.objects.all()...")
    users = User.objects.all()
    print(f"✅ Found {len(users)} users")
    for user in users[:3]:  # Show first 3 users
        print(f"  - {user.username} (id: {user.id})")
except Exception as e:
    print(f"❌ ERROR listing users: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. Testing User creation...")
    user = User.objects.create_user(username='diagtest', password='testpass123')
    print(f"✅ Created user: {user}")
    user.delete()  # cleanup
    print("✅ User deleted successfully")
except Exception as e:
    print(f"❌ ERROR creating user: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. Testing UserSerializer...")
    from api.serializers import UserSerializer
    data = {'username': 'serialtest', 'password': 'testpass123'}
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        print(f"✅ Serializer created user: {user}")
        user.delete()  # cleanup
    else:
        print(f"❌ Serializer errors: {serializer.errors}")
except Exception as e:
    print(f"❌ ERROR with serializer: {e}")
    import traceback
    traceback.print_exc()

print("\nDiagnostic complete!")