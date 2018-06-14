==================
Sync Resume Detail
==================

.. http:post:: /api/resume/sync/
	      
This endpoint will sync first_name, last_name and email information for specific resume_id

   :reqheader Authorization: valid user's auth token

   **Example request**

   .. sourcecode:: http
		   
      POST /api/resume/sync/
      Accept: application/json

      {
        "resume_id": "ea8e5907-e4dc-4552-892a-09273f28881d",
	"first_name": "Russ",
	"last_name": "Cox",
	"email": "r@google.com",
      }


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 OK
      Vary: Accept
      Content-Type: application/json
      
      {
        "message": "success",
      }

   :statuscode 201: success. no error
   :statuscode 401: unauthorized. If Authorization header is missing or invalid
   :statuscode 404: badrequest. If resume_id is missing or invalid.

