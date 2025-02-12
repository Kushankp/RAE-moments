import requests
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv(r'E:\UIC\RAE\Homework\moments\.env')

def load_api_key():
    # Get API key and endpoint from environment variables
    subscription_key = os.getenv('AZURE_KEY')
    endpoint = os.getenv('AZURE_ENDPOINT')

    if not subscription_key or not endpoint:
        raise ValueError("AZURE_KEY and AZURE_ENDPOINT must be set in the .env file")

    return subscription_key, endpoint

def query(filename):
    subscription_key, endpoint = load_api_key()
    object_detection_url = f"{endpoint}/vision/v3.2/detect"

    with open(filename, "rb") as image_data:
        headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
        params = {'visualFeatures': 'Objects'}
        response = requests.post(object_detection_url, headers=headers, params=params, data=image_data)

    response.raise_for_status()
    analysis = response.json()
    
    return [obj['object'] for obj in analysis['objects']]
