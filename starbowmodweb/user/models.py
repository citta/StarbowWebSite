from django.db import models

from django.db.models.signals import post_save
from django.conf import settings

from django.utils import timezone
from django.core import validators
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _

import os
import binascii


def generate_auth_token():
    return binascii.b2a_hex(os.urandom(15))


class User(AbstractBaseUser, PermissionsMixin):
    """ We had to copy this from contrib.auth.models because we need email to be unique. """

    username = models.CharField(_('username'), max_length=30,
        unique=True,
        help_text=_('<strong>Required!</strong><br>Your username can be composed of letters, digits, and the symbols "@", ".", "+", "-", and "_".'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
        ])

    email = models.EmailField(_('email address'),
        unique=True,
        help_text=_('<strong>Required!</strong>'),
        validators=[
            validators.validate_email
        ])

    authtoken = models.CharField(_('auth token'), max_length=48,
        unique=True,
        help_text=_('The authentication token used to log into the client app'),
        default=generate_auth_token)

    first_name = models.CharField(_('first name'), max_length=30, blank=True)

    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    is_staff = models.BooleanField(_('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'))

    is_active = models.BooleanField(_('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, related_name='profile')
    mybb_loginkey = models.CharField(max_length=100)
    mybb_uid = models.IntegerField(null=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# This is supposed to use settings.USER_AUTH_MODEL but it doesn't seem to work
post_save.connect(create_user_profile, sender=User)
