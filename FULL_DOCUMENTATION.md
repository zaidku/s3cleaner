# S3Cleaner

A Flask-based REST API for managing AWS S3 buckets. Provides endpoints to list, delete, and batch-clean objects using boto3. Designed for automation and bulk operations, with file type and age-based cleaning.

## Features
- List all objects in a bucket (with pagination)
- Delete individual objects
- Clean objects by file extension and age (>90 days)
- Batch deletes (up to 1000 objects/request)
- Activity logging to `s3_cleaner_activity.log`

## Architecture
- `app/main.py`: Flask app entry point. Registers API blueprint and runs the service.
- `app/s3_cleaner.py`: Implements all API endpoints and S3 logic. Uses a blueprint (`s3_bp`) for `/api` routes.
- `requirements.txt`: Python dependencies (`Flask`, `boto3`).
- `.github/copilot-instructions.md`: AI agent guidance and conventions.

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

## API Endpoints
### List Objects
- `GET /api/list?bucket=<bucket>`
- Response: `{ "objects": [ ... ] }`

### Delete Object
- `POST /api/delete`
- Body: `{ "bucket": "...", "key": "..." }`
- Response: `{ "message": "Deleted ..." }`

### Clean Bucket
- `POST /api/clean`
- Body: `{ "bucket": "...", "prefix": "..." }`
- Deletes objects by extension and age (>90 days)
- Response: `{ "message": "Cleaned ... objects" }`

## Logging
- All cleaning activity is logged to `s3_cleaner_activity.log`.
- Errors and info also appear in Flask console output.

## Development Patterns
- S3 operations use try/except for error handling.
- Batch deletes limited to 1000 objects/request (S3 API limit).
- Cleaning targets specific file extensions and objects older than 90 days.
- Logging uses a file handler for persistent tracking.

## Extending
- Add new endpoints in `app/s3_cleaner.py` using `@s3_bp.route`.
- Use `get_s3_client()` for S3 access.
- Return JSON responses and handle errors consistently.

## Testing & Debugging
- No test suite present; use API calls for manual testing.
- Check `s3_cleaner_activity.log` and Flask console for debugging.

## Security & Deployment
- Credentials must be set via environment variables.
- For production, use a WSGI server (e.g., gunicorn) and secure credentials.

## License
MIT

## Contributing
Pull requests welcome. For major changes, open an issue first to discuss.

## Maintainer
Zaid Kuba
