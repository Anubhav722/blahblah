==============
Related Skills
==============

.. http:get:: /api/skill/related/?skills=<skill-name>

   Get the list of related skills for the given `skill-name`

   :reqheader Authorization: token to authenticate

   **Example request**

   .. sourcecode:: http
		   
      GET /api/skill/related/?skill=python
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/javascript
      
      {
        "message": "success",
	"related": [
		     "data-science",
		     "data-analysis",
		     "natural-language-processing",
		     "algorithms",
		     "predictive-maintenance",
		     "big-data",
		     "statistical-analysis",
		     "r",
		     "predictive-modeling",
		     "nlp"
		   ]
      }

   :statuscode 200: success. no error
   :statuscode 401: Unauthorized. If Authorization header is either invalid or missing
