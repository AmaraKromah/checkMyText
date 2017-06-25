from django.contrib import admin
from .models import UserProfile, StudentDetails, CompanyDetails, UserType, UserFile, Rating


# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):

        if obj is not None:
            if obj.status == "student":
                self.exclude = ['company_details']
            elif obj.status == "bedrijf":
                self.exclude = ['student_details']
            else:
                self.exclude = ['student_details', 'company_details']

        userprofile = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)

        return userprofile


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(StudentDetails)
admin.site.register(CompanyDetails)
admin.site.register(UserType)
admin.site.register(UserFile)
admin.site.register(Rating)
