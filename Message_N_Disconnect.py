import requests
from requests.packages import urllib3
import time


#Disables warnings about insecure requests if verify set to False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

###################################################
#### Critical variables required for proper execution
#### 
###################################################
#Loging into Horizon Server API with admin creds
username = "SHORT_AD_USERNAME"
password = "AD_PASSWORD" 
domain = "AD_DOMAIN"

#Short AD login name of user to message and disconnect
login_name = "SHORT_AD_USERNAME"


###################################################
#### Useful functions for managing Horizon Sever API
#### 
###################################################

#Authenticates to the Horizon environment specified by target using
#the username, password and domain arguments. Returns the access_token
#that's later used in headers for authorization of other
#requests.  
def get_access_token(target, username, password, domain):

    json_data = {
    "username": username,
    "password": password,
    "domain": domain
    }

    response = requests.post(
        target,
        json=json_data,
        verify=False
    )
      
    return response.json()["access_token"]


#Get request using target URL and special filter parameters
def getR_got_w_filter(target, filter_param):
    headers = {
        'authorization': 'Bearer ' + JWtoken
    }

    params = {
        'filter': filter_param
    }

    response = requests.get(
        target,
        params=params,
        headers=headers,
        verify=False
    )

    return response.json()


#POST request based on target URL and JSON request body based off of
#json_4_request
def getR_posted_w_JSON(target, json_4_request):
    headers = {
        'authorization': 'Bearer ' + JWtoken
    }

    response = requests.post(
        target,
        json=json_4_request,
        headers=headers,
        verify=False
    )
    
    return response


###########################################################
#####Getting the access token from Horizon Server API and
#####assigning it to the JWtoken variable used for
#####auhtorizing all proceeding calls.  
###########################################################
#Address for login API
target = "https://horizon.evengooder.com/rest/login"

#Set variable JWtoken to access_token 
JWtoken = get_access_token(target, username, password, domain)


###################################################
#### Getting the users AD ID based on their short
#### AD login name.  This AD ID is used by Horizon 
#### internally for any kind of management
###################################################
#Address to call on
target_url = "https://horizon.evengooder.com/rest/external/v1/ad-users-or-groups"

#Filter param based on login_name variable
ad_users_or_groups_filter = '{"type":"Equals","name":"login_name","value":"' + login_name + '"}'

#Making the call and reuturning JSON formatted response 
responseBodyJSON = getR_got_w_filter(target_url, ad_users_or_groups_filter)

target_user_id = responseBodyJSON[0]["id"]


###################################################
#### Grab ID of target session 
#### 
###################################################
#Address to call on
target_url = "https://horizon.evengooder.com/rest/inventory/v2/sessions"

#Filter param based on target_user_id variable
session_filter = '{"type":"Equals","name":"user_id","value":"' + target_user_id + '"}'

#Making the call and returning a JSON formatted response
targetSession = getR_got_w_filter(target_url, session_filter)

target_session_id = targetSession[0]["id"]


###################################################
#### Sends a message to target_session_id
#### 
###################################################
#Address to call on
target = "https://horizon.evengooder.com/rest/inventory/v1/sessions/action/send-message"

#JSON body request required for send-message endpoint 
json_data = {
    "message": "Your session will be disconnected in about 8 seconds.",
    "message_type": "INFO",
    "session_ids": [ target_session_id ]
}

#Making the call and returning reponse to message_post for observation and
#error handling
message_post = getR_posted_w_JSON(target, json_data)

#Pausing for 8 seconds before actual disconnect 
time.sleep(8)

###################################################
#### Disconnects the target_session_id
#### 
###################################################
#Address to call on
target = "https://horizon.evengooder.com/rest/inventory/v1/sessions/action/disconnect"

#JSON body request required for send-message endpoint 
json_data = [
    target_session_id
]

#Returning reponse to message_post for observation and error handling
disconnect_post = getR_posted_w_JSON(target, json_data)
