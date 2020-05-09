from django.db import models
import datetime

class SharedFileModelManager(models.Manager):
    def all_active(self):
        return self.get_query_set().filter(active=True).filter(expiration_date__gte=datetime.datetime.now())