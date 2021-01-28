from django.contrib import admin

from hasker_login.models import HaskerUser


@admin.register(HaskerUser)
class HaskerUserAdmin(admin.ModelAdmin):
    fields = ('email', 'password', 'first_name', 'last_name', 'avatar', 'join', 'is_staff', 'is_active')