<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#org0bb79d7">1. Filter-API Ranking system</a></li>
<li><a href="#org4b5ea42">2. Coding Ranking</a>
<ul>
<li><a href="#org7623d7f">2.1. Github</a></li>
<li><a href="#org7d138d1">2.2. Stackoverflow</a></li>
<li><a href="#org0d93b99">2.3. Bitbucket</a></li>
<li><a href="#orgc9d1880">2.4. PlayStore</a></li>
<li><a href="#org7456043">2.5. AppStore</a></li>
</ul>
</li>
<li><a href="#org965d16d">3. Skill Ranking</a></li>
<li><a href="#org0cfd393">4. Social Ranking</a>
<ul>
<li><a href="#org537dd0b">4.1. Website</a></li>
<li><a href="#org507c53f">4.2. Blog (There could be multiple blog URLs)</a></li>
</ul>
</li>
</ul>
</div>
</div>

<a id="org0bb79d7"></a>

# Filter-API Ranking system

-   Ranking is one of the main functionaliy of the filter-api. This is usually done asynchoronously (via celery tasks)
-   The ranking system is broadly classified into three types. Coding, Skill and Social
-   We can add other types also going forward.


<a id="org4b5ea42"></a>

# Coding Ranking


<a id="org7623d7f"></a>

## Github

-   Reputation-Score
    -   Based On: No of followers
    -   First calculate: how long the user is using the Github based on the time he signed up.
    -   This value can be one of the New, Medium or Old.
    -   Based on this value we allocate score according to the mapping present in resume/utils/ranking/github.py
    -   The maximum score any user can get is 0.2
-   Contribution-Score
    -   Based On: No of repos
    -   Based on the number of repos, we allocate score according to the `USER_CONTRIBUTION_MAPPING` in resume/utils/ranking/github.py
    -   The maximum score any user can get is 0.6
-   Activity-Score
    -   Based on: How often he uses github
    -   We divide user into two broad categories ACTIVE or INACTIVE
    -   Active User would get the score of 0.2
    -   Inactive user would get the score of 0.1
    -   The maximum score any user can get is 0.2
-   Total-Score
    -   Total score is always the sum of reputation, contribution and activity scores.
    -   i.e: 0.2 + 0.6 + 0.2
    -   The maximum score cannot exceed 1


<a id="org7d138d1"></a>

## Stackoverflow

-   Reputation-Score
    -   Based on: stack_overflow_reputation, badges_count and followers_count
    -   We also categorize user whether he/she is NEW, MEDIUM or OLD based how long he/she is using the stackoverflow
    -   Each category have their own set of score
    -   The maximum score one can get is 0.3
-   Contribution-Score
    -   Based on: number of answers and how many of them are accepted.
    -   The maximum score one can get is 0.1
-   Activity-Score
    -   Based on: How often he/she uses stackoverflow
    -   Active user get 0.2 while Inactive user get 0.1
    -   The maximum score one can get is 0.2
-   Total Score
    -   Sum of Reputation, Contribution and Activity score


<a id="org0d93b99"></a>

## Bitbucket

-   Exactly same as github scoring system


<a id="orgc9d1880"></a>

## PlayStore

-   Reputation
    -   Based on: App rating in the App store
    -   Get the app rating and return app_rating/10
    -   The maximum value it can have is 0.5
-   Contribution
    -   Based on: Number.of app downloads in the app store
    -   Based on that value the score is assigned from 0.5 to 2.5
    -   The maximum value it can have is 2.5
-   Activity
    -   Based on: When was the last update for the app is released
    -   If its less than 3 months, score of 2.5 is assigned
    -   Its its greater than 3 months, score of 1.2 is assigned
    -   The maximum value it can have is 2.5


<a id="org7456043"></a>

## AppStore

-   Reputation
    -   Based on: ratings of current version and all-versions
    -   the maximum value it can have is 0.5
-   Contribution
    -   Based on: whether app's developer name matches with candidate name
    -   the maximum value it can have is 0.2
-   Activity
    -   Exactly same as calculated for playstore.
    -   Except here the threshold value is 6 months (whether update is released)


<a id="org965d16d"></a>

# Skill Ranking

Skill ranking is calculated dynamically based on supplied skills. It is helpful to identify how good the candidate is with respect to the given skills requirements

-   Its further sub divided into two types. Exact match and Similarity Match
-   Exact match is simple. It try to match the supplied skill directly with resume (e.g: javascript -> javascript)
-   Similarity match is based on Latent Semantic Analysis (explained in different doc) (e.g: mysql -> postgres)
-   Exact match gets the complete score, where similarity match gets half the score
-   Total skill score is combination of exact match and similarity match
-   The maximum score it can get is 1.0 (only if all the required skills are exactly matched)
-   for e.g: Lets say resume have skills "javascript" and "postgres". And lets say required skills are "javascript" and "mysql". Candidate will get 75% match (0.75 score)


<a id="org0cfd393"></a>

# Social Ranking


<a id="org537dd0b"></a>

## Website

-   Reputation
    -   Based on: Alexa ranking
    -   Based on alexa ranking the score is assigned according to the `WEBSITE_REPUTATION_MAPPING` in resume/utils/ranking/website.py
    -   Score can range from 0.02 to 0.2
    -   The maximum score it can get is 0.2
-   Contribution
    -   Based on: Whether candidate email matches with website domain name registration
    -   The maximum score it can have is 0.6
-   Activity
    -   NA


<a id="org507c53f"></a>

## Blog (There could be multiple blog URLs)

-   Reputation
    -   Based on: Alexa ranking. <http://www.alexa.com/siteinfo>
    -   The maximum value it can have is 0.2
-   Contribution
    -   Based on: no of posts
    -   The maximum value it can have is 0.4
-   Activity
    -   Based on: date of the latest post
    -   The maximum value it can have is 0.4

