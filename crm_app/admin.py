from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.



class UserModel(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'is_logged_in')}),  # Add is_login here
    )
    list_display = UserAdmin.list_display + ('user_type', 'is_logged_in')  # Add is_login to list display

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('users', 'emp_code', 'branch', 'department')  # Fields to display in the list view
    search_fields = ('emp_code', 'department')  # Make fields searchable in the admin search bar
    list_filter = ('department', 'branch')  # Add filters to the sidebar
    ordering = ('emp_code',)  # Order by emp_code by default
    list_per_page = 20  # Limit the number of records per page in the list view

admin.site.register(CustomUser,UserModel)
admin.site.register(Admin)
admin.site.register(VisaCountry)
admin.site.register(VisaCategory)
admin.site.register(DocumentCategory)
admin.site.register(Document)
admin.site.register(CaseCategoryDocument)
admin.site.register(VisaSubcategory)
admin.site.register(Branch)
admin.site.register(Group)
admin.site.register(Package)
admin.site.register(SuccessStory)
admin.site.register(News)
admin.site.register(ActivityLog)
admin.site.register(LoginLog)
admin.site.register(FAQ)
admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Agent)
admin.site.register(OutSourcingAgent)
admin.site.register(BulkMessage)
admin.site.register(AgentAgreement)
admin.site.register(AgentKyc)
admin.site.register(Report)
admin.site.register(Enquiry)
admin.site.register(DocumentFiles)
admin.site.register(Notes)
admin.site.register(EnqAppointment)
admin.site.register(TestScore)
admin.site.register(Work_Experience)
admin.site.register(Education_Summary)
admin.site.register(Todo)
admin.site.register(Wallet)
admin.site.register(RechargeHistory)
admin.site.register(SubAgnt)
admin.site.register(WalletHistory)

