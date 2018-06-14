from faker import Faker
from ..models import Client, UserProfile
from django.contrib.auth import get_user_model
from factory import django, SubFactory, fuzzy, Sequence, LazyAttribute


fake = Faker()
User = get_user_model()


class ClientFactory(django.DjangoModelFactory):
    class Meta:
        model = Client

    key = fake.sha1()
    secret = fake.sha256()
    organization = fake.company()


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    username = fake.user_name()
    email = fake.email()


class UserProfileFactory(django.DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ('user',)

    client = SubFactory(ClientFactory)
    user = SubFactory(UserFactory)
    limit = fake.numerify()
    label = fake.name()
