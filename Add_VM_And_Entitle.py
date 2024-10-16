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

#Unique ID of desktop pool to add user to
desktop_pool_name = "DESKTOP_POOL_NAME"

#FQDN of vCenter instance
vCenter_name = "VCENTER_FQDN"

#Name of VM within vCenter
vm_name = "VCENTER_VM_NAME"

#Base URL. "https://" + FQDN of Horizon Connection server + "/rest/"
BaseURL = "https://horizon.evengooder.com/rest/"

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

#Address to call on
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

#Taps into first object of array and pulls ID attribute
target_user_id = responseBodyJSON[0]["id"]


###################################################
#### Grab desktop pool ID based on pools Unique ID 
#### 
###################################################

#Address to call on
target_url = BaseURL + "inventory/v4/desktop-pools"

#Filter param based on desktop_pool_name variable
desktop_filter = '{"type":"Equals","name":"name","value":"' + desktop_pool_name + '"}'

#Making the call and returning a JSON formatted response
desktopPool = getR_got_w_filter(target_url, desktop_filter)

target_pool_id = desktopPool[0]["id"]



###################################################
##### Get vCenter ID based of vCenter FQDN
#####
###################################################


#Address to call on
targetURL = BaseURL + "config/v1/virtual-centers"

#Params for getR_got_w_object_serarch
params = {
    'format': 'JSON'
}

#Fetch the object who's key named "server_name" matches the value of vCenter_name
vCenter_object = getR_got_w_object_search(targetURL, params, "server_name", vCenter_name)

#Pulling the ID off the returned vCenter object 
vCenter_ID = vCenter_object["id"]


###################################################
##### Get target machine ID from vCenter 
#####
###################################################

#Address to call on
targetURL = BaseURL + "external/v1/virtual-machines"

#Params for getR_got_w_object_serarch
params = {
    'format': 'JSON',
    'vcenter_id': vCenter_ID
}

#Fetch the VM object who's key named "name" matches the value of vm_name
vm_object = getR_got_w_object_search(targetURL, params, "name", vm_name)

#Pull value of "id" off returned VM object 
vm_id = vm_object["id"]


###################################################
##### Add VM to Manual desktop pool  
#####
###################################################

#Address to call on
targetURL = BaseURL + "inventory/v1/desktop-pools/" + target_pool_id + "/action/add-machines"

#Target machine ID from vCenter is fed as part of an array for later
#use in the JSON body request
target_machine = [ vm_id ]

#Adding the vCenter VM to the manaul pool 
getR_posted_w_JSON(targetURL, target_machine)



###################################################
#### Get Horizon machine ID 
#### 
###################################################

#Need a pause between adding vCenter VM to pool and obtaining it's
#special Horizon ID. This pauses for 3 seconds 
time.sleep(3)

#Address to call on
target_url = BaseURL + "inventory/v5/machines"

#Filter param based on vm_name variable
desktop_filter = '{"type":"Equals","name":"name","value":"' + vm_name + '"}'

#Make call to target_URL using filter based on vm_name.  Back the machine object that
#matches that vm_name
horizon_VM = getR_got_w_filter(target_url, desktop_filter)

#Pulls the ID of the machine object and assigns to horizon_machine_id variable
horizon_machine_id = horizon_VM[0]["id"]




###################################################
##### Dedicate desktop to user 
#####
###################################################

#Address to call on
targetURL = BaseURL + "inventory/v1/machines/" + horizon_machine_id + "/action/assign-users"

#Proper formate for requied JSON body request
target_user = [ target_user_id ]

#Proper formate for requied JSON body request
getR_posted_w_JSON(targetURL, target_user)


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
