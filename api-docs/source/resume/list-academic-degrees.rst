================
Academic Degrees
================

.. http:get:: /api/resume/degrees/

This simple endpoint returns lists of possible academic degrees along with its short and long names

   **Example request**

   .. sourcecode:: http
		   
      GET /api/resume/degrees/
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/javascript

      [
        {
	  "long_name": "bachelor of engineering",
	  "short_name": "b.e"
	},
	{
	  "long_name": "bachelor of technology",
	  "short_name": "b.tech"
	},
	{
	  "long_name": "master of technology",
	  "short_name": "m.tech"
	},
	{
	  "long_name": "master of science",
	  "short_name": "m.sc"
	},
	{
	  "long_name": "master of science",
	  "short_name": "m.s"
	},
	{
	  "long_name": "bachelor of science",
	  "short_name": "b.sc"
	},
	{
	  "long_name": "doctrate",
	  "short_name": "ph.d"
	},
	{
	  "long_name": "master of business administration",
	  "short_name": "mba"
	},
	{
	  "long_name": "master of computer application",
	  "short_name": "mca"
	},
	{
	  "long_name": "bachelor of computer application",
	  "short_name": "bca"
	},
	{
	  "long_name": "bachelor of science",
	  "short_name": "b.s"
	},
	{
	  "long_name": "master of philosophy",
	  "short_name": "m.phil"
	},
	{
	  "long_name": "bachelor of arts",
	  "short_name": "b.a"
	},
	{
	  "long_name": "master of arts",
	  "short_name": "m.a"
	}
      ]

   :statuscode 200: success. no error

