from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):

    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group',
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):

    list_display = ('id',
                    'title',
                    'description',
                    )
    list_display_links = (
        'id',
        'title',
    )
    search_fields = ('title',)
    list_filter = ('title',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
