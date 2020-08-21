AWS_ACCESS_KEY_ID='AKIATTFB6KG67WCPGP5A'
AWS_SECRET_ACCESS_KEY='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'
AWS_BUCKET_NAME = 'reconai-traffic'

import boto3
import pandas as pd

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)






dynamodb = boto3.client('dynamodb')

response = dynamodb.scan(
    TableName=your_table,
    Select='ALL_ATTRIBUTES')

data = response['Items']

while 'LastEvaluatedKey' in response:
    response = dynamodb.scan(
        TableName=your_table,
        Select='ALL_ATTRIBUTES',
        ExclusiveStartKey=response['LastEvaluatedKey'])

    data.extend(response['Items'])