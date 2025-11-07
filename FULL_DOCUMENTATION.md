# S3Cleaner Documentation

## Overview

S3Cleaner is an enterprise-grade Flask REST API service designed for automated AWS S3 bucket lifecycle management. The service provides programmatic interfaces for listing, deleting, and batch-cleaning S3 objects with configurable retention policies and file type filtering.

### Core Capabilities
- **Object Enumeration**: Paginated listing of bucket contents with continuation token handling
- **Selective Deletion**: Granular object removal by key
- **Policy-Based Cleaning**: Automated deletion of objects based on age (>90 days) and file extension patterns
- **Batch Operations**: Optimized bulk deletions (up to 1000 objects per request)
- **Audit Logging**: Comprehensive activity tracking to `s3_cleaner_activity.log`

---

## Architecture

### Component Structure

```
S3Cleaner/
├── app/
│   ├── main.py           # Application entry point and Flask initialization
│   └── s3_cleaner.py     # API blueprint and S3 operations implementation
├── requirements.txt      # Python dependency manifest
└── .github/
    └── copilot-instructions.md  # AI agent development guidelines
```

### System Design

**`app/main.py`**
- Initializes Flask application instance
- Registers the S3 blueprint under `/api` prefix
- Provides health check endpoint at root (`/`)
- Configures development server with debug mode

**`app/s3_cleaner.py`**
- Implements Flask Blueprint (`s3_bp`) for API routing
- Defines S3 client factory with retry logic and timeout configuration
- Exposes three REST endpoints: `/list`, `/delete`, `/clean`
- Handles boto3 error exceptions and logging infrastructure

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | Latest | Web framework for REST API |
| boto3 | Latest | AWS SDK for S3 operations |

---

## Installation & Configuration

### Prerequisites
- Python 3.7+
- AWS account with S3 access
- IAM credentials with appropriate S3 permissions

### Installation Steps

1. Clone repository and navigate to project directory:
   ```bash
   git clone https://github.com/zaidku/s3cleaner.git
   cd s3cleaner
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials via environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID="<access_key>"
   export AWS_SECRET_ACCESS_KEY="<secret_key>"
   export AWS_REGION="<region>"
   ```

   **Windows (PowerShell):**
   ```powershell
   $env:AWS_ACCESS_KEY_ID="<access_key>"
   $env:AWS_SECRET_ACCESS_KEY="<secret_key>"
   $env:AWS_REGION="<region>"
   ```

### AWS IAM Permissions

Minimum required IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::bucket-name",
        "arn:aws:s3:::bucket-name/*"
      ]
    }
  ]
}
```

---

## Running the Service

### Development Mode

```bash
python app/main.py
```

Service starts on `http://127.0.0.1:5000` with debug mode enabled.

### Production Deployment

Use a production WSGI server (e.g., Gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

**Configuration recommendations:**
- Workers: `2-4 × CPU_CORES`
- Timeout: `120s` for large bucket operations
- Bind: Internal network interface or reverse proxy

---

## API Reference

### Base URL
```
http://<host>:<port>/api
```

### Endpoints

#### 1. List Objects

**Endpoint:** `GET /api/list`

**Description:** Retrieves all object keys from a specified S3 bucket. Automatically handles pagination using continuation tokens.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bucket` | string | Yes | S3 bucket name |

**Request Example:**
```bash
curl "http://localhost:5000/api/list?bucket=my-bucket"
```

**Response:**
```json
{
  "objects": [
    "file1.txt",
    "folder/file2.jpg",
    "archive/backup.zip"
  ]
}
```

**Status Codes:**
- `200 OK`: Successful retrieval
- `400 Bad Request`: Missing bucket parameter
- `500 Internal Server Error`: AWS operation failed

---

#### 2. Delete Object

**Endpoint:** `POST /api/delete`

**Description:** Deletes a single object from an S3 bucket by key.

**Request Body:**
```json
{
  "bucket": "my-bucket",
  "key": "path/to/object.txt"
}
```

**Request Example:**
```bash
curl -X POST http://localhost:5000/api/delete \
  -H "Content-Type: application/json" \
  -d '{"bucket": "my-bucket", "key": "old-file.txt"}'
```

**Response:**
```json
{
  "message": "Deleted old-file.txt from my-bucket"
}
```

**Status Codes:**
- `200 OK`: Object deleted successfully
- `400 Bad Request`: Missing bucket or key parameter
- `500 Internal Server Error`: Deletion failed

---

#### 3. Clean Bucket

**Endpoint:** `POST /api/clean`

**Description:** Executes policy-based deletion of objects matching file extension criteria and age threshold (>90 days). Processes deletions in batches of up to 1000 objects per request.

**Request Body:**
```json
{
  "bucket": "my-bucket",
  "prefix": "uploads/"
}
```

**Cleaning Policy:**
- **Age threshold:** Objects older than 90 days
- **Supported extensions:** `.stl`, `.ply`, `.obj`, `.dcm`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`, `.heic`, `.ico`, `.jfif`, `.raw`, `.cr2`, `.nef`, `.orf`, `.sr2`

**Request Example:**
```bash
curl -X POST http://localhost:5000/api/clean \
  -H "Content-Type: application/json" \
  -d '{"bucket": "my-bucket", "prefix": "backups/"}'
```

**Response:**
```json
{
  "message": "Cleaned 1523 objects from my-bucket"
}
```

**Status Codes:**
- `200 OK`: Cleaning operation completed
- `400 Bad Request`: Missing bucket parameter
- `500 Internal Server Error`: Operation failed

**Performance Characteristics:**
- Batch size: 1000 objects (AWS S3 API limit)
- Pagination: Automatic continuation token handling
- Time complexity: O(n) where n = total objects in bucket/prefix

---

## Logging & Monitoring

### Log Files

**`s3_cleaner_activity.log`**
- Location: Project root directory
- Format: `%(asctime)s %(levelname)s %(name)s %(message)s`
- Rotation: Not configured (manual management required)

**Log Events:**
- Object listing operations and counts
- Individual deletions with bucket/key details
- Batch deletion results
- Error stack traces with AWS exception details

### Console Output

Flask development server logs include:
- HTTP request/response details
- Uncaught exceptions
- Server startup/shutdown events

---

## Error Handling

### Exception Management

All S3 operations implement try/except blocks for:
- `ClientError`: AWS service-side errors (permissions, bucket not found, etc.)
- `BotoCoreError`: Client-side SDK errors (network timeouts, configuration issues)

### Retry Configuration

S3 client configured with boto3 `Config`:
```python
Config(
    retries={'max_attempts': 5, 'mode': 'standard'},
    connect_timeout=10,
    read_timeout=30
)
```

**Retry behavior:**
- Max attempts: 5
- Backoff: Exponential with jitter (AWS SDK default)
- Retryable errors: Transient network failures, throttling (429), server errors (5xx)

---

## Development Guide

### Adding New Endpoints

1. Define route in `app/s3_cleaner.py`:
   ```python
   @s3_bp.route('/endpoint', methods=['POST'])
   def new_endpoint():
       data = request.get_json()
       s3 = get_s3_client()
       # Implementation
       return jsonify({'result': 'success'}), 200
   ```

2. Use `get_s3_client()` for S3 access
3. Return JSON responses with appropriate status codes
4. Wrap operations in try/except blocks

### Code Conventions

- **Error handling:** Always catch `ClientError` and `BotoCoreError`
- **Logging:** Use module logger (`logging.getLogger('s3_cleaner')`)
- **Response format:** JSON with `message` or `error` keys
- **HTTP status codes:** 200 (success), 400 (client error), 500 (server error)

### Testing

**Manual Testing:**
```bash
# List objects
curl "http://localhost:5000/api/list?bucket=test-bucket"

# Delete object
curl -X POST http://localhost:5000/api/delete \
  -H "Content-Type: application/json" \
  -d '{"bucket": "test-bucket", "key": "test.txt"}'

# Clean bucket
curl -X POST http://localhost:5000/api/clean \
  -H "Content-Type: application/json" \
  -d '{"bucket": "test-bucket", "prefix": "old/"}'
```

**Unit Testing:** Not currently implemented. Consider adding `pytest` with `moto` for S3 mocking.

---

## Security Considerations

### Credential Management

- **Environment variables:** Required for AWS credentials (never hardcode)
- **IAM roles:** Preferred for EC2/ECS deployments (avoids credential management)
- **Secrets management:** Use AWS Secrets Manager or HashiCorp Vault for production

### API Security

**Current implementation has no authentication.** For production:
- Implement API key validation
- Add JWT-based authentication
- Use AWS API Gateway with IAM authorization
- Enable HTTPS/TLS termination

### Network Security

- Deploy behind reverse proxy (nginx, ALB)
- Restrict access via security groups/firewall rules
- Use VPC endpoints for S3 access (avoid public internet)

---

## Performance Optimization

### Batch Operations

- Clean endpoint processes deletions in 1000-object batches (S3 API limit)
- Reduces API calls and improves throughput

### Pagination Handling

- List operations automatically handle continuation tokens
- No memory limitations for large buckets (streaming approach)

### Connection Pooling

boto3 automatically manages HTTP connection pooling via `urllib3`.

---

## Troubleshooting

### Common Issues

**Issue:** `AccessDenied` errors
- **Solution:** Verify IAM permissions and bucket policies

**Issue:** Timeout on large bucket operations
- **Solution:** Increase `read_timeout` in `get_s3_client()` configuration

**Issue:** Objects not deleted during clean operation
- **Solution:** Verify objects meet age (>90 days) and extension criteria

### Debug Steps

1. Check environment variables: `echo $AWS_ACCESS_KEY_ID`
2. Review `s3_cleaner_activity.log` for detailed error messages
3. Enable Flask debug mode: `app.run(debug=True)`
4. Test AWS credentials: `aws s3 ls s3://bucket-name`

---

## Deployment Architectures

### Standalone Server

```
[Client] → [S3Cleaner Flask App] → [AWS S3]
```

### Production (Recommended)

```
[Client] → [ALB/nginx] → [Gunicorn] → [S3Cleaner Flask App] → [AWS S3]
                                ↓
                          [CloudWatch Logs]
```

---

## Compliance & Auditing

### Audit Trail

All deletion operations logged to `s3_cleaner_activity.log` with:
- Timestamp (ISO 8601)
- Bucket name
- Object key
- Operation result

### Data Retention

Service does not store S3 object data. All operations are pass-through to AWS S3.

---

## Roadmap & Future Enhancements

- [ ] Authentication/authorization layer
- [ ] Configurable retention policies (API parameter)
- [ ] Regex-based object filtering
- [ ] Dry-run mode for clean operations
- [ ] Prometheus metrics export
- [ ] Unit test coverage with `pytest` + `moto`
- [ ] Docker containerization
- [ ] Helm chart for Kubernetes deployment

---

## License

MIT License - See LICENSE file for details

---

## Support & Contributing

### Reporting Issues

Submit issues via GitHub: https://github.com/zaidku/s3cleaner/issues

### Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/enhancement`
3. Commit changes: `git commit -m 'Add enhancement'`
4. Push to branch: `git push origin feature/enhancement`
5. Submit pull request

---

## Appendix

### S3 Client Configuration Reference

```python
boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    config=Config(
        retries={'max_attempts': 5, 'mode': 'standard'},
        connect_timeout=10,
        read_timeout=30
    )
)
```

### Supported File Extensions (Clean Endpoint)

3D Models: `.stl`, `.ply`, `.obj`  
Medical: `.dcm`  
Documents: `.pdf`  
Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`, `.heic`, `.ico`, `.jfif`, `.raw`, `.cr2`, `.nef`, `.orf`, `.sr2`

---

**Document Version:** 1.0  
**Last Updated:** November 7, 2025  
**Maintained By:** Zaid Kuba
