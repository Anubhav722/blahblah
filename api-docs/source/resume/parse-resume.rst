============
Parse Resume
============

.. http:post:: /api/resume/internal/

Accepts a resume multi-part file(doc, docx or pdf). parses it and create a resume instance.
This endpoint do two kinds of parsing. Quick parsing(synchronously) and Deep parsing(Asynchronously via tasks queue)

Quick Parsing - Only basic information is extracted (email, phonenumber, first_name, last_name)
Deep Parsing - Information such as experience, companies worked for, education details are extracted

   :reqheader Authorization: valid user's auth token
   :form file: resume file either in one of the supported formats(doc, docx, pdf)

   **Example request**

   .. sourcecode:: http
		   
      POST /api/resume/internal/
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 OK
      Vary: Accept
      Content-Type: application/json
      
      {
        "id": "mypos",
	"first_name": "Russ",
	"last_name": "Cox",
	"email": "r@google.com",
	"phones": "+919876543210",
	"address": "Indirangar, Bangalore, India",
	"urls": ["https://github.com/rsc"]
      }

   :statuscode 201: success. no error
   :statuscode 401: unauthorized. If Authorization header is missing or invalid
   :statuscode 400: badrequest. If file is missing or invalid format
		    

