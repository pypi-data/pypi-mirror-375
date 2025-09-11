import boto3
from datetime import datetime
import pandas as pd
import io

def upload_parquet_to_s3(aws_access_key_id, aws_secret_access_key, bucket_name):

    current_dttm = datetime.now()
    current_dttm_str = current_dttm.strftime('%Y-%m-%dT%H.%M.%S')
    df = pd.DataFrame([{'current_dttm': current_dttm, 'current_dttm_str': current_dttm_str}])
    file_path = f'{current_dttm_str}.parquet'

    buffer = io.BytesIO()
    df.to_parquet(buffer, engine='pyarrow')
    buffer.seek(0)

    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    s3.upload_fileobj(buffer, Bucket=bucket_name, Key=file_path)

    return True