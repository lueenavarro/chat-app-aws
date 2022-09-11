import json
import boto3

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    try:
        client.update_item(
            TableName='chat-app-connection',
            Key= {
                'connection_id': {'S': event['requestContext']['connectionId']}
            },
            UpdateExpression='SET room_id = :room_id, username = :username',
            ExpressionAttributeValues= {
                ':room_id': {'S': body['room_id']},
                ':username': {'S': body['username']}
            }
        )

        connections = client.query(
            TableName='chat-app-connection',
            IndexName='room-index',
            KeyConditions = {
                'room_id': {
                    'ComparisonOperator': "EQ",
                    "AttributeValueList": [ {"S": body['room_id']} ]
                }
            },
            AttributesToGet=['connection_id'],
        )

        apigw_client = boto3.client('apigatewaymanagementapi', 
                                    endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
                        )

        for connection in connections['Items']:
            apigw_client.post_to_connection(
                Data=json.dumps({'action': 'enter', 'room_id': body['room_id'], 'username': body['username']}),
                ConnectionId=connection['connection_id']['S']
            )
    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': 'Server error.'}
    
    return {'statusCode': 200, 'body': 'Entered.'}