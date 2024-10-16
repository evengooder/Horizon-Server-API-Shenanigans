import requests
from requests.packages import urllib3
import time

#Disables warnings about insecure requests 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


###################################################
#### Critical variables required for proper execution
#### 
###################################################
#Loging into Horizon Server API with admin creds
username = "SHORT_AD_USERNAME"
password = "AD_PASSWORD" 
domain = "AD_DOMAIN"

#Short AD login name of user to entitle
login_name = "SHORT_AD_USERNAME"

#Name of app to target and terminate 
target_app = "TARGET_APP"

#Base URL. "https://" + FQDN of Horizon Connection server + "/rest/"
BaseURL = "https://FQDN_HORIZON_CONNECTION_SERVER/rest/"

###########################################################
##### Some resuable functions
#####
###########################################################

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


#Searches for specific object in array of objects based on unique key value
#Object_key_name is the name of the key to check for the object_key_value        
def getR_got_w_object_search(target, params, object_key_name, object_key_value):
    headers = {
        'authorization': 'Bearer ' + JWtoken
    }

    response = requests.get(
        target,
        params=params,
        headers=headers,
        verify=False
    )

    object_array = response.json()

    for json_object in object_array:
        if json_object[ object_key_name ] == object_key_value:       
            return json_object 


###########################################################
#####Getting the access token from Horizon Server API
#####
###########################################################

#Address for login API
target = BaseURL + "login"

#Set variable JWtoken to access_token 
JWtoken = get_access_token(target, username, password, domain)


###################################################
#### Getting the users AD ID based on their short
#### AD login name
###################################################

#Address to call on
target_url = BaseURL + "external/v1/ad-users-or-groups"

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
target_url = BaseURL + "inventory/v2/sessions"

#Filter param based on target_user_id variable
session_filter = '{"type":"Equals","name":"user_id","value":"' + target_user_id + '"}'

#Making the call and returning a JSON formatted response
targetSession = getR_got_w_filter(target_url, session_filter)


target_session_id = targetSession[0]["id"]



###################################################
##### Retrieve list of running apps within session
##### and locating 
###################################################

#Address to call on
target = BaseURL + "helpdesk/v1/performance/remote-application"

#Required params, including session_id to inspect
params = {
    'format': 'JSON',
    'session_id': target_session_id
}

#Loops through returnned array fo objects for an object with a name that equals the variable
#target_app.  
application_object = getR_got_w_object_search(target, params, "name", target_app)

#Pulls value of remote_application_id from matching object 
remote_app_id = application_object[ "remote_application_id" ]


###################################################
#### Kill remote application
#### 
###################################################

target = BaseURL + "helpdesk/v1/performance/remote-application/action/end-remote-application"

def kill_remote_app(target, target_session, remote_app):
    headers = {
        'accept': 'application/json',
        'authorization': 'Bearer ' + JWtoken
    }

    params = {
        'format': 'JSON',
        'session_id': target_session,
        'remote_application_id': remote_app
    }

    response = requests.post(
        target,
        params=params,
        headers=headers,
        verify=False,
    )
    
    #return response.json()

kill_remote_app(target, target_session_id, remote_app_id)

