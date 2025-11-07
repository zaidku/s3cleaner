from flask import Blueprint, request, jsonify
import boto3
import os
import logging
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config

s3_bp = Blueprint('s3', __name__)

# Helper to get S3 client

def get_s3_client():
    boto_config = Config(
        retries={
            'max_attempts': 5,
            'mode': 'standard'
        },
        connect_timeout=10,
        read_timeout=30
    )
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'),
        config=boto_config
    )

@s3_bp.route('/list', methods=['GET'])
def list_objects():
    bucket = request.args.get('bucket')
    if not bucket:
        return jsonify({'error': 'Bucket name required'}), 400
    s3 = get_s3_client()
    logger = logging.getLogger('s3_cleaner')
    try:
        continuation_token = None
        all_keys = []
        while True:
            if continuation_token:
                response = s3.list_objects_v2(Bucket=bucket, ContinuationToken=continuation_token)
            else:
                response = s3.list_objects_v2(Bucket=bucket)
            contents = response.get('Contents', [])
            all_keys.extend([obj['Key'] for obj in contents])
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
        logger.info(f"Listed {len(all_keys)} objects from {bucket}")
        return jsonify({'objects': all_keys})
    except (ClientError, BotoCoreError) as e:
        logger.error(f"Error listing objects in bucket {bucket}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@s3_bp.route('/delete', methods=['POST'])
def delete_object():
    data = request.get_json()
    bucket = data.get('bucket')
    key = data.get('key')
    if not bucket or not key:
        return jsonify({'error': 'Bucket and key required'}), 400
    s3 = get_s3_client()
    logger = logging.getLogger('s3_cleaner')
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        logger.info(f"Deleted {key} from {bucket}")
        return jsonify({'message': f'Deleted {key} from {bucket}'}), 200
    except (ClientError, BotoCoreError) as e:
        logger.error(f"Error deleting {key} from bucket {bucket}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@s3_bp.route('/clean', methods=['POST'])
def clean_bucket():
    import datetime
    data = request.get_json()
    bucket = data.get('bucket')
    prefix = data.get('prefix', '')
    if not bucket:
        return jsonify({'error': 'Bucket name required'}), 400
    s3 = get_s3_client()
    logger = logging.getLogger('s3_cleaner')
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        file_handler = logging.FileHandler('s3_cleaner_activity.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    try:
        now = datetime.datetime.utcnow()
        extensions = [
            '.stl', '.ply', '.obj', '.dcm', '.pdf',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.heic', '.ico', '.jfif', '.raw', '.cr2', '.nef', '.orf', '.sr2'
        ]
        to_delete = []
        continuation_token = None
        while True:
            try:
                if continuation_token:
                    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, ContinuationToken=continuation_token)
                else:
                    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            except (ClientError, BotoCoreError) as e:
                logger.error(f"Error listing objects for cleaning in bucket {bucket}: {str(e)}")
                break
            contents = response.get('Contents', [])
            for obj in contents:
                key = obj['Key'].lower()
                last_modified = obj.get('LastModified')
                if not last_modified:
                    continue
                if isinstance(last_modified, str):
                    last_modified = datetime.datetime.fromisoformat(last_modified)
                age_days = (now - last_modified.replace(tzinfo=None)).days
                if any(key.endswith(ext) for ext in extensions) and age_days > 90:
                    to_delete.append({'Key': obj['Key']})
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
        deleted = 0
        # Batch delete (max 1000 per request)
        for i in range(0, len(to_delete), 1000):
            batch = to_delete[i:i+1000]
            if batch:
                try:
                    result = s3.delete_objects(Bucket=bucket, Delete={'Objects': batch})
                    deleted += len(result.get('Deleted', []))
                    logger.info(f"Deleted {len(result.get('Deleted', []))} objects from {bucket}")
                except (ClientError, BotoCoreError) as e:
                    logger.error(f"Error batch deleting objects in bucket {bucket}: {str(e)}")
        logger.info(f"Total cleaned: {deleted} objects from {bucket}")
        return jsonify({'message': f'Cleaned {deleted} objects from {bucket}'}), 200
    except Exception as e:
        logger.error(f"Error cleaning bucket {bucket}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
