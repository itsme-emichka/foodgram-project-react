from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )
    list_filter = (
        'email',
        'username',
    )
