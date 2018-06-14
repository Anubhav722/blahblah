# Accounts API

## User Profile API

!!! summary "Description"
    Create User Profile

-----

### URL
> **POST** &nbsp;&nbsp; `/api/accounts`

-----

### Parameters

Name | Data Type | Description
:----------: | :-------------: | :-------------:
**aircto-client-key** | string | **Unique identifier for your profile**
**aircto-client-secret** | string | **Authentication secret to access service**
**limit** | number | **Resume upload limit**
**label** | string | **Label to identify Token**

------

### Sample Request
```
curl -X POST -H "Authorization: Token <auth_token>" -H "aircto-client-key: <client-key>" -H "aircto-client-secret: <client-secret>" -d {"label": "Aircto", "limit": 20} http://localhost:8000/api/accounts
```
-----

### Sample Response

``` javascript
{
  "label": "Aircto",
  "token": "9e16602faa7cd44813a19f372da8492e67343e90"
}
```

HTTP Status Codes | Reason
:----------: | :-------------:
**201** | User Profile created successfully
**400** | Invalid Data (Bad Request)
**401** | Provided credentials are incorrect/missing

-----
