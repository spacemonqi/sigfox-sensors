from decimal import Decimal
from pprint import pprint
import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import plotly.express as px

# To run the code using the DynamoDB web service, change the line
# dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")
# to
# dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

def plot_trend():
    df = px.data.gapminder().query("country=='Canada'")
    fig = px.line(df, x='year', y='lifeExp', title='Life expectancy in Canada')
    fig.show()

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

if __name__ == '__main__':

    plot_trend()

    # # Read an itemx`
    # movie = get_movie("The Big New Movie", 2015,)
    # if movie:
    #     print("Get movie succeeded:")
    #     pprint(movie, sort_dicts=False)
