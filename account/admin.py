from django.contrib import admin
from account.models import Account,Door,QR,Inside,Camera,ReturnedValueFromScript
from django.contrib.auth.admin import UserAdmin

#admin.site.register(Account)

class AccountAdmin(UserAdmin):
    list_display = ('id','username','data_joined','name','surname','last_login','is_admin','is_staff')
    search_fields = ('username',)
    readonly_fields = ('data_joined','last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(Account,AccountAdmin)
admin.site.register(Door)
admin.site.register(QR)
admin.site.register(Inside)
admin.site.register(Camera)
admin.site.register(ReturnedValueFromScript)