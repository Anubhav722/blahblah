
from django.db import models


class BaseModel(models.Model):
    """
    Generic abstract base class for all other models

    Fields:
    * :attr: `created_date` Creation date
    * :attr: `modified_date` Updation date
    * :attr: `deleted_date` Deletion date
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
