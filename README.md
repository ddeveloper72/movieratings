# 🎬 Movie Rater API

[![Django](https://img.shields.io/badge/Django-5.1.13-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.15.2-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![AWS S3](https://img.shields.io/badge/AWS-S3-orange.svg)](https://aws.amazon.com/s3/)
[![Azure SQL](https://img.shields.io/badge/Azure-SQL%20Database-blue.svg)](https://azure.microsoft.com/en-us/products/azure-sql/database/)

**Live Application:** [https://ddeveloper72-movie-rater-api.herokuapp.com/](https://ddeveloper72-movie-rater-api.herokuapp.com/)

## 📖 Overview

Movie Rater API is a production-ready Django REST Framework application that provides a complete backend service for movie rating and review platforms. Built with modern cloud infrastructure, it serves as the backend API for an Angular 10 frontend application, handling user authentication, movie data management, rating systems, and cloud-based image storage.

### 🎯 Purpose

This API enables developers to build movie rating applications with features like:
- **User Management** - Token-based authentication for secure API access
- **Movie Database** - CRUD operations for movie information with image support
- **Rating System** - User-generated ratings with automatic average calculation
- **Cloud Storage** - AWS S3 integration for movie poster/cover image uploads
- **Admin Portal** - Custom Django admin interface accessible via frontend

### 🏗️ Architecture

- **Backend Framework:** Django 5.1.13 with Django REST Framework 3.15.2
- **Database (Production):** Azure SQL Database
- **Database (Development):** SQLite3
- **Image Storage:** AWS S3 with presigned URL upload
- **Static Files:** WhiteNoise for static file serving
- **Deployment:** Heroku with automatic GitHub deployment
- **Authentication:** Token-based authentication via DRF

## ✨ Key Features

### 1. **Secure Image Upload to AWS S3**
- Direct frontend-to-S3 uploads using presigned URLs
- 8-layer security system (authentication, rate limiting, file validation)
- Zero-cost deduplication using content-based hashing
- Support for JPEG, PNG, WebP, and GIF formats
- 5 MB file size limit with automatic enforcement

### 2. **RESTful API Design**
- Complete CRUD operations for movies, users, and ratings
- Token-based authentication for all protected endpoints
- Comprehensive error handling and validation
- API browsable interface for development

### 3. **Intelligent Rating System**
- Per-user movie ratings (1-5 stars)
- Automatic average rating calculation
- Unique user-movie rating constraint (one rating per user per movie)
- Real-time rating updates

### 4. **Production-Ready Infrastructure**
- Azure SQL Database for scalable data storage
- WhiteNoise for efficient static file serving
- Environment-based configuration for dev/prod separation
- Comprehensive security measures

## 📚 Additional Documentation

- **[S3 Upload Integration Guide](S3_UPLOAD_GUIDE.md)** - Complete guide for frontend developers to implement image uploads
- **[Security Documentation](SECURITY.md)** - Detailed security measures and best practices


## 🚀 API Endpoints

### Authentication
- `POST /auth/` - Obtain authentication token
  ```json
  {"username": "user", "password": "pass"}
  ```

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Movies
- `GET /api/movies/` - List all movies
- `POST /api/movies/` - Create new movie (admin only)
- `GET /api/movies/{id}/` - Get movie details
- `PUT /api/movies/{id}/` - Update movie (admin only)
- `DELETE /api/movies/{id}/` - Delete movie (admin only)
- `POST /api/movies/{id}/rate_movie/` - Rate a movie (1-5 stars)
- `POST /api/movies/get_upload_url/` - Get presigned S3 URL for image upload

### Ratings
- `GET /api/ratings/` - List all ratings
- `GET /api/ratings/{id}/` - Get rating details

## 📊 Data Models

### Movie Model
```python
{
    "id": 1,
    "title": "The Shawshank Redemption",
    "description": "Two imprisoned men bond over years...",
    "imagePath": "https://movie-rater.s3.eu-west-1.amazonaws.com/media/movies/movie-abc123.jpg",
    "no_of_ratings": 3,
    "ave_ratings": 4.67
}
```

### Rating Model
```python
{
    "id": 1,
    "stars": 5,
    "user": 1,
    "movie": 1
}
```

### User Model
```python
{
    "id": 1,
    "username": "moviefan",
    "password": "***" // write-only
}
```

## 🔐 Authentication

This API uses **Token Authentication** for secure access:

1. **Obtain Token:**
   ```bash
   curl -X POST https://ddeveloper72-movie-rater-api.herokuapp.com/auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "youruser", "password": "yourpass"}'
   ```

2. **Use Token in Requests:**
   ```bash
   curl -X GET https://ddeveloper72-movie-rater-api.herokuapp.com/api/movies/ \
     -H "Authorization: Token your-token-here"
   ```

Tokens are automatically created when new users are registered.

## 🖼️ Image Upload Workflow

The API provides a secure, efficient workflow for uploading movie cover images:

1. **Frontend requests presigned URL:**
   ```typescript
   POST /api/movies/get_upload_url/
   {
     "filename": "poster.jpg",
     "contentType": "image/jpeg",
     "fileHash": "abc123..." // Optional for deduplication
   }
   ```

2. **Backend returns presigned URL:**
   ```json
   {
     "upload_url": "https://movie-rater.s3.amazonaws.com/...",
     "public_url": "https://movie-rater.s3.eu-west-1.amazonaws.com/media/movies/movie-abc123.jpg",
     "method": "PUT",
     "headers": {...}
   }
   ```

3. **Frontend uploads directly to S3:**
   ```typescript
   PUT <upload_url>
   Content-Type: image/jpeg
   Body: <file binary>
   ```

4. **Frontend updates movie record:**
   ```typescript
   PATCH /api/movies/{id}/
   {
     "imagePath": "<public_url>"
   }
   ```

See [S3_UPLOAD_GUIDE.md](S3_UPLOAD_GUIDE.md) for complete implementation details.

## 🛡️ Security Features

### 8-Layer Security System for Image Uploads:
1. ✅ **Authentication Required** - Token-based authentication
2. ✅ **Rate Limiting** - 10 uploads per user per hour
3. ✅ **File Size Limit** - 5 MB maximum
4. ✅ **File Type Validation** - Images only (JPEG, PNG, WebP, GIF)
5. ✅ **Extension-MIME Validation** - Prevents disguised files
6. ✅ **Unique Filename Generation** - UUID or hash-based
7. ✅ **Presigned URL Expiration** - 1 hour expiration
8. ✅ **Public-Read ACL** - Controlled access permissions

See [SECURITY.md](SECURITY.md) for detailed security documentation.


## 💻 Local Development Setup

### Prerequisites
- Python 3.11+
- pip and virtualenv
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ddeveloper72/movieratings.git
   cd movieratings
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the API:**
   - API Root: http://localhost:8000/api/
   - Admin Portal: http://localhost:8000/admin/

## 🧪 Testing

### Test Presigned URL Generation
```bash
python manage.py shell
```
```python
from api.s3_utils import generate_presigned_upload_url
url_data = generate_presigned_upload_url('test.jpg', 'image/jpeg')
print(url_data)
```

### Test API Endpoints
```bash
# Get authentication token
curl -X POST http://localhost:8000/auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'

# List movies
curl -X GET http://localhost:8000/api/movies/ \
  -H "Authorization: Token your-token-here"
```

## 📦 Technology Stack

### Backend
- **Django 5.1.13** - Web framework
- **Django REST Framework 3.15.2** - API framework
- **WhiteNoise 6.8.2** - Static file serving

### Database
- **Azure SQL Database** (Production)
- **SQLite3** (Development)
- **pyodbc 5.2.0** - Azure SQL driver

### Cloud Services
- **AWS S3** - Image storage
- **boto3 1.35.77** - AWS SDK for Python
- **botocore 1.35.77** - Low-level AWS interface

### Deployment
- **Heroku** - Platform as a Service
- **gunicorn 23.0.0** - WSGI HTTP Server
- **dj-database-url 2.3.0** - Database URL parsing

### Other
- **python-dotenv 1.0.1** - Environment variable management
- **requests 2.32.3** - HTTP library

## 🌐 Deployment

### Heroku Deployment

This project is configured for automatic deployment to Heroku:

1. **Prerequisites:**
   - Heroku account
   - Heroku CLI installed
   - Git repository connected to Heroku

2. **Environment Variables:**
   Set the following config vars in Heroku:
   ```bash
   heroku config:set SECRET_KEY=your-production-secret
   heroku config:set DEBUG=False
   heroku config:set AWS_ACCESS_KEY_ID=your-aws-key
   heroku config:set AWS_SECRET_ACCESS_KEY=your-aws-secret
   heroku config:set AZURE_SQL_HOST=your-azure-host
   heroku config:set AZURE_SQL_NAME=your-database
   heroku config:set AZURE_SQL_USER=your-username
   heroku config:set AZURE_SQL_PASSWORD=your-password
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

4. **Run migrations on Heroku:**
   ```bash
   heroku run python manage.py migrate
   ```

### Automatic Deployment
This repository is configured for automatic deployment from GitHub. Any push to the `main` branch triggers a deployment to Heroku.

## 📁 Project Structure

```
MovieRaterApi/
├── api/                      # Main API application
│   ├── models.py            # Movie, Rating models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API viewsets
│   ├── urls.py              # API URL routing
│   └── s3_utils.py          # S3 presigned URL utilities
├── home/                    # Home page application
│   ├── views.py            # Home view
│   └── templates/          # HTML templates
├── movierater/             # Project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
├── staticfiles/           # Collected static files
├── templates/             # Global templates
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── db.sqlite3            # SQLite database (development)
├── manage.py             # Django management script
├── Procfile              # Heroku process file
├── requirements.txt      # Python dependencies
├── runtime.txt           # Python version for Heroku
├── README.md             # This file
├── S3_UPLOAD_GUIDE.md   # S3 upload integration guide
└── SECURITY.md          # Security documentation
```

## 🔧 Admin Portal Integration

This API includes a custom admin portal that can be accessed through your Angular frontend:

```python
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(),
        {'template_name': 'core/login.html'}, name='login'),
    path('admin/logout/', include('home.urls')),
]
```

**Key Features:**
- Custom admin login accessible from frontend
- Seamless logout redirect to home page
- Maintains Django's admin functionality
- No need for separate admin interface

## 🎓 Learning Journey

This project evolved from a tutorial by Senior Full Stack Engineer **Krystian Czekalski**, with significant enhancements including:
- AWS S3 integration for cloud image storage
- Azure SQL Database for production data
- Advanced security implementation (8-layer security system)
- Zero-cost deduplication for image uploads
- Custom admin portal integration
- SVG sprite rendering solution via DOM injection
- Comprehensive API documentation

## 👨‍💻 Developer

**Duncan Falconer (ddeveloper72)**
- GitHub: [@ddeveloper72](https://github.com/ddeveloper72)
- Repository: [movieratings](https://github.com/ddeveloper72/movieratings)

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/ddeveloper72/movieratings/issues).

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

**Built with ❤️ using Django REST Framework**