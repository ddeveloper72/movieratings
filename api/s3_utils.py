"""
S3 utilities for generating presigned upload URLs
"""
import os
import boto3
from botocore.exceptions import ClientError


def generate_presigned_upload_url(file_name, file_type='image/jpeg', expiration=3600, max_size_mb=5, file_hash=None):
    """
    Generate a presigned S3 URL for direct file upload from frontend.
    
    Args:
        file_name: Original filename from frontend (will be sanitized)
        file_type: MIME type of the file (default: image/jpeg)
        expiration: URL expiration time in seconds (default: 1 hour)
        max_size_mb: Maximum file size in MB (default: 5 MB)
        file_hash: Optional SHA256 hash of file content for deduplication
    
    Returns:
        dict with 'url' (presigned URL), 'key' (S3 object key), and 'public_url' (final image URL)
    """
    # Get AWS credentials from environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = 'movie-rater'
    region = 'eu-west-1'  # Change if your bucket is in a different region
    
    if not (aws_access_key and aws_secret_key):
        raise ValueError("AWS credentials not configured")
    
    # Sanitize filename and create S3 key
    import uuid
    from pathlib import Path
    
    # Generate filename based on content hash (for deduplication) or UUID (for uniqueness)
    ext = Path(file_name).suffix or '.jpg'
    
    if file_hash:
        # Use hash-based filename for automatic deduplication
        # Same image = same hash = same filename = overwrites duplicate
        safe_name = f"movie-{file_hash[:16]}{ext}"
    else:
        # Fall back to UUID for unique filenames (legacy behavior)
        unique_id = uuid.uuid4().hex[:8]
        safe_name = f"movie-{unique_id}{ext}"
    
    s3_key = f"media/movies/{safe_name}"
    
    # Calculate max size in bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        # Generate presigned POST URL with size limit
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key,
                'ContentType': file_type,
                'ACL': 'public-read',  # Make uploaded images publicly readable
                'ContentLength': max_size_bytes  # Enforce max file size
            },
            ExpiresIn=expiration
        )
        
        # Construct the public URL that will be accessible after upload
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        
        return {
            'upload_url': response,
            'key': s3_key,
            'public_url': public_url,
            'method': 'PUT',
            'headers': {
                'Content-Type': file_type,
                'x-amz-acl': 'public-read',
                'Content-Length': str(max_size_bytes)
            }
        }
        
    except ClientError as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")
