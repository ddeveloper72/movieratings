#!/bin/bash

# Movie Rater Backend Diagnostic Script
# Run this script to quickly diagnose the Heroku backend issues

echo "🔬 Movie Rater Backend Quick Diagnostic"
echo "========================================"
echo ""

# Check if Heroku CLI is available
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first."
    echo "   Download from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

APP_NAME="ddeveloper72-movie-rater-api"

echo "📡 Checking app status..."
heroku ps -a $APP_NAME

echo ""
echo "🗄️ Checking database status..."
heroku pg:info -a $APP_NAME

echo ""
echo "📜 Checking recent logs (last 100 lines)..."
echo "Looking for errors related to /api/users/ and /auth/ endpoints..."
heroku logs --tail --num=100 -a $APP_NAME | grep -E "(ERROR|500|api/users|auth/|Exception|Traceback)" || echo "No obvious errors found in recent logs"

echo ""
echo "🔄 Checking migration status..."
heroku run python manage.py showmigrations -a $APP_NAME

echo ""
echo "📊 Checking config variables..."
heroku config -a $APP_NAME | grep -E "(DATABASE_URL|SECRET_KEY|DEBUG)" || echo "Key config variables not visible"

echo ""
echo "🧪 Testing basic Django shell access..."
echo "If this fails, there's a fundamental Django issue..."
heroku run python manage.py shell -a $APP_NAME << EOF
print("✅ Django shell access working")
try:
    from django.contrib.auth.models import User
    print(f"✅ User model import successful")
    user_count = User.objects.count()
    print(f"✅ Database query successful: {user_count} users found")
except Exception as e:
    print(f"❌ Error with User model: {e}")

try:
    from api.models import *
    print("✅ API models import successful")
except Exception as e:
    print(f"❌ Error importing API models: {e}")

try:
    from api.serializers import *
    print("✅ API serializers import successful")
except Exception as e:
    print(f"❌ Error importing API serializers: {e}")

exit()
EOF

echo ""
echo "📋 SUMMARY"
echo "=========="
echo "1. Check the logs above for any ERROR messages"
echo "2. If migration issues found, run: heroku run python manage.py migrate -a $APP_NAME"
echo "3. If import errors found, check your requirements.txt and redeploy"
echo "4. If database errors found, check DATABASE_URL configuration"
echo ""
echo "💡 Next steps:"
echo "   - Review the full diagnostic report: FRONTEND_DIAGNOSTIC_REPORT.md"
echo "   - Use quick fix commands: QUICK_FIX_COMMANDS.md"
echo "   - Test frontend after fixes: https://angular-movie-rater.web.app"