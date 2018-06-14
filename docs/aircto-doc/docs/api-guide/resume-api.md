# Resume API

!!! summary "Description"
    API to upload the resume to parse.

!!! note "API Host and endpoints"
    **API Host:** [https://parser.aircto.com/](https://parser.aircto.com)  
    **Base API URL:** [https://parser.aircto.com/api/](https://parser.aircto.com/api)  
    **Parse Resume:** [https://parser.aircto.com/api/resumes](https://parser.aircto.com/api/resumes)  
    **Retrieve Parsed Resume Details:** [https://parser.aircto.com/api/resumes/{resume-id}](https://parser.aircto.com/api/resumes/<resume-id>)  

<!-- -------------------------------------------------------------------------------- -->

## Parse Resume

-----

### URL

> **POST** &nbsp;&nbsp; `/api/resumes`

-----

### Parameters

Name | Data Type | Description
:----------: | :-------------: | :-------------:
**file** | file | **Resume File**

------

### Sample Request

!!! note "Note"
    This request should be **multipart/form-data.**

```
curl -X POST -i -H "Authorization: Token <auth-token>" -F file=@"/path/to/your/resume.extension"  https://parser.aircto.com/api/resumes
```
-----

### Sample Response

``` javascript

{
  "status": "processing",
  "resume_id": "c44d1f5c-b772-4543-bf07-f8f4d11486b5"
}

```
-----

<!-- -------------------------------------------------------------------------------- -->

## Retrieve Resume

!!! info "Info"
    **URL types could be:**
    (One might find it in this endpoint as key: `urls`)  
    &nbsp;&nbsp;&nbsp;&nbsp; - **contribution**  
    &nbsp;&nbsp;&nbsp;&nbsp; - **coding**  
    &nbsp;&nbsp;&nbsp;&nbsp; - **social**    
    &nbsp;&nbsp;&nbsp;&nbsp; - **blog**  
    &nbsp;&nbsp;&nbsp;&nbsp; - **forums**  
    &nbsp;&nbsp;&nbsp;&nbsp; - **other**  
    -----
    **Find out, what `parse_status` represents**:  
    &nbsp;&nbsp;&nbsp;&nbsp; **0**: **`processing`** (Means, resume is still in processing state.)  
    &nbsp;&nbsp;&nbsp;&nbsp; **1**: **`processed`** (Means, resume is done with extraction, and details would be available by now.)  

-----

### URL
> **GET** &nbsp;&nbsp; `/api/resumes/<resume-id>`

-----

### Sample Request

```
curl -X GET -H "Authorization: Token <auth_token>" https://parser.aircto.com/api/resumes/<resume-id>
```

-----

### Sample Response

``` javascript

{
    "id": "cf042d64-3503-4d6b-aab0-dcb6012cd25b",
    "created_date": "2018-01-17T11:09:40.637710Z",
    "file_name": "abhijeet_resume.pdf",
    "first_name": "abhijeet",
    "last_name": "kapoor",
    "email": "kapoor@outlook.com",
    "experience": 2.5,
    "phone_number": "+919909999099",
    "parse_status": 1,
    "resume_location": "https://parser.aircto.com/media/cf042d64-3503-4d6b-aab0-dcb6012cd25b.pdf",
    "urls": [
        {
            "url": "https://in.linkedin.com/in/kapoor",
            "category": "social"
        },
        {
            "url": "http://kapoor.github.io",
            "category": "blog"
        },
        {
            "url": "http://github.com/kapoor",
            "category": "contributions"
        }
    ],
    "locations": null,
    "companies": [
        "ola"
    ],
    "institutions": [
        "university of delhi",
        "rajdhani college"
    ],
    "skills_found": [
        "css",
        "c++",
        "sql",
        "java",
        "html",
        "solr",
        "shell",
        "redis",
        "mysql",
        "apache",
        "django",
        "python",
        "mongodb",
        "cassandra",
        "javascript",
        "elasticsearch"
    ],
    "disciplines_found": [
        {
            "long_name": "bachelor of science",
            "short_name": "b.sc"
        },
        {
            "long_name": "master of science",
            "short_name": "m.sc"
        }
    ]
}

```

-----

<!-- -------------------------------------------------------------------------------- -->

## Filter Resumes

!!! note "Note"
    This request should be **application/json.**  
    It should filter resumes which satisfied with your provided input.  
    `resume_ids` would take multiple resumes to apply filter on.  

-----

### URL

> **POST** &nbsp;&nbsp; `/api/resumes/filter/`

------

### Sample Request

``` javascript

{
  "resume_ids": [
    "c44d1f5c-b772-4543-bf07-f8f4d11486b5"
  ],
  "exp_min": 1,
  "exp_max": 2,
  "top_colleges": true,
  "degrees":["b.e","b.tech","m.c.a"],
  "skills": ["golang","python","java","mongodb"],
  "locations":["bangalore","pune","chennai"],
  "companies":["ola", "flipkart","red hat", "amazon"]
}
```
-----

### Sample Response

``` javascript

{
    "data": [
        {
            "top_colleges": {
                "unmatched": [
                    "rajdhani college"
                ],
                "matched": [
                    "university of delhi"
                ]
            },
            "skills": {
                "unmatched": [
                    "golang"
                ],
                "matched": [
                    "python",
                    "java",
                    "mongodb"
                ]
            },
            "companies": {
                "unmatched": [
                    "red hat",
                    "amazon",
                    "flipkart"
                ],
                "matched": ["ola"]
            },
            "locations": {
                "unmatched": [
                    "bangalore",
                    "chennai"
                ],
                "matched": ["pune"]
            },
            "experience": {
                "unmatched": 0,
                "matched": 2
            },
            "degrees": {
                "unmatched": [
                    "m.c.a",
                    "b.tech"
                ],
                "matched": [
                    "b.e"
                ]
            },
            "resume_id": "c44d1f5c-b772-4543-bf07-f8f4d11486b5"
        }
        .....
        .....
    ]
}

```
-----

<!-- -------------------------------------------------------------------------------- -->

## Trial Version
### Validate Trial User

-----

#### URL
> **GET** &nbsp;&nbsp; `/api/resumes/trial-user/validate/?email=<email-address>`

-----

#### Sample Request

```
curl -X GET https://parser.aircto.com/api/resumes/trial-user/validate/?email=<email-address>
```

-----

#### Possible Sample Response
``` javascript
{
  "status": "success",
  "message": "<email-address> is valid."
}
```

``` javascript
{
  "status": "failure",
  "message": "Please use a valid email address."
}
```

``` javascript
{
  "status": "failure",
  "message": "This email has already been used for the trial version."
}
```

-----

<!-- -------------------------------------------------------------------------------- -->

### Retrieve Resume

-----

#### URL
> **GET** &nbsp;&nbsp; `/api/resumes/trial/<resume-id>`

-----

#### Sample Request

```
curl -X GET https://parser.aircto.com/api/resumes/trial/<resume-id>
```

-----

#### Sample Response
``` javascript

{
  "first_name": "shayv",
  "last_name": "akshay",
  "email": "shayv@gmail.com",
  "phone_number": "",
  "parse_status": "completed",
  "resume_id": "1a3e4048-9b15-4c0d-aa2d-1ada3610a0f9",
  "urls": [
    {
      "url": "http://aircto.com/blog",
      "category": "others"
    },
    {
      "url": "http://github.com/username",
      "category": "contributions"
    }
  ]
}

```

-----

<!-- -------------------------------------------------------------------------------- -->

### Parse Resume

-----

#### URL

> **POST** &nbsp;&nbsp; `/api/resumes/trial`

-----

#### Parameters

Name | Data Type | Description
:----------: | :-------------: | :-------------:
**file** | file | **Resume File**
**skills** | string | **Skill set you want to lookup in resume (Comma Separated)**
**email_address** | string | **Email Address of user who wants to try Aircto Filter Service**

------

#### Sample Request

```
curl -X POST -i -F email_address=user@domain.com -F skills=python,django -F file=@"/path/to/your/file.extension"  https://parser.aircto.com/api/resumes/trial
```
-----

#### Sample Response

``` javascript

{
  "status": "processing",
  "resume_id": "109d2f86-b950-4c4a-969e-c888caa849f5"
}
```

-----

<!-- -------------------------------------------------------------------------------- -->

## Skill Suggestion

-----

### URL
> **GET** &nbsp;&nbsp; `/api/resumes/skill-suggestion/?q=<skill-name>`

-----

### Sample Request

```
curl -X GET -H "Authorization: Token <auth_token>" https://parser.aircto.com/api/resumes/skill-suggestion/?q=<skill-name>
```

-----

### Sample Response
``` javascript

{
  "result": [
    "flask",
    "python",
    "pyramid",
    "tornado",
    "django"
  ]
}
```

-----

<!-- -------------------------------------------------------------------------------- -->
