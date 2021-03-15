#!/usr/local/bin/python3

from boto3.dynamodb.conditions import Key
import boto3

def create_sigfox_table_AWS(online, table_name, region, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb', region_name=region)
        else:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        table_name=table_name,
        KeySchema=[
            {
                'AttributeName': 'deviceId',
                'KeyType': 'HASH'  # Partition Key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort Key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'deviceId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        },
        StreamSpecification={
            'StreamEnabled': True,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'
        }
    )
    return table

def delete_sigfox_table_AWS(online, table_name, region, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb', region_name=region)
        else:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table(table_name)
    table.delete()

def scan_items_AWS(online, table_name, region, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb', region_name=region)
        else:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table(table_name)
    response = table.scan()
    return response

def put_item_AWS(online, table_name, deviceId, timestamp, data, temperature, humidity, region, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb', region_name=region)
        else:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table(table_name)
    response = table.put_item(
        Item={
            'deviceId': deviceId,
            'timestamp': timestamp,
            'payload': {
                'data': data,
                'temperature': temperature,
                'humidity': humidity,
            }
        }
    )
    return response

def query_and_project_items_AWS(online, table_name, deviceId, last_timestamp, region, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb', region_name=region)
        else:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table(table_name)
    response = table.query(
                        ProjectionExpression='#id, #ts, payload',
                        ExpressionAttributeNames={'#id': 'deviceId', '#ts': 'timestamp'},
                        KeyConditionExpression=Key('deviceId').eq(deviceId) & Key('timestamp').between(last_timestamp+1, 99999999999999)
               )
    return response['Items']
