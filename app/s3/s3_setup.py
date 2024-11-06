from .s3_manager import S3Manager
s3_manager = None
bucket_name=None

def init_s3_manager(app):
    global s3_manager, bucket_name
    s3_manager = S3Manager(app)
    bucket_name=app.config['bucket_name']


def get_s3_manager():
    global s3_manager
    if s3_manager is None:
        raise Exception("S3 Manager is not initialized")
    return s3_manager

def get_bucket_name():
    if bucket_name is None:
        raise Exception("Bucket name is not initialized")
    return bucket_name