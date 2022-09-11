import boto3

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    try:
        client.put_item(
            TableName='chat-app-connection',
            Item= {
                'connection_id': {'S': event['requestContext']['connectionId']},
            }
        )
    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': 'Server error.'}
    
    return {'statusCode': 200, 'body': 'Connected.'}