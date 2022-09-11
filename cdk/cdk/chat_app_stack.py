from aws_cdk import (
    core,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwi,
    aws_lambda as lmbda,
    aws_dynamodb as ddb,
    aws_s3 as s3,
    aws_cloudfront_origins as origins,
    aws_cloudfront as cloudfront

)
from constructs import Construct

class ChatAppStack(core.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app='chat-app'

        static_website_bucket = s3.Bucket(
            self,
            id=f"{app}-client-bucket",
            bucket_name=f"{app}-client-bucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=core.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            enforce_ssl=True
        )

        origin = origins.S3Origin(static_website_bucket)

        static_website_distribution = cloudfront.Distribution(
            self,
            'StaticWebsiteDistribution',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object='index.html',
            error_responses=[cloudfront.ErrorResponse(
                http_status=403,
                response_http_status=200,
                response_page_path='/'
            )],
            additional_behaviors={
                'index.html': cloudfront.BehaviorOptions(
                    origin=origin,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                )
            }
        )

        connect_handler = lmbda.Function(
            self, id=f"{app}-connect-handler",
            runtime=lmbda.Runtime.PYTHON_3_9,
            handler='index.lambda_handler',
            code=lmbda.Code.from_asset('../websocket/on_connect')
        )

        disconnect_handler = lmbda.Function(
            self, id=f"{app}-disconnect-handler",
            runtime=lmbda.Runtime.PYTHON_3_9,
            handler='index.lambda_handler',
            code=lmbda.Code.from_asset('../websocket/on_disconnect')
        )

        enter_handler =  lmbda.Function(
            self, id=f"{app}-enter-handler",
            runtime=lmbda.Runtime.PYTHON_3_9,
            handler='index.lambda_handler',
            code=lmbda.Code.from_asset('../websocket/on_enter')
        )
       
        message_handler = lmbda.Function(
            self, id=f"{app}-message-handler",
            runtime=lmbda.Runtime.PYTHON_3_9,
            handler='index.lambda_handler',
            code=lmbda.Code.from_asset('../websocket/send_message')
        )

        web_socket_api = apigwv2.WebSocketApi(
            self, id=f"{app}-websocket-api", 
            route_selection_expression='$request.body.action',
            connect_route_options=apigwv2.WebSocketRouteOptions(
                integration=apigwi.WebSocketLambdaIntegration(f"{app}-connect-integ", connect_handler)
            ),
            disconnect_route_options=apigwv2.WebSocketRouteOptions(
                integration=apigwi.WebSocketLambdaIntegration(f"{app}-disconnect-integ", disconnect_handler)
            )
        )

        web_socket_api.add_route("enter",
            integration=apigwi.WebSocketLambdaIntegration(f"{app}-enter-integ", enter_handler)
        )


        web_socket_api.add_route("sendmessage",
            integration=apigwi.WebSocketLambdaIntegration(f"{app}-send-message-integ", message_handler)
        )

        web_socket_api.grant_manage_connections(disconnect_handler)
        web_socket_api.grant_manage_connections(enter_handler)
        web_socket_api.grant_manage_connections(message_handler)

        web_socket_stage = apigwv2.WebSocketStage(
            self, id=f"{app}-websocket-stage", 
            stage_name='prod',
            web_socket_api=web_socket_api, 
            auto_deploy=True
        )

        connection_table = ddb.Table(
            self, id=f"{app}-connection-table", 
            table_name='chat-app-connection',
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            partition_key=ddb.Attribute(
                name='connection_id',
                type=ddb.AttributeType.STRING
            ),
            removal_policy=core.RemovalPolicy.DESTROY
        )

        connection_table.add_global_secondary_index(
            index_name='room-index',
            partition_key=ddb.Attribute(
                name='room_id',
                type=ddb.AttributeType.STRING
            ),
            sort_key=ddb.Attribute(
                name='username',
                type=ddb.AttributeType.STRING
            ),
        )

        connection_table.grant_read_write_data(connect_handler)
        connection_table.grant_read_write_data(disconnect_handler)
        connection_table.grant_read_write_data(enter_handler)
        connection_table.grant_read_write_data(message_handler)


        
        