==============
Filter Resumes
==============

.. http:post:: /api/resume/filter/

This endpoint apply various ranges of filter over the available resumes in the database and returns the list whatever matches.

NOTE: This endpoint accepts filter arguments as GET params and resume_ids as POST params

   :reqheader Authorization: valid user's auth token
			     
   :param skills: skills to be filtered on
   :type skills: list of strings
   :skills_per: percentage of skills to match for
   :type skills_per: int
   :code_per: percentage of coding skills to match for
   :type code_per: int
   :loc: name of the location to match with
   :type loc: list of strings
   :exp_min: minimum years of experience to apply filter
   :type exp_min: int
   :exp_max: maximum years of experience to apply filter
   :type exp_max: int
   :comp: name of the companies to match with
   :type comp: list of strings
   :inst: institution to apply filter. only possible value is 'top'
   :degrees: name of the academic degrees to match with
   :type degrees: list of strings

   :form ids: list of resume ids
	      
   **Example request**

   .. sourcecode:: http
		   
      POST api/resumes/filter/?skills=python,mysql&skills_per=10&exp_min=3&exp_max=7
      Accept: application/json

      {
	"ids": [
	       "ab215a6d-1804-4578-9ac3-0426a8f83bbb",
	       "f1cd9cdb-b299-4bd1-9dba-b12e04bb909a",
	       "11ffef72-2153-425e-8807-dab5e8ff44c9",
	       "797f2aa9-8fa8-424b-81b1-4c3918a88045",
	       "29fb78d1-bfb1-4169-9b15-10b915e809b8",
	       "b00bf6f2-ba6d-4b0a-9cd6-543587ec4551",
	       "3a213925-2f52-410c-99f8-566cdd33e7cf",
	       "bb993371-ed67-440a-8afb-c87c3bc38fbd",
	       "5e9e0729-4b81-4062-bb6b-b80e48a4a203",
	       "ea8e5907-e4dc-4552-892a-09273f28881d"
	       ]
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 OK
      Vary: Accept
      Content-Type: application/json
      
     [
      {
        "id": "ab215a6d-1804-4578-9ac3-0426a8f83bbb",
	"first_name": "Russ",
	"last_name": "Cox",
	"email": "r@google.com",
	"locations": ["bangalore", "mumbai", "chennai"],
	"experience": 4.0,
	"companies": ["Amazon Inc", "Google", "Microsoft"],
	"institutions" ["IIT Delhi", "IIT Madras"],
	"matched_skills": ["python"],
	"resume_location": "https://filter-api.s3.amazon.com/media/resumes/ab215a6d-1804-4578-9ac3-0426a8f83bbb",
	  "related_skills": [{"name": "mysql","related": ["database", "postgres"]}],
      },
    {
        "id": "bdcd15a6d-1804-4578-9ac3-0426a8f83bbb",
	"first_name": "Rob",
	"last_name": "Pike",
	"email": "rob@google.com",
	"locations": ["delhi", "lucknow", "chennai"],
	"experience": 14.0,
	"companies": ["Facebook", "Google", "Microsoft"],
	"institutions" ["IIT Kargpur", "IIT Madras"],
	"matched_skills": ["mysql"],
	"resume_location": "https://filter-api.s3.amazon.com/media/resumes/bdcd15a6d-1804-4578-9ac3-0426a8f83bbb",
	  "related_skills": [{"name": "python","related": ["nlp", "r"]}],
      },
     ]

   :statuscode 200: success. no error
   :statuscode 401: unauthorized. If Authorization header is missing or invalid
		    

