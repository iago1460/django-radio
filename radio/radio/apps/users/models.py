from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.TextField(blank=True, verbose_name=_("biography"))
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
