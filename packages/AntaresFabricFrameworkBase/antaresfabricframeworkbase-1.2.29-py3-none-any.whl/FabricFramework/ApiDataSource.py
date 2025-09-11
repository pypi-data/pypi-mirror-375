# Imports
from pyspark.sql import SparkSession
from enum import Enum
from requests.auth import HTTPBasicAuth
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from pyspark.sql.functions import lit
import requests
import json
import time as t
from datetime import datetime, timedelta
from pytz import timezone
from pyspark.sql.functions import col

from FabricFramework.FabricDataInterface import *
from FabricFramework.FabricLocations import *

#Constants mapping the ingestion configuration nodes relevant to the REST API source
REST_API_KEY_VAULT_NAME = "key_vault_name"
REST_API_TENANT_ID = "tenant_id"
REST_API_CLIENT_ID = "client_id"
REST_API_CLIENT_SECRET = "client_secret"
REST_API_SECRET_NAME = "secret_name"
REST_API_SETTINGS = "rest_api_settings"
REST_API_VERB = "api_verb"
REST_API_BASE_URL = "base_url"
REST_API_RELATIVE_URL = "relative_url"
REST_API_AUTHORIZATION = "authorization"
REST_API_KEY = "key"
REST_API_NAME = "name"
REST_API_VALUE = "value"
REST_API_VALUE_SECRET = "value_secret"
REST_API_HEADERS = "headers"
REST_API_PARAMETERS = "params"
REST_API_PAGINATION_RULE_SETTINGS = "pagination_rule_settings"
REST_API_TYPE = "type"
REST_API_EXPRESSION = "expression"
REST_API_VALUE_RANGE = "value_range"
REST_API_END_CONDITION = "end_condition"
REST_API_AREA = "api_area"
REST_API_AUTH_SETTINGS = "auth_settings"
REST_API_DATA_NODE = "response_data_node"
REST_API_SOURCE_NAME = "source_name"
REST_API_WATERMARK = "watermark"
REST_API_TRUSTED_WORKSPACE = "trusted_workspace"
REST_API_TRUSTED_LAKEHOUSE = "trusted_lakehouse"
REST_API_PARENT_SOURCE_ID = "parent_SourceId"
REST_API_PRIMARY_KEY = "primary_key"
REST_API_DESTINATION_NAME = "destination_name"
REST_API_RAW_WORKSPACE = "raw_workspace"
REST_API_RAW_LAKEHOUSE = "raw_lakehouse"
REST_API_PARENT_FILTER = "parent_filter"
REST_API_PRIMARY_KEY_PATH = "primary_key_path"

#Class RestAPIAuthorizationType represents the various API authorization types
class RestAPIAuthorizationType(Enum):
    Basic = 1
    BearerToken = 2
    APIKey = 3
    OAuth2 = 4
    NoAuth = 5
    DynamicBearerToken = 6

#Class RestAPIArea represents the area of the API request or response
class RestAPIArea(Enum):
    Params = 1
    Headers = 2
    Body = 3
    Undefined = 4

#Class RestAPIDictionaryItemType represents the type of a REST API dictionary item object
class RestAPIDictionaryItemType(Enum):
    Undefined = 1,
    GrantType = 2
    CallBackURL = 3
    AuthURL = 4
    AccessTokenURL = 5
    ClientId = 6
    ClientSecret = 7
    Scope = 8
    State = 9
    RefreshTokenURL = 10
    AuthRequest = 11
    TokenRequest = 12
    RefreshRequest = 13
    PaginationEndCondition = 14
    UserName = 15
    Password = 16
    BearerToken = 17
    APIKey = 18
    BaseURL = 19
    DynamicBearerToken = 20

#Class RestAPIPaginationRuleType represents the type of REST API pagination rule
class RestAPIPaginationRuleType(Enum):
    AbsoluteUrl = 1
    QueryParameters = 2
    Headers = 3
    SupportRFC5988 = 4
    MaxRequestNumber = 5
    EndCondition = 6

#Class RestAPIVerbType represents the API Verb
class RestAPIVerbType(Enum):
    Get = 1
    Put = 2
    Delete = 3
    Head = 4
    Patch = 5
    Post = 6
    Request = 7

#Class RestAPIDictionaryItem represents a generic dictionary item, representing an area of the REST API (body, params or headers)
class RestAPIDictionaryItem():
    def __init__(self, itemType: RestAPIDictionaryItemType, apiArea: RestAPIArea, keyName, keyValue ="", keyValueSecret=""):
        self.type = self._validate_itemType(itemType)
        self.apiArea = self._validate_apiArea(apiArea)
        self.key = self._validate_keyName(keyName)
        self.value = self._validate_keyValue(keyValue)
        self.valueSecret = keyValueSecret

        if keyValue.strip() == "" and keyValueSecret.strip() == "":
            raise ValueError(f"Either keyValue or keyValueSecret must be specified")

    def _validate_itemType(self, itemType):
        if isinstance(itemType, (RestAPIDictionaryItemType)):
            return itemType
        raise TypeError(
            f"The itemType of type RestAPIDictionaryItemType is expected, got {type(itemType).__name__}"
        )  

    def _validate_apiArea(self, apiArea):
        if isinstance(apiArea, (RestAPIArea)):
            return apiArea
        raise TypeError(
            f"The apiArea of type RestAPIArea is expected, got {type(apiArea).__name__}"
        )  

    def _validate_keyName(self, keyName): 
        if isinstance(keyName, (str)):
            if keyName.strip() == "":
                raise TypeError(f"keyName cannot be blank")
            else:
                return keyName
        else:                
            raise TypeError(
                f"The keyName of type str is expected, got {type(keyName).__name__}"
            )

    def _validate_keyValue(self, keyValue): 
        if isinstance(keyValue, (str)):
            return keyValue
        else:                
            raise TypeError(
                f"The keyValue of type str is expected, got {type(keyValue).__name__}"
            )            

    #def _validate_keyValueSecret(self, keyValueSecret): 
        #if isinstance(keyValueSecret, (str)):            
            #return KeyVault(source[REST_API_KEY_VAULT_NAME], keyValueSecret).secretValue    #Get the actual key vault secret value from the specified secret name
        #else:                
            #raise TypeError(
                #f"The keyValueSecret of type str is expected, got {type(keyValueSecret).__name__}"
            #)  

#Class RestAPIPaginationRule represents the REST API pagination rule
class RestAPIPaginationRule:
    def __init__(self, ruleType: RestAPIPaginationRuleType, ruleKeyName, ruleExpression, ruleValueRange, endCondition: RestAPIDictionaryItem):
        self.type = self._validate_ruleType(ruleType)
        self.key = self._validate_ruleKeyName(ruleKeyName)
        self.expression = self._validate_ruleExpression(ruleExpression)
        self.valueRange = self._validate_ruleValueRange(ruleValueRange)
        self.endCondition = self._validate_endCondition(endCondition)

    #===========================================================
    #Private methods
    #===========================================================
    def _validate_ruleType(self, ruleType):
        if isinstance(ruleType, (RestAPIPaginationRuleType)):
            return ruleType
        raise TypeError(
            f"The ruleType of type RestAPIPaginationRuleType is expected, got {type(ruleType).__name__}"
        )  

    def _validate_ruleKeyName(self, ruleKeyName): 
        if isinstance(ruleKeyName, (str)):
            return ruleKeyName
        raise TypeError(
                f"The ruleKeyName of type str is expected, got {type(ruleKeyName).__name__}"
            )  

    def _validate_ruleExpression(self, ruleExpression): 
        if isinstance(ruleExpression, (str)):
            return ruleExpression
        raise TypeError(
                f"The ruleExpression of type str is expected, got {type(ruleExpression).__name__}"
            )                             


    def _validate_ruleValueRange(self, ruleValueRange):
        if not isinstance(ruleValueRange, (int)) and not isinstance(ruleValueRange, (str)):
            raise TypeError(
                f"The ruleValueRange of type str or int is expected, got {type(ruleValueRange).__name__}"
            )   
        else:            
            if isinstance(ruleValueRange, (int)):   #An int value provided
                return ruleValueRange
            else:   #A range provided. It must comply the format N:N:N
                if not ruleValueRange.count(":") == 2:
                    raise ValueError(f"The format of ruleValueRange must be N:N:N")
                else:
                    ruleValRngLst = ruleValueRange.split(":")   #e.g. 1::1 -> ['1','','1']
                    #The incremental counter is mandatory
                    try:
                        incrCtr = int(ruleValRngLst[2].strip())
                    except:
                        raise ValueError(f"Invalid incremental counter value specified {ruleValRngLst[2]}")

                    #The min value is also mandatory
                    try:
                        minVal = int(ruleValRngLst[0].strip())
                    except:
                        raise ValueError(f"Invalid min value specified {ruleValRngLst[0]}")

                    #The max value is not mandatory but if specified, must be an integer
                    try:
                        if not ruleValRngLst[1].strip() == "":
                            maxVal = int(ruleValRngLst[1].strip())
                    except:
                        raise ValueError(f"Invalid max value specified {ruleValRngLst[1]}")

                    return ruleValueRange   #All good!                       
                       


    def _validate_endCondition(self, endCondition):
        if isinstance(endCondition, (RestAPIDictionaryItem)):
            return endCondition
        raise TypeError(
            f"The endCondition of type RestAPIDictionaryItem is expected, got {type(endCondition).__name__}"
        )  

    #===========================================================
    #Public methods
    #===========================================================
    #Return the abolute value of the value range
    def getAbsValue(self):
        if isinstance(self.valueRange, (int)):   #An int value provided
            return self.valueRange
        else:   #A range provided
            return None

    #Return the min value of the value range
    def getMinValue(self):
        if isinstance(self.valueRange, (int)):   #An int value provided
            return self.valueRange
        else:   #A range provided
            valRngLst = self.valueRange.split(":")          
            return int(valRngLst[0].strip())


    #Return the max value of the value range
    def getMaxValue(self):
        if isinstance(self.valueRange, (int)):   #An int value provided
            return self.valueRange
        else:   #A range provided
            valRngLst = self.valueRange.split(":")          
            if not valRngLst[1].strip() == "":
                return int(valRngLst[1].strip())
            else:
                return None   

    #Return the incremental value of the range
    def getIncrementalValue(self):
        if isinstance(self.valueRange, (int)):   #An int value provided
            return None
        else:   #A range provided
            valRngLst = self.valueRange.split(":")          
            return int(valRngLst[2].strip())                                        


#Class RESTAPIAuthorization represents the API authorization
class RESTAPIAuthorization:
    def __init__(self, authType: RestAPIAuthorizationType, authSettings = []):
        self.authType = self._validate_autheType(authType)
        self.authSettings = self._validate_authSettings(authSettings)

    
    def _validate_autheType(self, authType):
        if isinstance(authType, (RestAPIAuthorizationType)):
            return authType
        raise TypeError(
            f"The authType of type RestAPIAuthorizationType is expected, got {type(authType).__name__}"
        )  

    def _validate_authSettings(self, authSettings):
        if not authSettings:
            return []
        else:
            #Return a list of dictionary items against each auth setting in the config file
            authSettingLst = []
            for authSetting in authSettings:
                if not authSetting[REST_API_TYPE]:
                    dicItemType = RestAPIDictionaryItemType.Undefined
                else:    
                    match authSetting[REST_API_TYPE].lower().strip():
                        case "":
                            dicItemType = RestAPIDictionaryItemType.Undefined
                        case "undefined":
                            dicItemType = RestAPIDictionaryItemType.Undefined
                        case "granttype":
                            dicItemType = RestAPIDictionaryItemType.GrantType
                        case "callbackurl":
                            dicItemType = RestAPIDictionaryItemType.CallBackURL
                        case "authurl":
                            dicItemType = RestAPIDictionaryItemType.AuthURL
                        case "accesstokenurl":
                            dicItemType = RestAPIDictionaryItemType.AccessTokenURL  
                        case "bearertoken":
                            dicItemType = RestAPIDictionaryItemType.BearerToken                          
                        case "clientid":
                            dicItemType = RestAPIDictionaryItemType.ClientId 
                        case "clientsecret":
                            dicItemType = RestAPIDictionaryItemType.ClientSecret 
                        case "scope":
                            dicItemType = RestAPIDictionaryItemType.Scope 
                        case "state":
                            dicItemType = RestAPIDictionaryItemType.State 
                        case "refreshtokenurl":
                            dicItemType = RestAPIDictionaryItemType.RefreshTokenURL 
                        case "authrequest":
                            dicItemType = RestAPIDictionaryItemType.AuthRequest
                        case "tokenrequest":
                            dicItemType = RestAPIDictionaryItemType.TokenRequest                         
                        case "refreshrequest":
                            dicItemType = RestAPIDictionaryItemType.RefreshRequest                                
                        case "paginationendcondition":
                            dicItemType = RestAPIDictionaryItemType.PaginationEndCondition 
                        case "username":
                            dicItemType = RestAPIDictionaryItemType.UserName 
                        case "password":
                            dicItemType = RestAPIDictionaryItemType.Password 
                        case "refreshtokenurl":
                            dicItemType = RestAPIDictionaryItemType.RefreshTokenURL
                        case _:
                            dicItemType = RestAPIDictionaryItemType.Undefined

                
                if not authSetting[REST_API_AREA]:
                    dicItemAPIArea = RestAPIArea.Undefined
                else:                       
                    match authSetting[REST_API_AREA].lower().strip():
                        case "params":
                            dicItemAPIArea = RestAPIArea.Params
                        case "headers":
                            dicItemAPIArea = RestAPIArea.Headers
                        case "body":
                            dicItemAPIArea = RestAPIArea.Body
                        case _:
                            dicItemAPIArea = RestAPIArea.Undefined

                if not authSetting[REST_API_KEY]:
                    raise ValueError(f"The attribute " + REST_API_KEY + " not specified")  
                else                    :
                    dicItemKey = authSetting[REST_API_KEY]

                dictItemVal = authSetting[REST_API_VALUE] if REST_API_VALUE in authSetting else "" # this line doesnt work         
                dictItemValSecret = authSetting[REST_API_VALUE_SECRET] if REST_API_VALUE_SECRET in authSetting else ""

                dictItem = RestAPIDictionaryItem(dicItemType, dicItemAPIArea, dicItemKey, dictItemVal, dictItemValSecret)

                authSettingLst.append(dictItem)
            
            return authSettingLst

# #Class for Azure Key Vault access. 
# #Note: This is to be replaced by the actual framework class
# class KeyVault:
#      def __init__(self, keyVaultName, secretName):
#         credential = ClientSecretCredential(tenant_id = "a15bd49e-2167-467b-b2ac-78dcf57ce5ce", client_id = "f79ed4dd-669b-460f-a61f-bcdc7e3f70a2", client_secret = "Mpk8Q~REK6LsbLBaBLDeXCSOtwpfSXZofTfmPcS_")
#         vaultURL = f"https://" + keyVaultName + ".vault.azure.net"
#         secretClient = SecretClient(vault_url=vaultURL, credential=credential)
#         self.secretValue = secretClient.get_secret(secretName).value

class KeyVault:
    def __init__(self, keyvaultname, tenantid, clientid, clientsecret, secretName):
        credential = ClientSecretCredential(tenantid, clientid, clientsecret)
        vaultURL = f"https://{keyvaultname}.vault.azure.net"
        secretClient = SecretClient(vault_url=vaultURL, credential=credential)
        self.secretVal = secretClient.get_secret(secretName).value

    @property
    def secretValue(self):
        return self.secretVal
    

#Class RestAPIDataSource represents a REST API data source
class RestAPIDataSource():
    def __init__(self, connection, source, function=None, constants=None):
        self.spark = SparkSession.builder.appName("Default").getOrCreate()
        #Read the credentials from the secret connection string 
        self.credentials = self._getCredentials(connection)  
        #Read in the relevant config settings
        self.verb = self._getVerb(source[REST_API_SETTINGS][REST_API_VERB]) #Get the API verb
        self.baseURL = source[REST_API_SETTINGS][REST_API_BASE_URL]
        self.relativeURL = source[REST_API_SETTINGS][REST_API_RELATIVE_URL]
        self.auth = self.__getAuth(source[REST_API_SETTINGS][REST_API_AUTHORIZATION]) #Get the auth details        
        self.headers = self.__getHeaders(source[REST_API_SETTINGS][REST_API_HEADERS]) #Get the headers, if any
        self.params = self.__getParams(source[REST_API_SETTINGS][REST_API_PARAMETERS]) #Get the query parameters, if any
        self.dataNode = source[REST_API_SETTINGS][REST_API_DATA_NODE] #The data node in the response
        self.constants = constants
        self.dynamicBearerToken = self._getDynamicBearerToken()
        self.primaryKeys = source[REST_API_PRIMARY_KEY]

        # Get the primary key path, if any
        if (
            REST_API_SETTINGS in source and
            REST_API_PRIMARY_KEY_PATH in source[REST_API_SETTINGS] and
            source[REST_API_SETTINGS][REST_API_PRIMARY_KEY_PATH]
        ):
            self.primaryKeyPath = source[REST_API_SETTINGS][REST_API_PRIMARY_KEY_PATH]
        else:
            self.primaryKeyPath = ""

        # Get the pagination rule settings, if any
        if (
            REST_API_SETTINGS in source and
            REST_API_PAGINATION_RULE_SETTINGS in source[REST_API_SETTINGS] and
            source[REST_API_SETTINGS][REST_API_PAGINATION_RULE_SETTINGS]
        ):
            self.paginationRuleSettings = self.__getPaginationRuleSettings(
                source[REST_API_SETTINGS][REST_API_PAGINATION_RULE_SETTINGS]
            )
        else:
            self.paginationRuleSettings = None

        # Get the parent entity, if any
        if (
            REST_API_SETTINGS in source and
            REST_API_PARENT_SOURCE_ID in source[REST_API_SETTINGS] and
            source[REST_API_SETTINGS][REST_API_PARENT_SOURCE_ID]
        ):
            self.parentSourceId = source[REST_API_SETTINGS][REST_API_PARENT_SOURCE_ID]
        else:
            self.parentSourceId = None

        self.trustedWorkSpaceId = source[REST_API_TRUSTED_WORKSPACE]
        self.trustedLakeHouseId = source[REST_API_TRUSTED_LAKEHOUSE]
        self.sourceName = source[REST_API_SOURCE_NAME]
        self.rawWorkSpaceId = source[REST_API_RAW_WORKSPACE]
        self.rawLakeHouseId = source[REST_API_RAW_LAKEHOUSE]

        # Get the parent filter, if any
        if (
            REST_API_SETTINGS in source and
            REST_API_PARENT_FILTER in source[REST_API_SETTINGS] and
            source[REST_API_SETTINGS][REST_API_PARENT_FILTER]
        ):
            self.parentFilter = source[REST_API_SETTINGS][REST_API_PARENT_FILTER]
        else:
            self.parentFilter = None
         

    #===========================================================
    #Private methods
    #===========================================================
    #Private method to get the credentials from the key vault secret
    def _getCredentials(self, connection):
        credentials = []
        #Load the connection string as json
        conns = json.loads(connection)
        #Loop through and create a list of dictionary items
        for conn in conns:            
            match conn[REST_API_TYPE].lower().strip(): 
                case "username":
                    itemType = RestAPIDictionaryItemType.UserName
                case "password":
                    itemType = RestAPIDictionaryItemType.Password
                case "clientid":
                    itemType = RestAPIDictionaryItemType.ClientId
                case "bearertoken":
                    itemType = RestAPIDictionaryItemType.BearerToken
                case "apikey":
                    itemType = RestAPIDictionaryItemType.APIKey
                case _:
                    raise ValueError(f"Invalid value specifed for the credential node " + REST_API_TYPE + ": " + conn[REST_API_TYPE])  

            try:
                match conn[REST_API_AREA].lower().strip(): 
                    case "params":
                        apiArea = RestAPIArea.Params
                    case "headers":
                        apiArea = RestAPIArea.Headers
                    case "body":
                        apiArea = RestAPIArea.Body
                    case _:
                        raise ValueError(f"Invalid value specifed for the credential node " + REST_API_AREA + ": " + conn[REST_API_AREA]) 
            except KeyError:
                apiArea = RestAPIArea.Undefined                         

            dicItem = RestAPIDictionaryItem(itemType, apiArea, conn[REST_API_KEY], conn[REST_API_VALUE])
            credentials.append(dicItem)

        return credentials

    
    def _getDynamicBearerToken(self):
        
        refreshTokenUrl = ""
        perm_token = ""
        accessTokenKey = ""

        # Set refresh token url
        for authSetting in self.auth.authSettings:
            if(authSetting.key.lower().strip() == "refreshtokenurl"):
                refreshTokenUrl = authSetting.value      
        
        if(refreshTokenUrl != ""):

            # Get the permenant token
            for credential in self.credentials:
                if(credential.key.lower().strip() == "authorization"):
                    perm_token = credential.value

            headers = {
                "Authorization": perm_token,
                "Content-Type": "application/json"
                        }

            refreshTokenResponse = requests.post(refreshTokenUrl, headers=headers)
            refreshTokenResponseJson = refreshTokenResponse.json()

            # set the Access Token key
            for authSetting in self.auth.authSettings:
                if(authSetting.type == RestAPIDictionaryItemType.BearerToken):
                    accessTokenKey = authSetting.key.replace("$", "").replace(">", "")  

            return refreshTokenResponseJson[accessTokenKey]
        else:
            return None


    #Private method to get the API verb from the config
    def _getVerb(self, verb):
        apiVerb = None
        match verb.strip().lower():
            case "get":
                apiVerb = RestAPIVerbType.Get
            case "put":
                apiVerb = RestAPIVerbType.Put
            case "delete":
                apiVerb = RestAPIVerbType.Delete
            case "head":
                apiVerb = RestAPIVerbType.Head
            case "patch":
                apiVerb = RestAPIVerbType.Patch
            case "post":
                apiVerb = RestAPIVerbType.Post
            case "request":
                apiVerb = RestAPIVerbType.Request
            case _:
                raise ValueError(f"Invalid value specifed for node " + REST_API_VERB + ": " + verb)
       
        return apiVerb
        
    
    #Private method to get the auth details from the config
    def __getAuth(self, auth):
        match auth[REST_API_TYPE].lower().strip():
            case "basic":
                authType = RestAPIAuthorizationType.Basic
            case "bearertoken":
                authType = RestAPIAuthorizationType.BearerToken  
            case "apikey":
                authType = RestAPIAuthorizationType.APIKey
            case "oauth2":
                authType = RestAPIAuthorizationType.OAuth2  
            case "dynamicbearertoken":
                authType = RestAPIAuthorizationType.DynamicBearerToken          
            case "":
                authType = RestAPIAuthorizationType.NoAuth
            case _:
                raise ValueError("Invalid value specifed for " + REST_API_AUTHORIZATION + "." + REST_API_TYPE)

        return RESTAPIAuthorization(authType, auth[REST_API_AUTH_SETTINGS] )


    #Private method to get the headers from the config, if any
    def __getHeaders(self, headers):
        allHeaders = []
        for header in headers:
            headerKey = header[REST_API_KEY]
            headerValue = header[REST_API_VALUE] if REST_API_VALUE in header else ""
            headerValueSecret = header[REST_API_VALUE_SECRET] if REST_API_VALUE_SECRET in header else ""          
            thisHeader = RestAPIDictionaryItem(RestAPIDictionaryItemType.Undefined, RestAPIArea.Headers, headerKey, headerValue, headerValueSecret)
            allHeaders.append(thisHeader)
        return allHeaders

    #Private method to get the params from the config, if any
    def __getParams(self, params):
        allParams = []
        for param in params:
            paramKey = param[REST_API_KEY]
            paramValue = param[REST_API_VALUE] if REST_API_VALUE in param else ""         
            thisparam = RestAPIDictionaryItem(RestAPIDictionaryItemType.Undefined, RestAPIArea.Params, paramKey, paramValue)
            allParams.append(thisparam)
        return allParams    

    #Private method to get the pagination rule settings from the config, if any   
    def __getPaginationRuleSettings(self, paginationRuleSettings):
        #Map the paginaton rule type
        match paginationRuleSettings[REST_API_TYPE].lower().strip(): 
            case "queryparameters":
                pgRuleType = RestAPIPaginationRuleType.QueryParameters
            case "absoluteurl":
                pgRuleType = RestAPIPaginationRuleType.AbsoluteUrl   
            case "headers":
                pgRuleType = RestAPIPaginationRuleType.Headers        
            case "supportrfc5988":
                pgRuleType = RestAPIPaginationRuleType.SupportRFC5988  
            case "maxrequestnumber":
                pgRuleType = RestAPIPaginationRuleType.MaxRequestNumber
            case "endcondition":
                pgRuleType = RestAPIPaginationRuleType.EndCondition                         
            case _:
                raise ValueError("Invalid value specifed for Pagination Rule Type: " + paginationRuleSettings[REST_API_TYPE].strip())   
                
        #Map the end condition API area
        match paginationRuleSettings[REST_API_END_CONDITION][REST_API_AREA].lower().strip(): 
            case "params":
                endCondArea = RestAPIArea.Params                        
            case "headers":
                endCondArea = RestAPIArea.Headers
            case "body":
                endCondArea = RestAPIArea.Body               
            case _:
                raise ValueError("Invalid value specifed for " + REST_API_END_CONDITION + "." + REST_API_AREA + ": " + 
                                        paginationRuleSettings[REST_API_END_CONDITION][REST_API_AREA])                                            

        #Create the end condition object
        endCond = RestAPIDictionaryItem(
                                            RestAPIDictionaryItemType.PaginationEndCondition
                                            ,endCondArea
                                            ,paginationRuleSettings[REST_API_END_CONDITION][REST_API_KEY]
                                            ,paginationRuleSettings[REST_API_END_CONDITION][REST_API_VALUE]
                                        )                
        
        return RestAPIPaginationRule(
                                            pgRuleType 
                                            ,paginationRuleSettings[REST_API_KEY]
                                            ,paginationRuleSettings[REST_API_EXPRESSION]
                                            ,paginationRuleSettings[REST_API_VALUE_RANGE]
                                            ,endCond
                                        )

    
    
    #Private method to get the API call headers 
    def _getAPICallHeaders(self): 
        hdrStr = ""  
        #Get the headers based on any header set in the config, if any
        for hdr in self.headers:
            if hdrStr == "":
                hdrStr = f"\"" + hdr.key + "\": \"" + hdr.value + "\""
            else:             
                hdrStr += f", \"" + hdr.key + "\": \"" + hdr.value + "\""

        #Next, loop throug the credentials and add any header specific item
        for crd in self.credentials:
            if crd.apiArea == RestAPIArea.Headers:
                if hdrStr == "":
                    hdrStr = f"\"" + crd.key + "\": \"" + crd.value + "\""
                else:             
                    hdrStr += f", \"" + crd.key + "\": \"" + crd.value + "\""

        return json.loads("{" + hdrStr + "}")   


    #Private method to get the API call params
    def _getAPICallParams(self): 
        paramStr = ""  
        #Get the params based on any param set in the config, if any
        for param in self.params:
            if paramStr == "":
                paramStr = f"\"" + param.key + "\": \"" + param.value + "\""
            else:             
                paramStr += f", \"" + param.key + "\": \"" + param.value + "\""

        #Next, loop throug the credentials and add any param specific item
        for crd in self.credentials:
            if crd.apiArea == RestAPIArea.Params:
                if paramStr == "":
                    paramStr = f"\"" + crd.key + "\": \"" + crd.value + "\""
                else:             
                    paramStr += f", \"" + crd.key + "\": \"" + crd.value + "\""

        return json.loads("{" + paramStr + "}") 


    #Private method to make an API call and return the Response object
    def _makeAPICall(self, apiVerb: RestAPIVerbType, url, headers = None, params = None, body = None):  
        apiURL = url
        apiHeaders = headers
        apiParams = params
        apiBody = body
        authToken = None
        resp = None 
        #-------------------------------------------------------------
        #Process the different auth types
        #-------------------------------------------------------------      
        match self.auth.authType:
            case RestAPIAuthorizationType.Basic:
                #Get the username & password from the secret credentials
                for crd in self.credentials:
                    match crd.type:
                        case RestAPIDictionaryItemType.UserName:
                            userName = crd.value
                        case RestAPIDictionaryItemType.Password:
                            pwd = crd.value
                
                #Create the Basic Auth token
                authToken = HTTPBasicAuth(userName, pwd)

            case RestAPIAuthorizationType.BearerToken:
                #Get the bearer token from the secret credentials
                for crd in self.credentials:
                    match crd.type:
                        case RestAPIDictionaryItemType.BearerToken:
                            bearerToken = crd.value
                        case _:
                            raise ValueError("No Bearer Token details found in the secret credentials") 

                #Add the bearer token to the header
                apiHeaders["Authorization"] = bearerToken

            case RestAPIAuthorizationType.APIKey:
                for crd in self.credentials:
                    match crd.type:
                        case RestAPIDictionaryItemType.APIKey:
                            apiKeyName = crd.key
                            apiKeyValue = crd.value
                            apiKeyArea = crd.apiArea
                        case _:
                            raise ValueError("No API Key details found in the secret credentials")

                #Add the API key to headers or params, based on the config
                if apiKeyArea == RestAPIArea.Headers:
                    apiHeaders[apiKeyName] = apiKeyValue
                if apiKeyArea == RestAPIArea.Params:
                    apiParams[apiKeyName] = apiKeyValue

            case RestAPIAuthorizationType.DynamicBearerToken:
                apiHeaders["Authorization"] = f"Token {self.dynamicBearerToken}"


            #**** TBD: Other auth types ***

        #-------------------------------------------------------------
        #Make the API call, based on the specified verb
        #-------------------------------------------------------------
        t.sleep(1)    #Sleep to avoid throttling
        
        match apiVerb:
            case RestAPIVerbType.Get:
                resp = requests.get(apiURL, auth = authToken, headers = apiHeaders, params = apiParams) 
            case RestAPIVerbType.Post:
                requests.post(apiURL, apiBody, auth = authToken, headers = apiHeaders, params = apiParams)
            case RestAPIVerbType.Put:
                requests.put(apiURL, apiBody, auth = authToken, headers = apiHeaders, params = apiParams)
            case RestAPIVerbType.Delete:
                requests.delete(apiURL, auth = authToken, headers = apiHeaders)

        #Return the Response object
        return resp

   
    
    #Private method to union 2 dataframes
    def _unionDataframes(self, df1, df2):
        #Add columns in df2 that are missing from df1
        for column in [column for column in df1.columns if column not in df2.columns]:
            df2 = df2.withColumn(column, lit(None)) 
                              

        #Add columns in df1 that are missing from df2
        for column in [column for column in df2.columns if column not in df1.columns]:
            df1 = df1.withColumn(column, lit(None))                
        
        #Return the union dataframe
        return df2.unionByName(df1, True)


    #Private method to get the response node specified in the end-condition settings
    def _getEndConditionNode(self, apiResponse):
        #Get the end condtion from cfg
        endCond = self.paginationRuleSettings.endCondition         
        #The node hierarchy is specified as ">" separated string in the end-condition key.
        #Split it into an array of node names
        nodeNames = endCond.key.split(">")
        #Load the API response into a Json object for traversal
        jsonData = json.loads(apiResponse)
        #Variables for traversal
        thisNode = None
        parentNode = None
        #Loop through the node names and traverse the json
        for nodeName in nodeNames:   
            if nodeName == "$":
                thisNode = parentNode = jsonData
            else:
                if isinstance(parentNode, dict):
                    try:
                        thisNode = parentNode[nodeName]
                    except:
                        thisNode = None
                if isinstance(parentNode, list):
                    try:
                        thisNode = parentNode[0][nodeName]
                    except:
                        thisNode = None
                if isinstance(parentNode, str):  
                    thisNode = None
            parentNode = thisNode

        return thisNode

    
    #Private method to check if the end condition that breaks pagination loop has been met or not
    def _endConditionMet(self, apiResponse) :
        result = False
        #Get the end condtion from cfg
        endCond = self.paginationRuleSettings.endCondition 
        #Get the node to test for end consition
        if endCond.apiArea == RestAPIArea.Body:            
            endCondNode = self._getEndConditionNode(apiResponse.content)
        if endCond.apiArea == RestAPIArea.Headers:            
            endCondNode = self._getEndConditionNode(apiResponse.headers)

        #----------------------------------------------------------------------------
        #Case: End condition is that the response should have a blank dictionary or list.
        #This happens when the last API call returns a blank response. 
        #Examples:
        #{} OR [] OR {Data:[]}
        #----------------------------------------------------------------------------
        if endCond.value.strip().lower() == "blank":
            if isinstance(endCondNode, dict) or isinstance(endCondNode, list):
                result = True if len(endCondNode) == 0 else False
                return result

        #----------------------------------------------------------------------------
        #Case: End condition is that the response should have a flag field with a
        #specific value at the last page.
        #Example:
        #{Data:[.....], Complete: True}
        #----------------------------------------------------------------------------
        if isinstance(endCondNode, str):
            result = True if endCondNode.strip().lower() == endCond.value.strip().lower() else False
            return result

        #----------------------------------------------------------------------------
        #Case: End condition is that the response should have a flag field at the last page.
        #Example:
        #{Data:[.....], DateComplete: 01/06/2024}
        #----------------------------------------------------------------------------
        if endCond.value.strip().lower() == "exist":
            result = True if endCondNode is not None else False
            return result              

        #----------------------------------------------------------------------------
        #Case: End condition is that the response should have a specific field with a
        #null value at the last page.
        #Example:
        #{Data:[.....], meta{...,next_cursor : null,....}}
        #----------------------------------------------------------------------------
        if endCond.value.strip().lower() == "blank":
            result = True if endCondNode is None else False
            return result

        #----------------------------------------------------------------------------
        #Case: End condition is that the response does not have a flag field at the 
        #last page.
        #Example:
        #The last page does not have a next page link.
        #All other pages:   {"data":[{"id":1,"name":"tom"},{"id":2,"name":"dick"},{"id":3,"name":"harry"}],"@nextLink":"next page link here!"}
        #Last page:         {"data":[{"id":1,"name":"tom"},{"id":2,"name":"dick"},{"id":3,"name":"harry"}]}
        #----------------------------------------------------------------------------
        if endCond.value.strip().lower() == "empty":
            result = True if endCondNode is None else False 
            return result

        # **** TBD: Other cases ***


    #Private method to load and return a Dataframe from API response
    def _loadDataFrameFromResponse(self, apiResponse):
        db = self.spark.sparkContext.parallelize([apiResponse.text])
        df = self.spark.read.json(db) 

        #If the API response has a particular node that has all the data, return that node  
        if self.dataNode != "": 
            df = df.select(self.dataNode)
            if self.primaryKeys:    #If there are primary keys
                for primaryKey in self.primaryKeys:
                    df = df.withColumn(primaryKey, F.col((self.dataNode + "." if self.primaryKeyPath == "" else self.primaryKeyPath) + primaryKey).alias(primaryKey.strip())) 
        return df


    #Private method to return the current date & time for download folder
    def _getFolderPathAsCurrDateTime(self):
        #tz = timezone("Australia/Sydney")
        today = datetime.now()
        return today.strftime("%Y/%m/%d/%H-%M-%S")


    #Private method to get the parent filter
    def _getParentFilter(self):
        return self.parentFilter



    #Private method to return the API data
    def _loadTable(self, relativeURL, dataFolderPath):
        dfFullData = None
        #-------------------------------------------------------------
        #Get the headers and params ready for the API call, if any
        #-------------------------------------------------------------
        apiHeaders = self._getAPICallHeaders()
        apiParams = self._getAPICallParams() 

        reltvURL = relativeURL

        #-------------------------------------------------------------
        #Make the API call, based on whether this API is paginated or not
        #-------------------------------------------------------------
        if self.paginationRuleSettings:     #This API is paginated
            #-------------------------------------------------------------------
            #Set the pagination loop settings
            #-------------------------------------------------------------------
            loopMinVal = self.paginationRuleSettings.getMinValue()
            loopMaxVal = self.paginationRuleSettings.getMaxValue()  
            loopIncr = self.paginationRuleSettings.getIncrementalValue()
            pgOffset = loopMinVal
            
            
            if loopMaxVal is None:  #Pagination has an end-condition specified that breaks the loop
                #Set up an infinite loop that will break when end condition is met
                while True:     
                    if self.paginationRuleSettings.type == RestAPIPaginationRuleType.QueryParameters: #Pagination info passed as params
                        apiParams[self.paginationRuleSettings.key] = pgOffset
                    if self.paginationRuleSettings.type == RestAPIPaginationRuleType.Headers: #Pagination info passed in headers
                        apiHeaders[self.paginationRuleSettings.key] = pgOffset 
                    if self.paginationRuleSettings.type == RestAPIPaginationRuleType.AbsoluteUrl:    #Pagination info is part of the URL
                        reltvURL = self.relativeURL.replace("\{id\}", pgOffset)       

                    #Make the API call     
                    print("Downloading page #", pgOffset, " of ", reltvURL)               
                    resp = self._makeAPICall(self.verb, self.baseURL + reltvURL, apiHeaders, apiParams)  

                    if resp.status_code != 200:
                        raise Exception("API call failed with status code " + str(resp.status_code))                    

                    #Get the API data
                    dfData = self._loadDataFrameFromResponse(resp)

                    #Save the API data as json files under the File section of the Raw Lakehouse
                    if dfData.count()> 0:  
                        dfData.write.format('json').mode("overwrite").save(dataFolderPath + "/" + str(pgOffset))
                        
                    #Increment page offset
                    pgOffset += loopIncr 

                    #Break out of the loop if the specified end-consition is met
                    if self._endConditionMet(resp):
                        break 

                #Read from the saved json files
                dfFullData = (self.spark.read.format("json") 
                                            .option("recursiveFileLookup", "true") 
                                            .option("pathGlobFilter","*.json")
                                            .load(dataFolderPath, header=True))     

            else:   #Pagination is based solely on the value range
                
                #Loop through the value range and make the API calls for each page             
                while pgOffset <= loopMaxVal:                    
                    if self.paginationRuleSettings.type == RestAPIPaginationRuleType.QueryParameters: #Pagination info passed as params
                        apiParams[self.paginationRuleSettings.key] = pgOffset
                    if self.paginationRuleSettings.type == RestAPIPaginationRuleType.Headers: #Pagination info passed in headers
                        apiHeaders[self.paginationRuleSettings.key] = pgOffset  
                    if self.paginationRuleSettings.type == RestAPIPaginationRuleType.AbsoluteUrl:    #Pagination info is part of the URL
                        reltvURL = self.relativeURL.replace("\{id\}", pgOffset)                                               
                   
                    #Make the API call  
                    print("Downloading page #", pgOffset, " of ", reltvURL)                     
                    resp = self._makeAPICall(self.verb, self.baseURL + reltvURL, apiHeaders, apiParams)

                    if resp.status_code != 200:
                        raise Exception("API call failed with status code " + str(resp.status_code))

                    #Get the API data
                    dfData = self._loadDataFrameFromResponse(resp)

                    #Save the API data as json files under the File section of the Raw Lakehouse
                    if dfData.count()> 0:                        
                        dfData.write.format('json').mode("overwrite").save(dataFolderPath + "/" + str(pgOffset))

                    #Increment page offset
                    pgOffset += loopIncr 

                #Read from the saved json files
                dfFullData = (self.spark.read.format("json") 
                                            .option("recursiveFileLookup", "true") 
                                            .option("pathGlobFilter","*.json")
                                            .load(dataFolderPath,header=True)) 

        else:   #This API is not paginated
           
            #Make the single API call
            print("Downloading ", reltvURL)   
            resp = self._makeAPICall(self.verb, self.baseURL + reltvURL, apiHeaders, apiParams)

            if resp.status_code != 200:
                raise Exception("API call failed with status code " + str(resp.status_code))

            #Load the response into a dataframe
            dfFullData = self._loadDataFrameFromResponse(resp)
            #Save the API data as json files under the File section of the Raw Lakehouse
            if dfFullData.count()> 0:
                dfFullData.write.format('json').mode("overwrite").save(dataFolderPath)

        #Return the data
        return dfFullData
    

    #===========================================================
    #Public methods
    #===========================================================
    def loadTable(self):
        dfFullData = None
        rawLakehouseLocation = FabricLakehouseLocation(self.constants["LAKEHOUSE_RAW_STAGE_NAME"], self.rawWorkSpaceId, self.rawLakeHouseId)
        rawFabricFolderLocation = FabricFolderLocation(self.sourceName + "/" + self._getFolderPathAsCurrDateTime(), rawLakehouseLocation)
        dataFolderPath = rawFabricFolderLocation.abfss_path()

        if self.parentSourceId:   #This is a child API
            #Get the parent config record
            fabricDataInterface = FabricDataInterface()
            configTablePath = convertURL(self.constants["DEFAULT_EXTRACTMANIFEST_TABLE"], self.constants["LAKEHOUSE_CONTROL_STAGE_NAME"])
            dcfg = fabricDataInterface.loadIngestionConfiguration("", configTablePath)
            parentSrcCfg = dcfg.where("SourceID = "+ str(self.parentSourceId)).collect()

            if len(parentSrcCfg) == 0:
                raise Exception("No config record exists for Parent Id " + str(self.parentSourceId))
            else:
                parentTrustedWorkSpace = parentSrcCfg[0][REST_API_TRUSTED_WORKSPACE]
                parentTrustedLakeHouse = parentSrcCfg[0][REST_API_TRUSTED_LAKEHOUSE]
                parentTrustedTableName = parentSrcCfg[0][REST_API_DESTINATION_NAME]
                parentPrimaryKeys = parentSrcCfg[0][REST_API_PRIMARY_KEY]
                parentPKStr = ",".join(parentPrimaryKeys)

                #Get the parent filter, if any
                parentFilter = self._getParentFilter()

                #Get the parent records    
                parenttrustedLakehouseLocation = FabricLakehouseLocation(self.constants["LAKEHOUSE_TRUSTED_STAGE_NAME"], parentTrustedWorkSpace, parentTrustedLakeHouse)
                trustedFabricTableLocation = FabricTableLocation(parentTrustedTableName, parenttrustedLakehouseLocation)

                allParents = fabricDataInterface.loadLatestDeltaTable(trustedFabricTableLocation, parentFilter).select(parentPKStr).collect()

                print(len(allParents))
                #i = 1            
                             
                #Loop through the parent records               
                for thisParent in allParents:
                    #Make the child API call and get data
                    rltvUrl = self.relativeURL.replace("{parentId}", str(thisParent[parentPKStr]))
                    dfData = self._loadTable(rltvUrl, dataFolderPath + "/" + str(thisParent[parentPKStr])) 
                    
                    #i = i+1
                    #if i>10:
                       #break
                

                #Read from the saved json files
                dfFullData = (self.spark.read.format("json") 
                                            .option("recursiveFileLookup", "true") 
                                            .option("pathGlobFilter","*.json")
                                            .load(dataFolderPath,header=True))                

        else: #This is a parent API
            #Get the data from the API call
            dfFullData = self._loadTable(self.relativeURL, dataFolderPath)            
                
        #If the API response has a particular "data" node the flatten the dataframe before returning 
        if self.dataNode != "": 
            dfFullData = dfFullData.select(F.explode(F.col(self.dataNode)).alias(self.dataNode))
            if self.primaryKeys:    #If there are primary keys
                for primaryKey in self.primaryKeys:                    
                    dfFullData = dfFullData.withColumn(primaryKey, F.col((self.dataNode + "." if self.primaryKeyPath == "" else self.primaryKeyPath) + primaryKey).alias(primaryKey.strip())) 

            #Convert the Json column to string
            dfFullData = dfFullData.withColumn(self.dataNode + "_str", to_json(self.dataNode)) #temp string column
            dfFullData = dfFullData.drop(self.dataNode)     #Drop the Json column
            dfFullData = dfFullData.withColumnRenamed(self.dataNode + "_str", self.dataNode) #Rename the string column to the Json column

        #Return the data
        return dfFullData
