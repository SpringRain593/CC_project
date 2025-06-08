import boto3, os, uuid, logging
from datetime import timedelta

log = logging.getLogger("cloudfs.s3")
s3      = boto3.client("s3")
BUCKET  = os.getenv("S3_BUCKET")
EXP_SEC = 15 * 60

def presign_put(user_prefix: str, filename: str):
    key = f"{user_prefix}/{uuid.uuid4()}_{filename}"
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=EXP_SEC
    )
    return key, url

def presign_get(key: str):
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=EXP_SEC
    )

