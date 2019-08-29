from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext, ugettext_lazy as _

# Create your models here.

SIGN_UP_STATUS_EMAIL = 'sign_up_status_email'
SIGN_UP_STATUS_FACEBOOK = 'sign_up_status_facebook'
SIGN_UP_STATUS_GOOGLE = 'sign_up_status_google'
SIGN_UP_STATUS_CHOICES = (
    (SIGN_UP_STATUS_EMAIL, _('g_sign_up_status_email')),
    (SIGN_UP_STATUS_FACEBOOK, _('g_sign_up_status_facebook')),
    (SIGN_UP_STATUS_GOOGLE, _('g_sign_up_status_google')),
)

class User(AbstractUser):
    pass
    id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length=15, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    image = models.CharField(max_length=255, default="")
    sign_up_status = models.CharField(max_length=64, choices=SIGN_UP_STATUS_CHOICES)
    social_id = models.CharField(max_length=255, default="")
    role = models.IntegerField(default=-1)
    
    class Meta:
        verbose_name = _('auth_user')
        verbose_name_plural = _('auth_users')
        db_table = 'auth_user'
        
class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, default="")
    price = models.FloatField(default=1)
    description = models.TextField(max_length=500, null=True)
    is_active = models.IntegerField(default=1)
    created_time = models.DateTimeField()
    added_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Item, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        db_table = 'item'
        
        