# S3 Image Upload - Frontend Integration Guide

## Overview
This API provides a presigned URL endpoint that allows the Angular frontend to upload movie cover images directly to AWS S3, bypassing the Django backend for file transfer. This approach reduces server load and improves upload performance.

## Workflow

1. **Request a presigned URL** from Django API
2. **Upload the image** directly to S3 using the presigned URL
3. **Save the public URL** in the Movie record via the API

## API Endpoint

### POST `/api/movies/get_upload_url/`

Generate a presigned S3 URL for direct image upload.

**Authentication:** Required (Token Authentication)

**Request Headers:**
```
Authorization: Token <your-auth-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "filename": "my-movie-poster.jpg",
  "contentType": "image/jpeg",
  "fileHash": "abc123def456..."  // Optional: SHA256 hash for deduplication
}
```

**Parameters:**
- `filename` (required): The original filename of the image
- `contentType` (optional): MIME type of the image. Defaults to `image/jpeg`
  - Allowed types: `image/jpeg`, `image/jpg`, `image/png`, `image/webp`, `image/gif`
- `fileHash` (optional): SHA256 hash of the file content for automatic deduplication
  - If provided, identical images will use the same S3 filename (saves storage!)
  - If omitted, each upload gets a unique UUID-based filename

**Response (200 OK):**
```json
{
  "upload_url": "https://movie-rater.s3.amazonaws.com/media/movies/movie-abc123.jpg?...",
  "key": "media/movies/movie-abc123.jpg",
  "public_url": "https://movie-rater.s3.eu-west-1.amazonaws.com/media/movies/movie-abc123.jpg",
  "method": "PUT",
  "headers": {
    "Content-Type": "image/jpeg",
    "x-amz-acl": "public-read"
  },
  "max_size_mb": 5,
  "uploads_remaining": 9,
  "deduplicated": true
}
```

**Response Fields:**
- `upload_url`: Presigned URL to use for uploading (valid for 1 hour)
- `key`: S3 object key (path within the bucket)
- `public_url`: Final public URL to save in `Movie.imagePath` after upload
- `method`: HTTP method to use for upload (always "PUT")
- `headers`: Required headers for the S3 upload request
- `max_size_mb`: Maximum file size allowed (5 MB)
- `uploads_remaining`: How many uploads this user has left in the current hour
- `deduplicated`: If true, this filename is based on content hash (duplicate detection enabled)

**Error Responses:**
- `400 Bad Request`: Missing filename or invalid content type
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: S3 service error

## Angular Integration Example

### Service Method

```typescript
// movie.service.ts
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Md5 } from 'ts-md5';  // npm install ts-md5

export interface PresignedUrlResponse {
  upload_url: string;
  key: string;
  public_url: string;
  method: string;
  headers: {
    'Content-Type': string;
    'x-amz-acl': string;
  };
  max_size_mb: number;
  uploads_remaining: number;
  deduplicated: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class MovieService {
  private apiUrl = 'http://localhost:8000/api';  // or your production URL
  
  constructor(private http: HttpClient) {}

  // Helper: Calculate file hash for deduplication
  async calculateFileHash(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const buffer = reader.result as ArrayBuffer;
        const hash = Md5.hashAsciiStr(new TextDecoder().decode(buffer));
        resolve(hash as string);
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });
  }

  // Step 1: Get presigned URL from Django (with optional deduplication)
  getUploadUrl(filename: string, contentType: string = 'image/jpeg', fileHash?: string): Observable<PresignedUrlResponse> {
    const headers = new HttpHeaders({
      'Authorization': `Token ${this.getAuthToken()}`,
      'Content-Type': 'application/json'
    });
    
    const body: any = { filename, contentType };
    if (fileHash) {
      body.fileHash = fileHash;  // Enable deduplication
    }
    
    return this.http.post<PresignedUrlResponse>(
      `${this.apiUrl}/movies/get_upload_url/`,
      body,
      { headers }
    );
  }

  // Step 2: Upload file directly to S3
  uploadToS3(file: File, uploadUrl: string, contentType: string): Observable<any> {
    const headers = new HttpHeaders({
      'Content-Type': contentType,
      'x-amz-acl': 'public-read'
    });
    
    // Use PUT method as specified in the response
    return this.http.put(uploadUrl, file, { headers });
  }

  // Step 3: Update movie with the public URL
  updateMovie(movieId: number, imagePath: string): Observable<any> {
    const headers = new HttpHeaders({
      'Authorization': `Token ${this.getAuthToken()}`,
      'Content-Type': 'application/json'
    });
    
    return this.http.patch(
      `${this.apiUrl}/movies/${movieId}/`,
      { imagePath },
      { headers }
    );
  }

  private getAuthToken(): string {
    // Retrieve token from localStorage or your auth service
    return localStorage.getItem('auth_token') || '';
  }
}
```

### Component Usage

```typescript
// movie-form.component.ts
export class MovieFormComponent {
  isUploading = false;
  uploadProgress = 0;

  constructor(private movieService: MovieService) {}

  onFileSelected(event: any, movieId: number) {
    const file: File = event.target.files[0];
    
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
      alert('Invalid file type. Please upload a valid image.');
      return;
    }

    // Validate file size (e.g., max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      alert('File is too large. Maximum size is 5MB.');
      return;
    }

    this.uploadMovieImage(file, movieId);
  }

  async uploadMovieImage(file: File, movieId: number) {
    this.isUploading = true;

    try {
      // Optional: Calculate file hash for deduplication (zero-cost duplicate prevention)
      const fileHash = await this.movieService.calculateFileHash(file);
      
      // Step 1: Get presigned URL with deduplication
      const presignedData = await this.movieService
        .getUploadUrl(file.name, file.type, fileHash)  // Pass hash for deduplication
        .toPromise();

      console.log('Presigned URL obtained:', presignedData.public_url);
      if (presignedData.deduplicated) {
        console.log('Deduplication enabled - duplicate images will share storage');
      }

      // Step 2: Upload directly to S3
      await this.movieService
        .uploadToS3(file, presignedData.upload_url, file.type)
        .toPromise();

      console.log('File uploaded to S3 successfully');

      // Step 3: Update movie record with the public URL
      await this.movieService
        .updateMovie(movieId, presignedData.public_url)
        .toPromise();

      console.log('Movie updated with image URL');
      alert('Image uploaded successfully!');

    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload image. Please try again.');
    } finally {
      this.isUploading = false;
    }
  }
}
```

### HTML Template

```html
<!-- movie-form.component.html -->
<div class="image-upload">
  <label for="movie-image">Movie Poster:</label>
  <input
    type="file"
    id="movie-image"
    accept="image/jpeg,image/jpg,image/png,image/webp,image/gif"
    (change)="onFileSelected($event, movie.id)"
    [disabled]="isUploading"
  />
  
  <div *ngIf="isUploading" class="upload-status">
    <p>Uploading...</p>
    <div class="progress-bar">
      <div class="progress" [style.width.%]="uploadProgress"></div>
    </div>
  </div>
  
  <img *ngIf="movie.imagePath" [src]="movie.imagePath" alt="Movie poster" />
</div>
```

## Important Notes

## Image Deduplication (Zero-Cost Optimization)

**Problem:** Multiple users uploading the same movie poster wastes storage.

**Solution:** Content-based deduplication using file hashes.

### How It Works

1. **Frontend calculates SHA256 hash** of the file before uploading
2. **Backend generates filename** based on hash: `movie-abc123def456.jpg`
3. **Same image = same hash = same filename** → S3 automatically overwrites duplicate
4. **Result:** Only one copy stored, multiple movies can reference it

### Benefits

- ✅ **Zero cost** - No extra AWS services needed
- ✅ **Automatic** - S3 handles duplicates natively
- ✅ **Storage savings** - Popular movie posters stored once
- ✅ **Bandwidth savings** - If file exists, upload still works (overwrites with identical content)

### Example Scenario

```
User A uploads "titanic.jpg" (hash: abc123)
→ Stored as: s3://movie-rater/media/movies/movie-abc123.jpg

User B uploads same "titanic.jpg" (hash: abc123)
→ Stored as: s3://movie-rater/media/movies/movie-abc123.jpg (overwrites)
→ Result: Only 1 file in S3, both movies reference the same URL

User C uploads different "titanic_hd.jpg" (hash: def456)
→ Stored as: s3://movie-rater/media/movies/movie-def456.jpg
→ Result: 2 unique files stored
```

### Implementation Options

**Option 1: With Deduplication (Recommended)**
```typescript
const fileHash = await this.movieService.calculateFileHash(file);
const presignedData = await this.movieService
  .getUploadUrl(file.name, file.type, fileHash);
```

**Option 2: Without Deduplication (Unique Files)**
```typescript
const presignedData = await this.movieService
  .getUploadUrl(file.name, file.type);  // No hash = UUID-based filename
```

### When to Use Deduplication

**Use deduplication when:**
- ✅ Multiple users might upload the same image (movie posters)
- ✅ You want to save storage costs
- ✅ Images are publicly accessible (not user-private)

**Don't use deduplication when:**
- ❌ Images are user-private (personal photos)
- ❌ You need to track who uploaded what
- ❌ Different movies should never share images

## Important Notes

1. **Presigned URL Expiration**: The presigned URL is valid for 1 hour (3600 seconds). Ensure the upload completes within this time.

2. **File Naming**: The backend automatically generates a unique filename with a UUID prefix (e.g., `movie-abc12345.jpg`) to prevent conflicts.

3. **S3 Structure**: Images are stored in `s3://movie-rater/media/movies/`

4. **Public Access**: Uploaded images are automatically set to `public-read` ACL, making them accessible via the public URL.

5. **CORS Configuration**: Ensure your S3 bucket has CORS configured to allow uploads from your frontend domain.

6. **Error Handling**: Always implement proper error handling for all three steps (get URL, upload, update record).

7. **Security**: Never expose AWS credentials in the frontend. The presigned URL approach keeps credentials secure on the backend.

## Testing with cURL

You can test the endpoint manually:

```bash
# Get presigned URL
curl -X POST http://localhost:8000/api/movies/get_upload_url/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.jpg", "contentType": "image/jpeg"}'

# Upload file to S3 (use the upload_url from above)
curl -X PUT "PRESIGNED_URL_HERE" \
  -H "Content-Type: image/jpeg" \
  -H "x-amz-acl: public-read" \
  --data-binary "@/path/to/your/image.jpg"
```

## Troubleshooting

- **403 Forbidden on S3 upload**: Check that AWS credentials have `s3:PutObject` permission
- **CORS errors**: Verify S3 bucket CORS configuration allows your frontend origin
- **URL expired**: Generate a new presigned URL (they expire after 1 hour)
- **Invalid content type**: Ensure you're using one of the allowed image MIME types
