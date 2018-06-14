from rest_framework import serializers
from jarvis.resume.utils.parser_helper import get_matched_degrees

from ..models import (
    Tag, GitHubRepo, GitHub, StackOverflow, Url, MobileApp,
    Resume, ResumeSkills, Skill, Score, Company
)

from .helpers import (
    get_github_scores, get_stackoverflow_scores,
    get_bitbucket_scores, get_blog_scores, get_website_scores,
    get_app_scores
)

from jarvis.resume.api.helpers import (
    get_stackoverflow_details, get_github_details,
    get_bitbucket_details, get_blog_details, get_website_details,
    get_total_score, get_ios_data, get_ios_urls, get_android_data,
    get_android_urls, get_download_url
)

from jarvis.resume.common import skill_match_percent

from urllib2 import urlparse
from django.conf import settings


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name',)

class TagSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize Tag model
    """
    class Meta:
        model = Tag


class GitHubRepoSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize GitHubRepo model
    """
    class Meta:
        model = GitHubRepo


class GitHubUserSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize GitHubUser model
    """
    class Meta:
        model = GitHub


class StackOverflowUserSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize StackOverflowUser model
    """
    class Meta:
        model = StackOverflow
        fields = '__all__'


class UrlSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize Url model
    """
    class Meta:
        model = Url
        fields = ('url', 'category')


class MobileAppSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize MobileApp model
    """
    class Meta:
        model = MobileApp
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    """Serializer used to serialize and de-serialize Score Model"""
    class Meta:
        model = Score
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):

    """Serializer used to serialize and de-serialize Skill Model"""
    class Meta:
        model = Skill
        fields = ('name', 'slug', )


class ResumeSkillsSerializer(serializers.ModelSerializer):
    """Serializer used to serialize and de-serialize ResumeSkills Model"""
    resume = serializers.ReadOnlyField(source='resume')
    skill = serializers.ReadOnlyField(source='skill')

    class Meta:
        model = ResumeSkills
        fields = '__all__'


class ResumeParseInternalSerializer(serializers.ModelSerializer):
    urls = UrlSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number', 'urls'
        )


class ResumeFilterSerializer(serializers.ModelSerializer):
    matched_skills = serializers.SerializerMethodField()
    related_skills = serializers.SerializerMethodField()
    locations = serializers.StringRelatedField(read_only=True, many=True)
    companies = serializers.StringRelatedField(read_only=True, many=True)
    scores = serializers.StringRelatedField(read_only=True, many=True)
    resume_location = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = (
            'id','first_name', 'last_name',
            'locations', 'email', 'experience', 'companies',
            'institutions', 'matched_skills', 'resume_location','scores',
            'related_skills',
        )

    def get_resume_location(self, instance):
        loc = instance.resume_location
        if loc:
            if loc[0] == '/':
                rel = loc.split('/media/')[1]
                return settings.DOMAIN + '/media/' + rel
            return loc
        return ''

    def get_matched_skills(self, instance):
        content = instance.content.lower()
        skills = self.context.get('skills', [])
        matched =  []
        for skill in skills:
            if skill in content:
                matched.append(skill)
        matched = [x for x in matched if x.strip()]
        return set(matched)

    def get_related_skills(self, instance):
        content = instance.content.lower()
        allrelated = self.context.get('related_skills', [])
        related = []
        for rel in allrelated:
            if rel in content:
                related.append(rel)

        related = [x for x in related if x.strip()]
        return set(related)

class ResumeSerializer(serializers.ModelSerializer):
    """
        Serializer used to serialize and de-serialize Resume model
    """

    urls = UrlSerializer(many=True, read_only=True)
    resume_location = serializers.SerializerMethodField('download_url')
    locations = serializers.SerializerMethodField('location_name')
    companies = serializers.SerializerMethodField('company_name')
    institutions = serializers.SerializerMethodField('institution_name')
    disciplines_found = serializers.SerializerMethodField()
    skills_found = serializers.SerializerMethodField('skill_name')
    # NOTE: Temporarily disabled.
    # score = serializers.SerializerMethodField('get_response')
    # matched_skills = serializers.SerializerMethodField()
    # related_skills = serializers.SerializerMethodField()

    def get_matched_skills(self, instance):
        content = instance.content.lower()
        skills = self.context.get('skills', [])
        matched =  []
        for skill in skills:
            if skill in content:
                matched.append(skill)
        matched = [x for x in matched if x.strip()]
        return set(matched)

    def get_related_skills(self, instance):
        content = instance.content.lower()
        skills = self.context.get('skills', [])
        per, exact, related, related_map = skill_match_percent(instance, skills)
        related_dict = []
        for k, v in related_map.items():
            if v:
                related_dict.append({"name": k, "related": v})

        return related_dict

    def domain(self, instance):
        url_instances = list(instance.urls.all())
        urls = [{'url': url.url, 'category': url.category} for url in url_instances]
        other_urls = []
        for item in urls:
            if item['category'] == 'others':
                other_urls.append(item['url'])
        website = instance.website_set.all()
        if website.exists():
            website = list(website)
            website_url = website[0].url
            try:
                other_urls.remove(website_url)
            except ValueError:
                pass
        domains = []
        if other_urls:
            for item in other_urls:
                parsed_url = urlparse(item)
                domain = parsed_url.scheme + '://' + parsed_url.netloc
                domains.append({'url': item, 'domain': domain})
            return domains

    def download_url(self, instance):
        loc = instance.resume_location
        if loc:
            if loc[0] == '/':
                rel = loc.split('/media/')[1]
                return settings.DOMAIN + '/media/' + rel
            return loc
        return ''

    def skill_name(self, instance):
        skill_instances = list(instance.skills.all())
        if skill_instances:
            return [skill.name for skill in skill_instances]
        return None

    def location_name(self, instance):
        location_instances = list(instance.locations.all())
        if location_instances:
            return [location.name for location in location_instances]
        return None

    def company_name(self, instance):
        company_instances = list(instance.companies.all())
        if company_instances:
            return [company.name for company in company_instances]
        return None

    def institution_name(self, instance):
        institution_instances = list(instance.institutions.all())
        if institution_instances:
            return [institution.name for institution in institution_instances]
        return None

    def get_disciplines_found(self, instance):
        return get_matched_degrees(instance.content)

    def get_response(self, instance):
        queryset = Resume.objects.filter(id=instance.id).prefetch_related(
            'blog_set', 'website_set', 'mobileapp_set', 'bitbucket_set',
            'github_set', 'stackoverflow_set'
        )
        instance = queryset[0]
        # Model Instances
        blog = instance.blog_set.all()
        website = instance.website_set.all()
        mobile_app = instance.mobileapp_set.all()
        bitbucket = instance.bitbucket_set.all()
        github = instance.github_set.all()
        stackoverflow = instance.stackoverflow_set.all()
        # GitHub
        github_contribution_score, github_activity_score, github_reputation_score = get_github_scores(github)
        # StackOverflow
        stackoverflow_contribution_score, stackoverflow_reputation_score, stackoverflow_activity_score = get_stackoverflow_scores(stackoverflow)
        # BitBucket
        bitbucket_contribution_score, \
        bitbucket_activity_score, \
        bitbucket_reputation_score = get_bitbucket_scores(bitbucket)
        # Blog
        average_blog_contribution_score, \
        average_blog_reputation_score, \
        average_blog_activity_score = get_blog_scores(blog)
        # Website
        average_website_contribution_score, \
        average_website_activity_score, \
        average_website_reputation_score = get_website_scores(website)
        # average mobile score
        average_mobile_app_contribution_score, \
        average_mobile_app_activity_score, \
        average_mobile_app_reputation_score = get_app_scores(mobile_app)
        # Activity Scores
        blog_activity_score = average_blog_activity_score
        website_activity_score = average_website_activity_score
        mobile_app_activity_score = average_mobile_app_activity_score
        # Contributions Scores
        blog_contribution_score = average_blog_contribution_score
        website_contribution_score = average_website_contribution_score
        mobile_app_contribution_score = average_mobile_app_contribution_score
        # Reputation Scores
        blog_reputation_score = average_blog_reputation_score
        website_reputation_score = average_website_reputation_score
        mobile_app_reputation_score = average_mobile_app_reputation_score
        # Total Contribution Score
        coding_total_contribution_score = github_contribution_score + bitbucket_contribution_score + \
                                          stackoverflow_contribution_score + mobile_app_contribution_score
        social_total_contribution_score = blog_contribution_score + website_contribution_score
        # Total Activity score
        coding_total_activity_score = github_activity_score + stackoverflow_activity_score + \
                                      bitbucket_activity_score + mobile_app_activity_score
        social_total_activity_score = blog_activity_score + website_activity_score
        # Total Reputation Score
        coding_total_reputation_score = github_reputation_score + stackoverflow_reputation_score + \
                                        bitbucket_reputation_score + mobile_app_reputation_score
        social_total_reputation_score = blog_reputation_score + website_reputation_score
        # Total Coding score 2.5 out of 5
        total_coding_score = coding_total_contribution_score + \
                             coding_total_reputation_score + coding_total_activity_score
        # Total Social Score 1.5 out 5
        total_social_score = social_total_contribution_score + \
                             social_total_activity_score + social_total_reputation_score
        # Total Skill Matching Score 1 out 5
        coding_score = []
        social_score = []
        # Generating Response
        # Coding Score
        total_github_score = github_contribution_score + \
                             github_reputation_score + github_activity_score
        total_stackoverflow_score = stackoverflow_activity_score + \
                                    stackoverflow_reputation_score + stackoverflow_contribution_score
        total_bitbucket_score = bitbucket_reputation_score + \
                                bitbucket_activity_score + bitbucket_contribution_score
        # Getting All StackOverflow Details
        if stackoverflow.exists():
            stackoverflow = stackoverflow[0]
            stackoverflow_data = get_stackoverflow_details(stackoverflow)
            stackoverflow_profile_url = stackoverflow.profile_url
            coding_score.append({'type': 'stackoverflow',
                                 'obtained': float("{0:.2f}".format(total_stackoverflow_score)),
                                 'data': stackoverflow_data,
                                 'url': stackoverflow_profile_url,
                                 })
        # Getting GitHub Details
        if github.exists():
            github = github[0]
            github_data = get_github_details(github)
            github_profile_url = github.profile_url
            coding_score.append({'type': 'github',
                                 'obtained': float("{0:.2f}".format(total_github_score)),
                                 'data': github_data,
                                 'url': github_profile_url,
                                 })
        # Getting Bit Bucket Details
        if bitbucket.exists():
            bitbucket = bitbucket[0]
            bitbucket_data = get_bitbucket_details(bitbucket)
            bitbucket_profile_url = bitbucket.profile_url
            coding_score.append({'type': 'bitbucket',
                                 'obtained': float("{0:.2f}".format(total_bitbucket_score)),
                                 'data': bitbucket_data,
                                 'url': bitbucket_profile_url
                                 })
        if mobile_app.exists():
            if mobile_app[0].app_type == 'ios':
                total_score_obtained = get_total_score(mobile_app)
                coding_score.append({'type': 'appstore',
                                     'obtained': total_score_obtained,
                                     'data': get_ios_data(mobile_app),
                                     'urls': get_ios_urls(mobile_app)
                                     })
            else:
                total_score_obtained = get_total_score(mobile_app)
                coding_score.append({
                    'type': 'playstore',
                    'obtained': total_score_obtained,
                    'data': get_android_data(mobile_app),
                    'urls': get_android_urls(mobile_app)
                })
        total_website_score = average_website_contribution_score + \
                              average_website_activity_score + average_website_reputation_score
        total_blog_score = average_blog_activity_score + \
                           average_blog_contribution_score + average_blog_reputation_score
        # Getting Blog Data
        if blog.exists():
            blog = blog[0]
            blog_data = get_blog_details(blog)
            blog_url = blog.url
            social_score.append({'type': 'blog',
                                 'obtained': float("{0:.2f}".format(total_blog_score)),
                                 'data': blog_data,
                                 'url': blog_url
                                 })
        # Getting Website Data
        if website.exists():
            website = website[0]
            website_data = get_website_details(website, instance.email)
            website_url = website.url
            social_score.append({'type': 'website',
                                 'obtained': float("{0:.2f}".format(total_website_score)),
                                 'data': website_data,
                                 'url': website_url
                                 })
        # Skill Score
        skills = instance.resumeskills_set.all()
        skill_data = []
        if skills.exists():
            for skill in skills:
                skill_data.append(
                    {'name': skill.skill.name, 'matched': skill.is_matched})
        skill_score = instance.get_skill_score()
        data_skill = [{'obtained': skill_score, 'skills': skill_data}]
        total_ranking = total_coding_score + total_social_score + skill_score
        coding = {'name': 'coding', 'data': coding_score}
        social = {'name': 'social', 'data': social_score}
        skills = {'name': 'skills', 'data': data_skill}
        ranking_data = [{'total': 5, 'obtained': float("{0:.2f}".format(total_ranking)),
                         'coding_score': float("{0:.2f}".format(total_coding_score)),
                         'social_score': float("{0:.2f}".format(total_social_score)),
                         'skill_score': float("{0:.2f}".format(skill_score))
                         }]
        ranking = {'name': 'Ranking', 'data': ranking_data}
        # get total and average app score
        score = [coding, social, ranking, skills]
        return score

    class Meta:
        model = Resume
        fields = (
            'id', 'created_date', 'file_name', 'first_name', 'last_name', 'email',
            'experience', 'phone_number', 'parse_status', 'resume_location',
            'urls', 'locations', 'companies', 'institutions', 'skills_found',
            'disciplines_found'
        )


class ResumeCallbackSerializer(serializers.ModelSerializer):
    """
    Serializer used to serialize and de-serialize resume model for callback.
    """
    locations = serializers.SerializerMethodField('location_name')

    def location_name(self, instance):
        location_instances = list(instance.locations.all())
        if location_instances:
            return [location.name for location in location_instances]
        return None

    class Meta:
        model = Resume
        fields = ('id', 'experience', 'locations',)
