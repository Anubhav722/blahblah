# Django Imports
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter

# App Imports
from jarvis.accounts.models import UserProfile
from .models import (
    Tag, GitHubRepo, GitHub, StackOverflow, Url, Resume, MobileApp, Website,
    Blog, BitBucket, TrialUser, ResumeSkills, Location, Company, Institution,
    Visitor,
)

# Miscellaneous
import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Adds Tag Model to Admin.
    """
    list_display = ('tag', 'slug')
    list_filter = ('tag', )
    search_fields = ('tag', )


@admin.register(GitHubRepo)
class RepositoryAdmin(admin.ModelAdmin):
    """
    Adds Repository Model to Admin.
    """
    list_display = (
        'repo_id', 'repo_name', 'repo_url', 'no_of_forks',
        'no_of_stars', 'no_of_watchers', 'open_issue_counts',
        'repo_created_at', 'last_pushed_at', 'is_forked'
    )
    list_filter = ('no_of_stars', 'open_issue_counts', 'repo_name')
    search_fields = ('repo_name', 'repo_id')


@admin.register(GitHub)
class GitHubAdmin(admin.ModelAdmin):
    """
    Adds GitHub Model to Admin.
    """
    list_display = (
        'resume', 'user_id', 'profile_url', 'user_name',
        'profile_name', 'email', 'followers', 'public_repos',
        'public_gists', 'hireable', 'reputation_score',
        'contribution_score', 'activity_score', 'blog_url', 'company'
    )
    list_filter = ('company', 'user_name',)
    search_fields = ('user_id', 'user_name', 'email', 'profile_name', 'company')


@admin.register(StackOverflow)
class StackOverflowAdmin(admin.ModelAdmin):
    """
    Adds StackOverflow Model to Admin.
    """
    list_display = (
        'resume', 'user_id', 'profile_name', 'reputation',
        'gold_badges_count', 'silver_badges_count',
        'bronze_badges_count', 'total_no_questions',
        'total_no_answers', 'reputation_score', 'contribution_score', 'activity_score'
    )

    list_filter = ('user_id', 'profile_name', )
    search_fields = ('user_id', 'profile_name')


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    """
    Adds Url Model to Admin.
    """
    list_display = ('category', 'url')
    list_filter = ('category', )
    search_fields = ('category', )


@admin.register(BitBucket)
class BitBucketAdmin(admin.ModelAdmin):
    """
    Adds Bit Bucket Model to Admin.
    """
    list_display = (
        'resume', 'user_name', 'profile_url', 'display_name',
        'total_no_public_repos','followers', 'reputation_score',
        'contribution_score', 'activity_score', 'blog_url', 'location'
    )
    list_filter = ('user_name',)
    search_fields = ('user_name', 'display_name')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    """
    Adds Resume Model to Admin.
    """
    list_display = (
        'id', 'file_name', 'user', 'trial_user', 'first_name',
        'last_name', 'email', 'phone_number', 'experience',
        'parse_status', 'resume_location'
    )
    list_filter = ('first_name', 'parse_status', 'user', 'trial_user')
    search_fields = ('id', 'first_name', 'parse_status', 'file_name', 'user',)


@admin.register(MobileApp)
class MobileAppAdmin(admin.ModelAdmin):
    """
    Adds MobileApp Model to Admin.
    """
    list_display = (
        'resume', 'app_type', 'app_url', 'reputation_score',
        'contribution_score', 'activity_score'
    )
    search_fields = ('app_url', 'app_type')
    list_filter = ('app_type', )


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    """
    Adds Website Model to Admin.
    """
    list_display = (
        'resume', 'url', 'reputation_score', 'contribution_score',
        'activity_score'
    )
    search_fields = ('url',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
    Adds Blog Model to Admin.
    """
    list_display = (
        'resume', 'url', 'reputation_score', 'contribution_score',
        'activity_score'
    )
    search_fields = ('url', )


@admin.register(ResumeSkills)
class ResumeSkillsAdmin(admin.ModelAdmin):
    """Adds Resume Skills Model to Admin"""
    list_display = ('resume', 'skill', 'is_matched')
    list_filter = ('resume', 'is_matched')
    search_fields = ('resume', 'skill', 'is_matched')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """
    Adds Location Model to Admin.
    """
    list_display = ('name', )
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Adds Company Model to Admin.
    """
    list_display = ('name', 'rank', )
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """
    Adds Institution Model to Admin.
    """
    list_display = ('name', 'score', )
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(TrialUser)
class TrialUserAdmin(admin.ModelAdmin):
    """
    Resume parsing for Trial Use Case.
    """
    list_display = ('email_address', )

    def get_actions(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.email_address == "sample@aircto.com":
            return False
        return super(TrialUserAdmin, self).has_delete_permission(request, obj=obj)


class OrganizationFilter(SimpleListFilter):
    title = 'organization'
    parameter_name = 'organization'

    def lookups(self, request, model_admin):
        list_tuple = []
        for user_profile in UserProfile.objects.all():
            list_tuple.append((user_profile.user.id, user_profile.label))
        return list_tuple

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id=int(self.value()))
        else:
            return queryset


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    """
    Adds Visitor Model to Admin.
    """
    list_display = ('user', 'last_active', 'query_string', 'get_label', )
    list_filter = (OrganizationFilter, 'user', )
    readonly_fields = ('query_string_prettified', )
    exclude = ('query_string',)

    def get_label(self, obj):
        user_profile = UserProfile.objects.get(user=obj.user)
        return user_profile.label
    get_label.short_description = 'Label'
    get_label.admin_order_field = 'user'

    def query_string_prettified(self, instance):
        """Function to display pretty version of query_string"""

        response = json.dumps(json.loads(instance.query_string), sort_keys=True, indent=4)
        response = response[:5000]
        formatter = HtmlFormatter(style='friendly')
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    query_string_prettified.short_description = 'Query String'
