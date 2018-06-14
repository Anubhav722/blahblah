<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#org97449df">1. Resume Extraction</a></li>
<li><a href="#org79f68fc">2. Extracting plain text</a></li>
<li><a href="#org3ff0ea8">3. Basic Information</a></li>
<li><a href="#orge7ceb78">4. URLs</a></li>
<li><a href="#orgbe1e906">5. Locations(city or state)</a></li>
<li><a href="#org29e74be">6. Companies</a></li>
<li><a href="#org7c596d8">7. Institutions</a></li>
<li><a href="#org00691ec">8. Total Years of Experience</a></li>
</ul>
</div>
</div>

<a id="org97449df"></a>

# Resume Extraction

Resume extraction in filter-api is done in two ways. Quick extraction (Synchronously) and Deep extraction(Asynchronously via tasks)
Following are the total information we are extracting from the resume currently


<a id="org79f68fc"></a>

# Extracting plain text

-   We use tika server. <https://github.com/chrismattmann/tika-python>
-   used to extract doc, docx and pdf
-   We use ocr to extract plain content from "image-based" resumes. <https://pypi.python.org/pypi/pytesseract>


<a id="org3ff0ea8"></a>

# Basic Information

We use thrid party repo to extract basic details of the candidate from the resume. <https://github.com/antonydeepak/ResumeParser>

-   FirstName
-   LastName
-   Email
-   Contact Number


<a id="orge7ceb78"></a>

# URLs

Extracted based on regexp. We also categorize the URLs

-   URL is categorized based on known list present in `resume/utils/url_list.py`
-   Every URL would fall in any of the following categories
    -   Contribution
    -   Coding
    -   Blog
    -   Forums
    -   Social
    -   Apps
    -   Others/Misc


<a id="orgbe1e906"></a>

# Locations(city or state)

We extract current locations of the candidate by following patterns. These pattern includes, splitting the resume to different sections base on the headings. All the headings we are using to split are available at `resume/utils/machine_learning_constants.py`

-   Following are the steps
    -   split the resumes into different sections
    -   match if there exists any locations that match with locations in the database (loaded via fixtures)


<a id="org29e74be"></a>

# Companies

  Companies are basically list of companies that candidate worked with (both past and present). We follow simple technique for company extraction
  we check if there is any match between companies available in the database(loaded via fixtures) with the plain resume content.
NOTE: If any company present in the resume doesn't contain in the database, it wouldn't be considered.


<a id="org7c596d8"></a>

# Institutions

This is exactly same as companies extraction


<a id="org00691ec"></a>

# Total Years of Experience

-   Years of Experience (YOE) is basically the total years of experience the candidate may mentioned in the resumes.
-   We split the resume into different sections based on title (`resume/utils/machine_learning_constants.py`) and we try to find YOE based on some common regexp patterns
-   YOE will be None if either resume doesn't contain (in case of fresher's resume or parser failed to extract)

