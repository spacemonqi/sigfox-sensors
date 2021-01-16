from decimal import Decimal
from pprint import pprint
import json
import boto3
from botocore.exceptions import ClientError

def create_movie_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName='Movies',
        KeySchema=[
            {
                'AttributeName': 'year',
                'KeyType': 'HASH' # Partition Key
            },
            {
                'AttributeName': 'title',
                'KeyType': 'RANGE' # Sort Key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'year',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def load_movies(movies, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')
    for movie in movies:
        year = int(movie['year'])
        title = movie['title']
        print("Adding movie:", year, title)
        table.put_item(Item=movie)

def put_movie(title, year, plot, rating, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')
    response = table.put_item(
        Item={
            'year': year,
            'title': title,
            'info': {
                'plot': plot,
                'rating': rating
            }
        }
    )
    return response

def get_movie(title, year, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

        table = dynamodb.Table('Movies')

        try:
            response = table.get_item(Key={'year': year, 'title': title})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']

def update_movie(title, year, rating, plot, actors, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')

    response = table.update_item(
        Key={
            'year': year,
            'title': title
        },
        UpdateExpression="set info.rating=:r, info.plot=:p, info.actors=:a",
        ExpressionAttributeValues={
            ':r': Decimal(rating),
            ':p': plot,
            ':a': actors
        },
        ReturnValues="UPDATED_NEW"
    )
    return response

def increase_rating(title, year, rating_increase, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')

    response = table.update_item(
        Key={
            'year': year,
            'title': title
        },
        UpdateExpression="set info.rating = info.rating + :val",
        ExpressionAttributeValues={
            ':val': Decimal(rating_increase)
        },
        ReturnValues="UPDATED_NEW"
    )
    return response

def remove_actors(title, year, actor_count, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')

    try:
        response = table.update_item(
            Key={
                'year': year,
                'title': title
            },
            UpdateExpression="remove info.actors[0]",
            ConditionExpression="size(info.actors) >= :num",
            ExpressionAttributeValues={':num': actor_count},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        return response

def delete_underrated_movie(title, year, rating, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')

    try:
        response = table.delete_item(
            Key={
                'year': year,
                'title': title
            },
            ConditionExpression="info.rating <= :val",
            ExpressionAttributeValues={
                ":val": Decimal(rating)
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        return response

def query_movies(year, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Movies')
    response = table.query(
        KeyConditionExpression=Key('year').eq(year)
    )
    return response['Items']

if __name__ == '__main__':

    # # Create the table
    # input("Press enter to create the table")
    # movie_table = create_movie_table()
    # print("Table status: ", movie_table.table_status)

    # # Populate the table
    # input("Press enter to populate the table")
    # with open("moviedata.json") as json_file:
    #     movie_list = json.load(json_file, parse_float=Decimal)
    # load_movies(movie_list)

    # # Add an item
    # movie_resp = put_movie("The Big New Movie", 2015,
    #                        "Nothing happens at all.", 0)
    # print("Put movie succeeded:")
    # pprint(movie_resp, sort_dicts=False)

    # # Read an item
    # movie = get_movie("The Big New Movie", 2015,)
    # if movie:
    #     print("Get movie succeeded:")
    #     pprint(movie, sort_dicts=False)

    # # Update an item
    # update_response = update_movie(
    #     "The Big New Movie", 2015, 5.5, "Everything happens all at once.",
    #     ["Larry", "Moe", "Curly"])
    # print("Update movie succeeded:")
    # pprint(update_response, sort_dicts=False)

    # # Increment an Atomic Counter
    # update_response = increase_rating("The Big New Movie", 2015, 1)
    # print("Update movie succeeded:")
    # pprint(update_response, sort_dicts=False)

    # # Update an item (Conditionally)
    # print("Attempting conditional update (expecting failure)...")
    # update_response = remove_actors("The Big New Movie", 2015, 3)
    # if update_response:
    #     print("Update movie succeeded:")
    #     pprint(update_response, sort_dicts=False)

    # # Delete an item
    # print("Attempting a conditional delete...")
    # delete_response = delete_underrated_movie("The Big New Movie", 2015, 5)
    # if delete_response:
    #     print("Delete movie succeeded:")
    #     pprint(delete_response, sort_dicts=False)

    # Query items
    query_year = 2001
    print(f"Movies from {query_year}")
    movies = query_movies(query_year)
    for movie in movies:
        print(movie['year'], ":", movie['title'])
