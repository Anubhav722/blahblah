<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#orgdc3243e">1. Filter-API-Architecture</a></li>
</ul>
</div>
</div>

<a id="orgdc3243e"></a>

# Filter-API-Architecture

-   Two Key Functionalities: Extracts the resume and calculate ranking.
-   Extraction
    -   Done in two ways
    -   Quick extraction (Synchronously)
        -   Basic information (first-name, last-name, phone-number and email)
        -   All the URLs in the resume
    -   Deep extraction (Asynchronously via tasks)
        -   All the URLs in the resume
        -   Basic information (first-name, last-name, phone-number and email)
        -   Locations of the candidate
        -   Companies worked for (both present and past)
        -   Institutions
        -   Total Work Experience
-   Calculate Ranking
    -   Skill Ranking
    -   Code Ranking
        -   Github
        -   Stackoverflow
        -   Bitbucket
        -   AppStore (iOS)
        -   PlayStore (Android)
    -   Social Ranking
        -   Blog
        -   Website

