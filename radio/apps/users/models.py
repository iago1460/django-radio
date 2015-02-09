# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = RichTextField(blank=True, verbose_name=_("biography"))
    avatar = models.ImageField(upload_to='avatars/', default='/static/radio/images/default-userprofile-avatar.jpg', verbose_name=_("avatar"))
    display_personal_page = models.BooleanField(default=False, verbose_name=_("display personal page"))
    slug = models.SlugField(max_length=30)

    def get_absolute_url(self):
        return reverse('users:detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                p = UserProfile.objects.get(user=self.user)
                self.pk = p.pk
            except UserProfile.DoesNotExist:
                pass
        self.slug = slugify(self.user.username)
        super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        default_permissions = ('change',)
        verbose_name = _('user profile')
        verbose_name_plural = _('user profile')

    def __unicode__(self):
        return "%s's profile" % self.user


def save_slug(sender, instance=None, **kwargs):
    if instance is not None and not kwargs.get('raw', False):
        userprofile, created = UserProfile.objects.get_or_create(user=instance)
        userprofile.save()


# Signal while saving user
post_save.connect(save_slug, sender=User)
