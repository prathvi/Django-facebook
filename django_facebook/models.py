from django.db import models
from django.core.urlresolvers import reverse
from djangotoolbox.fields import ListField
from djangotoolbox.fields import EmbeddedModelField
from djangotoolbox.fields import DictField
from django_facebook import model_managers
from datetime import datetime
from django.conf import settings
import os


PROFILE_IMAGE_PATH = os.path.join('images','facebook_profiles/%Y/%m/%d')

class FacebookUser(models.Model):
    '''
    Model for storing a users friends
    '''
    # in order to be able to easily move these to an another db,
    # use a user_id and no foreign key
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=(('F', 'female'),('M', 'male')), blank=True, null=True, max_length=1)
    timezone = models.TextField(blank=True, null=True)
    current_location =  DictField()
    hometown_location =  DictField()
    
    def __unicode__(self):
        return u'Facebook user %s' % self.name

class FacebookGroup(models.Model):
    fb_group_id = models.BigIntegerField()
    owner_id = models.TextField(max_length=50)
    group_name = models.TextField(max_length=50)
    pic_url = models.TextField(max_length=512,blank=True)
    description = models.TextField(max_length=1024,blank=True)
    link = models.TextField(max_length=512,blank=True)
    privacy = models.TextField(max_length=50,blank=True)
    members = ListField(EmbeddedModelField('FacebookUser'))
    last_sync_date = models.DateTimeField(default=datetime.now,blank=True)
    created_date = models.DateTimeField(default=datetime.now,blank=True)
    
    def __unicode__(self):
        return u'Facebook group %s' % self.group_name

class FacebookLike(models.Model):
    '''
    Model for storing all of a users fb likes
    '''
    # in order to be able to easily move these to an another db,
    # use a user_id and no foreign key
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return u'Facebook like %s' % self.name

class FacebookProfileModel(models.Model):
    '''
    Abstract class to add to your profile model.
    NOTE: If you don't use this this abstract class, make sure you copy/paste
    the fields in.
    '''
    about_me = models.TextField(blank=True)
    facebook_id = models.BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(
        blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True,
        upload_to=PROFILE_IMAGE_PATH, max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(('m', 'Male'), ('f', 'Female')), blank=True, null=True)
    friends = ListField(EmbeddedModelField('FacebookUser'))
    likes = ListField(EmbeddedModelField('FacebookLike'))
    groups = ListField(EmbeddedModelField('FacebookGroup'))
    raw_data = models.TextField(blank=True)

    def __unicode__(self):
        return self.user.__unicode__()

    class Meta:
        abstract = True

    def post_facebook_registration(self, request):
        '''
        Behaviour after registering with facebook
        '''
        from django_facebook.utils import next_redirect
        default_url = reverse('facebook_connect')
        response = next_redirect(request, default=default_url,
                                 next_key='register_next')
        response.set_cookie('fresh_registration', self.user_id)

        return response
    
    def clear_access_token(self):
        self.access_token = None
        self.save()

    def get_offline_graph(self):
        '''
        Returns a open facebook graph client based on the access token stored
        in the user's profile
        '''
        from open_facebook.api import OpenFacebook
        if self.access_token:
            graph = OpenFacebook(access_token=self.access_token)
            graph.current_user_id = self.facebook_id
            return graph
        
        

class FacebookProfile(FacebookProfileModel):
    '''
    Not abstract version of the facebook profile model
    Use this by setting
    AUTH_PROFILE_MODULE = 'django_facebook.FacebookProfile' 
    '''
    user = models.OneToOneField('auth.User')
    
    
if settings.AUTH_PROFILE_MODULE == 'django_facebook.FacebookProfile':
    '''
    If we are using the django facebook profile model, create the model
    and connect it to the user create signal
    '''
        
    from django.contrib.auth.models import User
    from django.db.models.signals import post_save
    
    #Make sure we create a FacebookProfile when creating a User
    def create_facebook_profile(sender, instance, created, **kwargs):
        if created:
            FacebookProfile.objects.create(user=instance)
    
    post_save.connect(create_facebook_profile, sender=User)
        
