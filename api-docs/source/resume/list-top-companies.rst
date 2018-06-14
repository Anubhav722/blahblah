=======================
List Top Companies
=======================

.. http:get:: /api/resume/companies/top/

This simple endpoint returns lists of top 100 companies(india) on the backend. Top companies are chosed based their rank

   **Example request**

   .. sourcecode:: http
		   
      GET /api/resume/companies/top/
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/javascript

      [
        {
	  "name": "Google"
	},
	{
	  "name": "Facebook"
	},
	{
	  "name": "Amazon"
	},
	{
	  "name": "Apple"
	},
	{
	  "name": "Microsoft"
	},
	{
	  "name": "Flipkart"
	},
	{
	  "name": "Wipro"
	},
	{
	  "name": "TCS"
	},
	{
	  "name": "CTS"
	},
	{
	  "name": "Infosys"
	}
      ]

   :statuscode 200: success. no error
