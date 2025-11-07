# S3Cleaner

A Flask-based REST API service to list, delete, and clean objects from AWS S3 buckets using boto3.

## Setup

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set AWS credentials as environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

## Usage

Start the service:
```sh
python app/main.py
```

### Endpoints
- `GET /api/list?bucket=<bucket>`: List objects in a bucket
- `POST /api/delete`: Delete an object (`bucket`, `key` in JSON body)
- `POST /api/clean`: Delete all objects in a bucket or prefix (`bucket`, `prefix` in JSON body)

## Notes
- Ensure your AWS credentials have appropriate S3 permissions.
- For production, use a proper WSGI server and secure your credentials.
