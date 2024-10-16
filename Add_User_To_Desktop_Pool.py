import requests
from requests.packages import urllib3

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

#Unique ID of desktop pool to add user to
desktop_pool_name = "DESKTOP_POOL_NAME"

#Base URL. "https://" + FQDN of Horizon Connection server + "/rest/"
BaseURL = "https://FQDN_HORIZON_CONNECTION_SERVER/rest/"

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
#####Getting the access token from Horizon Server API
#####
###########################################################
#Full address for login endpoint
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

#Making the call and reutrning JSON formatted response 
responseBodyJSON = getR_got_w_filter(target_url, ad_users_or_groups_filter)

target_user_id = responseBodyJSON[0]["id"]


##################################################
#### Grab desktop pool ID based on pools Unique ID 
#### 
###################################################
#Address to call on
target_url = BaseURL + "inventory/v4/desktop-pools" 

#Filter param based on desktop_pool_name variable
desktop_filter = '{"type":"Equals","name":"name","value":"' + desktop_pool_name + '"}'

#Making the call and reutrning JSON formatted response 
desktopPool = getR_got_w_filter(target_url, desktop_filter)

#Horizon's internal ID for the target desktop pool
target_pool_id = desktopPool[0]["id"]


###################################################
#### Entitling user to desktop pool 
#### 
###################################################
# Tricky JSON request body required for adding user 
json_data = [{
    "ad_user_or_group_ids": [ target_user_id ],
    "id": target_pool_id
}]

# Address to POST request to
target_url = BaseURL + "entitlements/v1/desktop-pools"

response = getR_posted_w_JSON(target_url, json_data)
