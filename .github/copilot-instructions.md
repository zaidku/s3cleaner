
# Copilot Instructions for S3Cleaner

## Project Overview
S3Cleaner is a Flask REST API service for managing AWS S3 buckets. It provides endpoints to list, delete, and batch-clean objects using boto3. The service is intended for automation and bulk operations on S3, with a focus on file types and age-based cleaning.

## Architecture & Key Files
- `app/main.py`: Flask app entry point. Registers API blueprint and runs the service.
- `app/s3_cleaner.py`: Implements all API endpoints and S3 logic. Uses a blueprint (`s3_bp`) for `/api` routes.
- `requirements.txt`: Lists dependencies (`Flask`, `boto3`).
- `README.md`: Setup, environment variables, and endpoint documentation.

## API Endpoints
- `GET /api/list?bucket=<bucket>`: Lists all object keys in a bucket (handles pagination).
- `POST /api/delete`: Deletes a single object. Expects JSON `{ "bucket": ..., "key": ... }`.
- `POST /api/clean`: Deletes objects by file extension and age (>90 days). Expects JSON `{ "bucket": ..., "prefix": ... }`. Batch deletes up to 1000 objects per request.

## S3 Integration
- Uses environment variables for AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`).
- S3 client is configured with retry and timeout settings for reliability.
- Logging is set up for cleaning operations (`s3_cleaner_activity.log`).

## Developer Workflow
1. Install dependencies: `pip install -r requirements.txt`
2. Set AWS credentials as environment variables.
3. Run the service: `python app/main.py`
4. Use endpoints as described in `README.md`.

## Patterns & Conventions
- All S3 operations are wrapped in try/except blocks for error handling.
- Batch deletes are limited to 1000 objects/request (S3 API limit).
- Cleaning logic targets specific file extensions and objects older than 90 days.
- Logging uses a file handler for persistent activity tracking.

## Example: Adding a New Endpoint
- Define route in `app/s3_cleaner.py` using `@s3_bp.route`.
- Use `get_s3_client()` for S3 access.
- Return JSON responses and handle errors consistently.

## Testing & Debugging
- No test suite present; manual testing via API calls recommended.
- For debugging, check `s3_cleaner_activity.log` and Flask console output.

## External Dependencies
- Flask (web framework)
- boto3 (AWS SDK)

## Security & Deployment
- Credentials must be set via environment variables.
- For production, use a WSGI server (e.g., gunicorn) and secure credentials.

Refer to this file for project-specific guidance. Update as new patterns or workflows emerge.