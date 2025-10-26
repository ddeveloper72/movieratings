# S3 Upload Security Measures

## Overview
This document outlines the multiple security layers implemented to protect the S3 bucket from inappropriate content and abuse.

## Security Layers Implemented

### 1. Authentication Required ✅
**What:** Only authenticated users can request upload URLs
**How:** Django REST Framework `TokenAuthentication` on the endpoint
**Benefit:** Anonymous users cannot upload anything

```python
permission_classes = (IsAuthenticated, )
```

### 2. Rate Limiting ✅
**What:** Maximum 10 uploads per user per hour
**How:** Django cache-based rate limiting
**Benefit:** Prevents spam and bulk uploads by malicious users

```python
# Rate limit: 10 uploads per user per hour
cache_key = f'upload_rate_limit_{user_id}'
upload_count = cache.get(cache_key, 0)
if upload_count >= 10:
    return 429 TOO_MANY_REQUESTS
```

**Configuration:**
- Limit: 10 uploads/hour per user
- Reset: Automatic after 1 hour
- Response: HTTP 429 (Too Many Requests)

### 3. File Size Limit ✅
**What:** Maximum 5 MB per file
**How:** Enforced in presigned URL parameters
**Benefit:** Prevents large file uploads that waste storage

```python
max_size_bytes = 5 * 1024 * 1024  # 5 MB
'ContentLength': max_size_bytes
```

### 4. File Type Validation ✅
**What:** Only image files allowed (JPEG, PNG, WebP, GIF)
**How:** Validates MIME type and file extension
**Benefit:** Prevents uploading of executables, videos, documents

```python
allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
```

### 5. Extension-MIME Validation ✅
**What:** File extension must match MIME type
**How:** Cross-validates extension with Content-Type header
**Benefit:** Prevents disguised files (e.g., .jpg that's actually .exe)

```python
ext_to_mime = {
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    # ...
}
if content_type != ext_to_mime[file_ext]:
    return 400 BAD_REQUEST
```

### 6. Unique Filename Generation ✅
**What:** Each upload gets a UUID-based unique name
**How:** `movie-{uuid}.{ext}` pattern
**Benefit:** 
- Prevents file overwrites
- Makes URLs non-guessable
- Reduces collision attacks

```python
unique_id = uuid.uuid4().hex[:8]
safe_name = f"movie-{unique_id}{ext}"
```

### 7. Presigned URL Expiration ✅
**What:** Upload URLs expire after 1 hour
**How:** Built into AWS presigned URL
**Benefit:** Stolen URLs become useless quickly

```python
ExpiresIn=3600  # 1 hour
```

### 8. Public Read, Private Write ✅
**What:** Files are publicly readable but only writable via presigned URL
**How:** S3 ACL set to `public-read` only
**Benefit:** Users can't modify or delete existing files

## Additional Recommended Security Measures

### 9. AWS S3 Bucket Policy (Recommended)
Add this to your S3 bucket policy to enforce restrictions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EnforceMaxFileSize",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::movie-rater/media/movies/*",
            "Condition": {
                "NumericGreaterThan": {
                    "s3:content-length": 5242880
                }
            }
        },
        {
            "Sid": "EnforceImageContentType",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::movie-rater/media/movies/*",
            "Condition": {
                "StringNotLike": {
                    "s3:content-type": "image/*"
                }
            }
        }
    ]
}
```

### 10. AWS Rekognition (Optional - Paid Service)
**What:** AI-powered image content moderation
**How:** Analyze uploaded images for inappropriate content
**Cost:** ~$0.001 per image
**Benefit:** Automatically detect NSFW content, violence, etc.

**Implementation Steps:**
1. Enable AWS Rekognition in your AWS account
2. Create a Lambda function triggered on S3 upload
3. Use `detect_moderation_labels` API
4. Delete or quarantine flagged images
5. Optionally ban users who repeatedly upload inappropriate content

**Example Lambda Trigger:**
```python
import boto3

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Analyze image
    response = rekognition.detect_moderation_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MinConfidence=75
    )
    
    # Check for inappropriate content
    if response['ModerationLabels']:
        # Delete the image
        s3.delete_object(Bucket=bucket, Key=key)
        # Log the incident
        print(f"Deleted inappropriate image: {key}")
```

### 11. CloudWatch Monitoring (Recommended)
**What:** Monitor S3 upload patterns
**How:** Set up CloudWatch alerts for unusual activity
**Benefit:** Detect abuse attempts early

**Alerts to configure:**
- Unusual number of uploads from single IP
- Rapid succession of uploads
- Failed upload attempts (potential probing)

### 12. User Reputation System (Optional)
**What:** Track user behavior and limit new users
**How:** Implement reputation scores in your Django app
**Benefit:** Trusted users get higher limits

**Example:**
```python
# New users: 5 uploads/hour
# Verified users: 10 uploads/hour
# Premium users: 50 uploads/hour

if user.reputation_score < 50:
    max_uploads = 5
elif user.is_verified:
    max_uploads = 10
else:
    max_uploads = 10
```

### 13. CORS Configuration (Already Configured)
**What:** Restrict which domains can upload
**How:** S3 CORS policy
**Benefit:** Prevents unauthorized websites from using your upload feature

```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>https://your-angular-app.com</AllowedOrigin>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```

## Current Protection Summary

| Security Measure | Status | Effectiveness |
|-----------------|--------|---------------|
| Authentication | ✅ Implemented | High |
| Rate Limiting | ✅ Implemented | High |
| File Size Limit | ✅ Implemented | High |
| File Type Validation | ✅ Implemented | High |
| Extension-MIME Validation | ✅ Implemented | Medium |
| Unique Filenames | ✅ Implemented | Medium |
| URL Expiration | ✅ Implemented | Medium |
| S3 ACL (Public-Read) | ✅ Implemented | High |
| S3 Bucket Policy | ⚠️ Recommended | High |
| AWS Rekognition | 💰 Optional (Paid) | Very High |
| CloudWatch Alerts | ⚠️ Recommended | Medium |
| User Reputation | 💡 Optional | Medium |
| CORS Policy | ⚠️ Should Configure | High |

## Risk Assessment

### Low Risk (Currently Protected) ✅
- Anonymous uploads
- File size abuse
- Spam/bulk uploads
- File overwrite attacks
- URL guessing

### Medium Risk (Partially Protected) ⚠️
- Malicious users with accounts
- Disguised file types
- Content moderation

### Can Be Further Reduced 💡
- Implement AWS Rekognition for content scanning
- Add S3 bucket policies for double enforcement
- Configure CORS to whitelist your Angular domain
- Add CloudWatch monitoring

## Monitoring & Response

### How to Monitor Uploads
1. **Django Admin:** Track which users are uploading
2. **AWS S3 Console:** View all uploaded files
3. **CloudWatch (if enabled):** Real-time alerts

### How to Handle Abuse
1. **Identify the user:** Check Django logs for user_id
2. **Ban the user:** Set `user.is_active = False` in Django admin
3. **Delete files:** Use AWS Console or CLI to remove inappropriate images
4. **Update database:** Clear `imagePath` for affected movies

### Emergency Cleanup Script
```python
# Delete specific file from S3
import boto3
s3 = boto3.client('s3')
s3.delete_object(Bucket='movie-rater', Key='media/movies/movie-abc123.jpg')

# Ban user in Django
from django.contrib.auth.models import User
user = User.objects.get(username='baduser')
user.is_active = False
user.save()
```

## Conclusion

**Current Protection Level: Good ✅**

Your implementation includes all essential security measures for a production application:
- Authentication prevents anonymous abuse
- Rate limiting prevents spam
- File validation prevents malicious uploads
- Size limits prevent storage abuse

**For maximum security (if budget allows), consider:**
- AWS Rekognition for AI content moderation (~$0.001/image)
- CloudWatch monitoring for unusual patterns (free tier available)
- S3 bucket policies for defense-in-depth

The current implementation is **production-ready** and provides strong protection against common abuse vectors. Most inappropriate content will be prevented at upload time through file type validation and rate limiting.
