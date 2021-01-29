import boto3
### Twitter API Keys

client_key = 'XXXXXXXXXXXXXXXXX'
client_secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

### AWS Keys
client = boto3.client(
    's3',
    # Hard coded strings as credentials, not recommended.

    aws_access_key_id='XXXXXXXXXXXXXXXX',
    aws_secret_access_key='XXXXXXXXXXXXXXXXXXXXXX'
)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', aws_access_key_id='XXXXXXXXX', aws_secret_access_key='XXXXXXXXXXXXXXXXX')

table = dynamodb.Table('table_name')

translate = boto3.client(service_name='translate', region_name='us-west-2', use_ssl=True)