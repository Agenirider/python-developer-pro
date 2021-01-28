from django.contrib import admin

from hasker_posts.models import Questions, Answers, Tags


@admin.register(Questions)
class HaskerUserAdmin(admin.ModelAdmin):
    fields = ('title', 'contains', 'author', 'created', 'tags')
    list_display = ('id', 'title', 'contains', 'author', 'created', 'tags')

@admin.register(Answers)
class HaskerUserAdmin(admin.ModelAdmin):
    fields = ('question', 'contains', 'author', 'created', 'marker_is_correct')
    list_display = ('id', 'question', 'contains', 'author', 'created', 'marker_is_correct')


@admin.register(Tags)
class HaskerUserAdmin(admin.ModelAdmin):
    fields = ('tag', 'created')
    list_display = ('id', 'tag', 'created')
