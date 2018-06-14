<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#orgcbc66f0">1. Skill Similarity Matching Algorithm</a></li>
<li><a href="#orgdd71621">2. Problem</a></li>
<li><a href="#orgb729978">3. Key Idea</a></li>
<li><a href="#org06e745b">4. Algorithm</a></li>
<li><a href="#org1537588">5. References</a></li>
</ul>
</div>
</div>

<a id="orgcbc66f0"></a>

# Skill Similarity Matching Algorithm

  This document focus on how similarity skill matching is happening in the filter-api. Usually two type of skill matching happens in the system
exact match and similar match. This document helps to understand the latter.


<a id="orgdd71621"></a>

# Problem

  We cannot always calculate the skills score based on exact match. For e.g: Lets say, If the required skills set are "javascript" and "postgres", but candidate have the skills of "javascript" and "mysql".
In this case we can calculate the skills score more accurately if system able to recognize that "mysql" and "postgres" are similar.


<a id="orgb729978"></a>

# Key Idea

  Create huge index of similar skills based on the fact that if two skills "often" appear together in the job description, both may be similar.
For e.g: If "angular.js" and "javascript" occur together in say 100 jobs, these both the skills are similar


<a id="org06e745b"></a>

# Algorithm

1.  We scrapped around 9k jobs from naukri in different types of jobs including (frontend, backend, python, devops, ruby, java, etc..)
2.  We created a index file "skills.index" by applying Latent Semantic Analysis over the collected job documents from naukri. (please read the references to understand LSA)
3.  We use python gensim (https://radimrehurek.com/gensim/) for calculating index file
3.  Index file have the ability to return "most-similar" skills for any given skill.
4.  We exposed endpoints that takes a single skill and returns the "most-similar" skills(skills app of filter-api)


<a id="org1537588"></a>

# References

-   <https://technowiki.wordpress.com/2011/08/27/latent-semantic-analysis-lsa-tutorial/>
-   <https://groups.google.com/forum/#!topic/gensim/xOcqMCtwHyE>
-   <https://www.kernix.com/blog/similarity-measure-of-textual-documents_p12>
-   <https://roshansanthosh.wordpress.com/2016/02/18/evaluating-term-and-document-similarity-using-latent-semantic-analysis/>
-   <http://blog.christianperone.com/2013/09/machine-learning-cosine-similarity-for-vector-space-models-part-iii/>
-   <https://de.dariah.eu/tatom/working_with_text.html>
-   <http://brandonrose.org/clustering>
-   <https://linkurio.us/blog/hr-analytics-graphs-match-person-job/>
-   <https://www.slideshare.net/Linkurious/hr-analytics-and-graphs-job-recommendations>
-   <https://gooroo.io/GoorooTHINK/Article/16229/A-network-graph-of-technical-skills/17450#.WQx5Z3aGPZs>
-   <http://insights.dice.com/2015/07/01/dice-data-how-tech-skills-connect/>

