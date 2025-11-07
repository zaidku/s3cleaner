# S3Cleaner

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)](https://flask.palletsprojects.com/)
[![AWS](https://img.shields.io/badge/AWS-S3-orange.svg)](https://aws.amazon.com/s3/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Enterprise-grade REST API for automated AWS S3 bucket lifecycle management. Built for production workloads requiring policy-based object retention, batch operations, and comprehensive audit logging.

---

## 🚀 Features

- **Smart Object Enumeration** - Paginated listing with automatic continuation token handling
- **Selective Deletion** - Granular control for single-object removal
- **Policy-Based Cleaning** - Automated deletion based on age (>90 days) and file type patterns
- **Batch Operations** - Optimized bulk deletions (up to 1000 objects/request)
- **Audit Logging** - Complete activity tracking to `s3_cleaner_activity.log`
- **Production Ready** - Retry logic, timeout handling, and error management

---

## 📋 Quick Start

### Prerequisites
- Python 3.7+
- AWS account with S3 access
- IAM credentials with S3 permissions (`ListBucket`, `DeleteObject`)

### Installation

```bash
# Clone repository
git clone https://github.com/zaidku/s3cleaner.git
cd s3cleaner

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-east-1"
```

### Run Development Server

```bash
python app/main.py
```

Service available at `http://127.0.0.1:5000`

---

## 🔌 API Endpoints

### List Objects
```bash
GET /api/list?bucket=my-bucket
```

**Response:**
```json
{
  "objects": ["file1.txt", "folder/file2.jpg", "archive/backup.zip"]
}
```

### Delete Object
```bash
POST /api/delete
Content-Type: application/json

{
  "bucket": "my-bucket",
  "key": "path/to/object.txt"
}
```

**Response:**
```json
{
  "message": "Deleted path/to/object.txt from my-bucket"
}
```

### Clean Bucket
```bash
POST /api/clean
Content-Type: application/json

{
  "bucket": "my-bucket",
  "prefix": "uploads/"
}
```

**Cleaning Policy:**
- Deletes objects older than **90 days**
- Targets specific file types: `.stl`, `.ply`, `.obj`, `.dcm`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`, `.heic`, `.ico`, `.jfif`, `.raw`, `.cr2`, `.nef`, `.orf`, `.sr2`

**Response:**
```json
{
  "message": "Cleaned 1523 objects from my-bucket"
}
```

---

## 🏗️ Architecture

```
S3Cleaner/
├── app/
│   ├── main.py           # Flask application entry point
│   └── s3_cleaner.py     # API blueprint and S3 operations
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── FULL_DOCUMENTATION.md # Complete technical documentation
```

**Technology Stack:**
- **Flask** - Web framework for REST API
- **boto3** - AWS SDK for Python
- **botocore** - Low-level AWS service access

---

## 🔒 Security

### Credential Management
- Use environment variables (never hardcode credentials)
- For EC2/ECS: Use IAM roles instead of static credentials
- Production: AWS Secrets Manager or HashiCorp Vault

### IAM Policy (Minimum Required)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::bucket-name", "arn:aws:s3:::bucket-name/*"]
    }
  ]
}
```

### API Security
**⚠️ Current implementation has no authentication.** For production:
- Implement API key validation
- Add JWT-based authentication
- Deploy behind AWS API Gateway
- Enable HTTPS/TLS termination

---

## 🚢 Production Deployment

### Using Gunicorn (Recommended)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 app.main:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
```

### Architecture Pattern

```
[Client] → [ALB/nginx] → [Gunicorn] → [S3Cleaner Flask] → [AWS S3]
                              ↓
                       [CloudWatch Logs]
```

---

## 📊 Logging & Monitoring

### Log Files
- **Location:** `s3_cleaner_activity.log` (project root)
- **Format:** `%(asctime)s %(levelname)s %(name)s %(message)s`
- **Events:** Object listings, deletions, batch operations, errors

### Console Output
- HTTP request/response details
- Uncaught exceptions
- Server lifecycle events

---

## ⚙️ Configuration

### S3 Client Settings
```python
Config(
    retries={'max_attempts': 5, 'mode': 'standard'},
    connect_timeout=10,
    read_timeout=30
)
```

- **Max Retries:** 5 attempts with exponential backoff
- **Connection Timeout:** 10 seconds
- **Read Timeout:** 30 seconds

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# List objects
curl "http://localhost:5000/api/list?bucket=test-bucket"

# Delete object
curl -X POST http://localhost:5000/api/delete \
  -H "Content-Type: application/json" \
  -d '{"bucket":"test-bucket","key":"test.txt"}'

# Clean bucket
curl -X POST http://localhost:5000/api/clean \
  -H "Content-Type: application/json" \
  -d '{"bucket":"test-bucket","prefix":"old/"}'
```

### Unit Testing
Not currently implemented. Recommended: `pytest` + `moto` for S3 mocking.

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `AccessDenied` errors | Verify IAM permissions and bucket policies |
| Timeout on large buckets | Increase `read_timeout` in S3 client config |
| Objects not deleted | Verify objects meet age (>90 days) + extension criteria |
| Missing logs | Check write permissions for `s3_cleaner_activity.log` |

**Debug Steps:**
1. Verify environment variables: `echo $AWS_ACCESS_KEY_ID`
2. Review `s3_cleaner_activity.log` for detailed errors
3. Test AWS credentials: `aws s3 ls s3://bucket-name`
4. Enable Flask debug mode in `app/main.py`

---

## 📚 Documentation

- **[FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md)** - Complete technical reference
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI agent development guidelines

---

## 🗺️ Roadmap

- [ ] Authentication/authorization layer (API keys, JWT)
- [ ] Configurable retention policies via API parameters
- [ ] Regex-based object filtering
- [ ] Dry-run mode for clean operations
- [ ] Prometheus metrics export
- [ ] Unit test coverage (pytest + moto)
- [ ] Docker containerization
- [ ] Kubernetes Helm chart

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/enhancement`
3. Commit changes: `git commit -m 'Add enhancement'`
4. Push to branch: `git push origin feature/enhancement`
5. Submit pull request

**Guidelines:**
- Follow existing code conventions
- Add tests for new features
- Update documentation accordingly
- Ensure all tests pass before submitting

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🐛 Support

**Issues:** [GitHub Issues](https://github.com/zaidku/s3cleaner/issues)  
**Maintainer:** Zaid Kuba

---

## 🙏 Acknowledgments

Inspired by legacy S3 cleaning tools from the boto era. Modernized for enterprise use with boto3, Flask, and production-grade patterns.

---

**Built with ❤️ for reliable S3 lifecycle management**
