=============
Filter Detail
=============

.. http:get:: /api/resume/filter/<resume-id>/

This endpoint return more detail about specific resume given in 'resume_id' includding details like coding score, social score, academic degrees.. etc

   :reqheader Authorization: valid user's auth token
			     
   :param resume_id: resume_id to be retrieved detail
   :type resume_id: UUID
	      
   **Example request**

   .. sourcecode:: http
		   
      GET api/resumes/filter/ab215a6d-1804-4578-9ac3-0426a8f83bbb/?skills=python,mysql
      Accept: application/json

   **Example response**:
   
   .. sourcecode:: http

      HTTP/1.1 201 OK
      Vary: Accept
      Content-Type: application/json

     {
     "first_name": "pawan",
     "last_name": "",
     "email": "pawansahai@live.com",
     "experience": 2.0,
     "file_name": "cb41a0bf-934e-509a-83e9-c8ad9a28265f.pdf",
     "phone_number": "+917045344958",
     "parse_status": 1,
     "id": "32a7a993-a6e9-4b4e-a7c4-2bc9a69708d6",
     "resume_location": "https://parser.aircto.in/media/d2924c06-71e0-4475-a945-bd8f1a5a4dc6.pdf",
     "created_date": "2017-06-14T14:38:14.407000Z",
     "score": [
	        {
		   "data": [
		             {
			       "obtained": 0.66,
			       "data": [
            {
              "count": 1735,
              "name": "Reputation"
            },
            {
              "count": 1,
              "name": "Gold Badges"
            },
            {
              "count": 20,
              "name": "Silver Badges"
            },
            {
              "count": 29,
              "name": "Bronze Badges"
            },
            {
              "count": 17,
              "name": "Total number of questions"
            },
            {
              "count": 26,
              "name": "Total number of answers"
            },
            {
              "count": "8 yrs 5 mos",
              "name": "Account Created"
            },
            {
              "count": "15 days",
              "name": "Last Activity"
            }
          ],
          "type": "stackoverflow",
          "url": "http://stackoverflow.com/users/56183"
        },
        {
          "obtained": 0.21,
          "data": [
            {
              "count": 1,
              "name": "Followers"
            },
            {
              "count": 11,
              "name": "Following"
            },
            {
              "count": 15,
              "name": "Repositories"
            },
            {
              "count": 1,
              "name": "Gists"
            },
            {
              "count": "4 yrs 5 mos",
              "name": "Account Created"
            },
            {
              "count": "16 days",
              "name": "Last Activity"
            }
          ],
          "type": "github",
          "url": "https://github.com/gandhirahul"
        }
      ],
      "name": "coding"
    },
    {
      "data": [
        {
          "obtained": 0.68,
          "data": [
            {
              "count": 15,
              "name": "Total Posts"
            },
            {
              "count": "2017-06-21",
              "name": "Latest Post"
            }
          ],
          "type": "blog",
          "url": "https://aircto.com/blog/"
        },
        {
          "obtained": 0.0,
          "data": [
            {
              "count": null,
              "name": "Alexa Ranking"
            },
            {
              "count": "pawansahai@live.com",
              "name": "Email"
            }
          ],
          "type": "website",
          "url": ""
        }
      ],
      "name": "social"
    },
    {
      "data": [
        {
          "obtained": 1.55,
          "coding_score": 0.87,
          "total": 5,
          "social_score": 0.68,
          "skill_score": 0.0
        }
      ],
      "name": "Ranking"
    },
    {
      "data": [
        {
          "obtained": 0,
          "skills": []
        }
      ],
      "name": "skills"
    },

     "urls": [
               {
	         "url": "http://lawkosh.com",
		 "category": "others"
	       },
	       {
	         "url": "http://ebcexplorer.com",
		 "category": "others"
	       },
	       {
	         "url": "http://workflow.ebcpublishing.in",
		 "category": "others"
	       },
	       {
	         "url": "http://bucketbolt.com",
		 "category": "others"
	       },
	       {
	         "url": "http://uknowva.com",
		 "category": "others"
	       },
	       {
	         "url": "http://uknowa.com",
		 "category": "others"
	       }
      ],
      "locations": [
		     "mumbai",
		     "maharashtra"
		   ],
      "companies": [
		     "ibm"
		   ],
      "institutions": [
		        "visva bharati",
			"institute of management and technology",
			"institute of management",
			"ambalika institute of management and technology"
		      ],
      "matched_skills": [
		          "jquery",
			  "python"
			],
     "related_skills": [
		         {
			   "name": "jms",
			   "related": [
			                "ood"
				      ]
		         },
			 {
			   "name": "linux",
			   "related": [
			                "aws"
				      ]
			 }
		       ],
    "disciplines": [
		     {
		       "long_name": "bachelor of technology",
		       "short_name": "b.tech"
		     },
		     {
		       "long_name": "master of business administration",
		       "short_name": "mba"
		     }
		  ]
    }

   :statuscode 200: success. no error
   :statuscode 401: unauthorized. If Authorization header is missing or invalid
		    

