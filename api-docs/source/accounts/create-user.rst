===========
Create User
===========

.. http:post:: /api/accounts/

   Create a django user and its associated userprofile. It also addes the `client` to userprofile created based headers `HTTP_AIRCTO_CLIENT_KEY` and `HTTP_AIRCTO_CLIENT_SECRET`

   :reqheader HTTP_AIRCTO_CLIENT_KEY: registered client key
   :reqheader HTTP_AIRCTO_CLIENT_SECRET: registered client secret
   :form label: label to identify company
   :form limit: number of resume this particular user can upload

   **Example request**

   .. sourcecode:: http
		   
      POST /api/accounts/
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json
      
      {
        "label": "mypos",
	"token": "0f9477b922ab9474ab202f3420f567eeff16abad"
      }

   :statuscode 200: no error
   :statuscode 401: if headers are missing/invalid


