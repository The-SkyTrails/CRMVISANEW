import requests
import json

# Define the URL and the headers
url = "https://backend.aisensy.com/campaign/t1/api/v2"
headers = {
    "Content-Type": "application/json"
}

# Define the payload
data = {
    "apiKey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1Zjk4M2ZmZTMxNWI1NDVjZDQ1Nzk3ZSIsIm5hbWUiOiJ0aGVza3l0cmFpbCA4NDEzIiwiYXBwTmFtZSI6IkFpU2Vuc3kiLCJjbGllbnRJZCI6IjY1Zjk4M2ZmZTMxNWI1NDVjZDQ1Nzk3NCIsImFjdGl2ZVBsYW4iOiJCQVNJQ19NT05USExZIiwiaWF0IjoxNzEwODUxMDcxfQ.XnS_3uclP8c0J6drYjBCAQmbE6bHxGuD2IAGPaS4N9Y",
    "campaignName": "Updates",
    "destination": "919135219071",
    "userName": "theskytrail 8413",
    "templateParams": [
        "Qamar sala kamina kutta "
    ],
    "source": "new-landing-page form",
    "media": {
        "url": "https://whatsapp-media-library.s3.ap-south-1.amazonaws.com/IMAGE/6353da2e153a147b991dd812/4958901_highanglekidcheatingschooltestmin.jpg",
        "filename": "sample_media"
    },
    "buttons": [],
    "carouselCards": [],
    "location": {},
    "paramsFallbackValue": {
        "FirstName": "user"
    }
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response
print(response.status_code)
print(response.text)
