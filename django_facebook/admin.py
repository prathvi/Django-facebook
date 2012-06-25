from django.contrib import admin
from django_facebook import models


class FacebookUserAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'facebook_id',)
    search_fields = ('name',)


class FacebookLikeAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'category', 'facebook_id',)
    search_fields = ('name',)
    filter_fields = ('category', )

class FacebookGroupAdmin(admin.ModelAdmin):
    list_display = ('fb_group_id', 'owner_id', 'group_name', 'pic_url',)
    search_fields = ('name',)


admin.site.register(models.FacebookUser, FacebookUserAdmin)
admin.site.register(models.FacebookLike, FacebookLikeAdmin)
admin.site.register(models.FacebookGroup, FacebookGroupAdmin)