from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, Otp
from unfold.admin import ModelAdmin

@admin.register(UserAccount)
class UserAccountAdmin(UserAdmin, ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    
    # Optimize the fieldsets
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Fields for creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    # Optimize database queries
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            
        ).prefetch_related(
            'groups',
            'user_permissions'
        )

@admin.register(Otp)
class OtpAdmin(ModelAdmin):
    list_display = ('user', 'email', 'created_at', 'expires_at')
    search_fields = ('user__email', 'email')
    ordering = ('-created_at',)