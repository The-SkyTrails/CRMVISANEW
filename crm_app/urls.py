

from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from .forms import LoginForm
urlpatterns = [
    
   path('dashboard/', dashboard,name="dashboard"),
   # path('', maintanance,name="maintanance"),
   path('Comingsoon/', comingsoon,name="comingsoon"),




   path('Add/Todo/',add_todo,name="add_todo"),
   path('Todo/List',todo_list,name="todo_list"),
   path('Edit/Todo/<int:pk>/',edit_todo,name="edit_todo"),
   path('Todo/Delete/<int:pk>/', delete_todo, name="delete_todo"),

   
   path('signup/', signup,name="signup"),
   # path('', auth_views.LoginView.as_view(template_name='crm/login.html',authentication_form=LoginForm), name='login'),
   path('', CustomLoginView.as_view(authentication_form=LoginForm), name='login'),
   path('logout/',auth_views.LogoutView.as_view(next_page='login'),name="logout"),
   path('profile/', profile,name="profile"),
   path('profile/Setting/', profile_setting,name="profile_setting"),

   # ------------------------- VISA COUNTRY --------------------------

   path('VisaCountry/Load/',visacountry_load,name="visacountry_load"),
   path('VisaCountry/List',visacountry_list,name="visacountry_list"),
   path('Add/VisaCountry',add_visacountry,name="add_visacountry"),
   path('VisaCountry/List/<int:pk>/edit',edit_visacountry,name="edit_visacountry"),
   path('VisaCountry/List/<int:pk>/delete', delete_visacountry, name="delete_visacountry"),

   
   # ------------------------- VISA CATEGORY --------------------------
   

   path('VisaCategory/Load/',visacategory_load,name="visacategory_load"),
   path('VisaCategory/List',visacategory_list,name="visacategory_list"),
   path('Add/VisaCategory',add_visacategory,name="add_visacategory"),
   path('VisaCategory/List/<int:pk>/edit',edit_visacategory,name="edit_visacategory"),
   path('VisaCategory/List/<int:pk>/delete', delete_visacategory, name="delete_visacategory"),


   # ------------------------- Document CATEGORY --------------------------

   path('DocumentCategory/Load/',document_category_load,name="document_category_load"),
   path('DocumentCategory/List',documentcategory_list,name="documentcategory_list"),
   path('Add/DocumentCategory',add_documentcategory,name="add_documentcategory"),
   path('DocumentCategory/List/<int:pk>/edit',edit_documentcategory,name="edit_documentcategory"),
   path('DocumentCategory/List/<int:pk>/delete', delete_documentcategory, name="delete_documentcategory"),


   # ------------------------- Documents --------------------------
   path('Documents/Load/',document_load,name="document_load"),
   path('Documents/List',documents_list,name="documents_list"),
   path('Add/Document',add_document,name="add_document"),
   path('Document/List/<int:pk>/edit',edit_document,name="edit_document"),
   path('Document/List/<int:pk>/delete', delete_document, name="delete_document"),


   # ------------------------- Case Category Document --------------------------

   path('CaseCategoryDocuments/Load/',case_Category_document_load,name="case_Category_document_load"),
   path('CaseCategoryDocuments/List',case_category_documents_list,name="case_category_documents_list"),
   path('Add/CaseCategoryDocuments',case_category_document,name="case_category_document"),
   path('CaseCategoryDocuments/List/<int:pk>/edit',edit_case_category_document,name="edit_case_category_document"),
   path('CaseCategoryDocuments/List/<int:pk>/delete', delete_case_category_document, name="delete_case_category_document"),

   
   # ------------------------- VisaSubcategory --------------------------

   path('VisaSubCategory/Load/',visasubcategory_load,name="visasubcategory_load"),
   path('VisaSubCategory/List',visasubcategory_list,name="visasubcategory_list"),
   path('Add/VisaSubCategory',visasubcategory,name="visasubcategory"),
   path('VisaSubCategory/List/<int:pk>/edit',edit_visasubcategory,name="edit_visasubcategory"),
   path('VisaSubCategory/List/<int:pk>/delete', delete_visasubcategory, name="delete_visasubcategory"),

   
   # ------------------------- Branch --------------------------

   path('Branch/Load/',branch_load,name="branch_load"),
   path('Branch/List',branch_list,name="branch_list"),
   path('Add/Branch',add_branch,name="add_branch"),
   path('Branch/List/<int:pk>/edit',edit_branch,name="edit_branch"),
   path('Branch/List/<int:pk>/delete', delete_branch, name="delete_branch"),


   
   # ------------------------- Group --------------------------

   path('Group/Load/',group_load,name="group_load"),
   path('Group/List',group_list,name="group_list"),
   path('Add/Group',add_group,name="add_group"),
   path('Group/List/<int:pk>/edit',edit_group,name="edit_group"),
   path('Group/List/<int:pk>/delete', delete_group, name="delete_group"),


   # ------------------------- Packages --------------------------
   
   path('Package/Load/',package_load,name="package_load"),
   # path('Package/List',package_list,name="package_list"),
   path('Add/Package',add_package,name="add_package"),
   path('product/Details/<int:id>', product_details,name="product_details"),
   path('Package/List/<int:pk>/delete', delete_package, name="delete_package"),


   path('Add/Swap',after_Swap,name="after_Swap"),
   path('Package/List',tab,name="package_list"),
   path('Disapprove/List/<int:pk>/delete', package_disapprove, name="package_disapprove"),
   path("package_pdf/<int:id>/", package_pdf, name="pac_pdf"),
   
   # ------------------------- Success Story --------------------------

   path('Successstory/Load/',succestory_load,name="succestory_load"),
   path("Add/Successstory", add_successstory, name="add_successstory"),
   path("Successstory/List", successstory_list, name="successstory_list"),
   path('Successstory/<int:pk>/delete', delete_successstory, name="delete_successstory"),


   
   # ------------------------- News --------------------------
   path('News/Load/',news_load,name="news_load"),
   path('News/List',news_list,name="news_list"),
   path('Add/News',add_news,name="add_news"),
   path('News/Edit/<int:pk>/',edit_news,name="edit_news"),
   path('News/Delete/<int:pk>/', delete_news, name="delete_news"),



   # ------------------------- Activity Log --------------------------

   path("Activitylog/Load", activity_log_load, name="activity_log_load"),
   path("activity_logs/", activity_log_view, name="activity_logs"),

   # ------------------------- Login Logs --------------------------

   path("LoginLogs", loginlog.as_view(), name="loginlog"),


   
   # ------------------------- Bulk Message --------------------------

   path('Bulk/Message/Load/',bulkMsg_load,name="bulkMsg_load"),
   path('Bulk/Message/List/',bulkMsg_list,name="bulkMsg_list"),
   path('Add/Bulk/Message/',add_bulkmsg,name="add_bulkmsg"),
   path('Bulk/Message/Delete/<int:pk>/',delete_bulkmsg,name="delete_bulkmsg"),
  


   # ------------------------- Passport Enquiry --------------------------

   path("Passport/Enquiry", passport_enquiry_view, name="passport_enq"),

   # ------------------------- Queries --------------------------
   
   path('Queries/Load/',queries_load.as_view(),name="queries_load"),
   path('Queries/List',queries_list,name="queries_list"),
   path("AddQueries/", add_Faq, name="add_Faq"),
   path('Add/Answer',add_answer,name="add_answer"),


   # ------------------------- Employee --------------------------

   path('Employee/Load/',employee_load,name="employee_load"),
   path('Employee/List',employee_list,name="employee_list"),
   path('Add/Employee',add_employee,name="add_employee"),
   path('Edit/Employee/<int:pk>/',edit_employee,name="edit_employee"),
   path('Delete/Employee/<int:pk>/',delete_employee,name="delete_employee"),


   
   # ------------------------- VISA TEAM Employee --------------------------

    path('VisaTeam/Employee/Load/',visa_team_load,name="visa_team_load"),
    path('VisaTeam/Employee/List/',visa_team_list,name="visa_team_list"),
    path('VisaTeam/Employee/Add/',add_visa_team,name="add_visa_team"),
    path("team_updated/<int:id>", visateamcolorupdate_view, name="team_updated"),


   
   # ------------------------- AGENT --------------------------

   path('Agent/Load/',agent_load,name="agent_load"),
   path('Agent/List/',agent_list,name="agent_list"),
   path('Add/Agent/',add_agent,name="add_agent"),
   path('update/assign/<int:pk>/',update_assign,name="update_assign"),
   path("search/rms/", rm_search_view, name="rm_search"),
   path('Agent/Delete/<int:pk>/', agent_delete, name="agent_delete"),
   path("Agent/Details/<int:id>/", agent_details, name="agent_details"),
   path("Agent/Personal/Details/<int:id>/", agent_personal_details, name="agent_personal_details"),
   path("Agent/Agreement/<int:id>/", agent_agreement, name="agent_agreement"),
   path('Agent/Agreement/Edit/<int:id>/edit',edit_agent_agreement,name="edit_agent_agreement"),
   path('Agent/Agreement/Delete/<int:pk>/',delete_agent_agreement,name="delete_agent_agreement"),
  

   path("Agent/Kyc/<int:id>/", agent_kyc, name="agent_kyc"),
   path("Add/Agent/Kyc/<int:id>/", add_agent_kyc, name="add_agent_kyc"),


   
   # ------------------------- OutSource AGENT --------------------------

    path('Outsource/Agent/List/',outsource_agent_list,name="outsource_agent_list"),
    path('OutsourceAgent/Delete/<int:pk>/', outsource_agent_delete, name="outsource_agent_delete"),
    path('OutsourceAgent/update/assign/<int:pk>/',update_outsourceassign,name="update_outsourceassign"),




   # ------------------------- Report --------------------------
   
   
   path("create_report/", create_report, name="create_report"),


   path('Report/Load/',report_load,name="report_load"),
   path('Report/List',report_list,name="report_list"),

   path('click/',click,name="click"),
   path('product/', product,name="product"),
   
   path('test/', test,name="test"),
   path('Employee/List',emp_list,name="emp_list"),
   path('Help/',help_emp,name="help_emp"),
  
   path('Admin/Load/',admin_load,name="admin_load"),
   path('Admin/List',admin_list,name="admin_list"),
   path('Add/Admin',add_admin,name="add_admin"),
   path('Admin/List/<int:pk>/edit',edit_admin,name="edit_admin"),
   path('Admin/List/<int:pk>/delete', delete_admin, name="delete_admin"),
   path('delete-multiple-admins/',delete_multiple_admins, name='delete_multiple_admins'),



   # ------------------------- Lead Load --------------------------

   # path('Add/Lead/',add_lead,name="add_lead"),
   path("Add/Lead/", add_lead.as_view(), name="add_lead"),
   path("AddEnquiry2/", Enquiry2View.as_view(), name="enquiry_form2"),
   path("AddEnquiry3/", Enquiry3View.as_view(), name="enquiry_form3"),
   path("enquiry/<int:id>/",enquiry4,name="enquiry_form4"),
   path("Details/<int:id>/",enquiry_details,name="enquiry_details"),
   path("Uploaddocument/<int:id>/", upload_document, name="uploaddocument"),
   path("Delete/UploadFile/<int:id>", delete_docfile, name="docfile"),
   # path("enquiry_form4/<int:id>/", admindocument, name="enquiry_form4"),



   path('Lead/Load/',lead_load,name="lead_load"),
   path('All/Lead',all_lead,name="all_lead"),
   path('Enrolled/Lead',enrolled_lead,name="enrolled_lead"),
   path('Lead/Cancel',lead_cancel,name="lead_cancel"),
   path('Active/Lead',lead_active,name="lead_active"),
   path('Inprocess/Lead',lead_inprocess,name="lead_inprocess"),
   path('Appointment/Lead',lead_appointment,name="lead_appointment"),
   path('Lead/Awaited',result_awaited,name="result_awaited"),
   path('Lead/New',lead_new,name="lead_new"),
   path('Lead/Approved',lead_approved,name="lead_approved"),
   path('Lead/Completed',lead_completed,name="lead_completed"),

   path("UpdateAssign/<int:id>", update_assigned_employee, name="update_assign_employee"),
   path("UpdateAssignAgent/<int:id>",update_assigned_agent,name="update_assigned_agent",),
   path("UpdateAssignOP/<int:id>", update_assigned_op, name="update_assigned_op"),
   path("lead_update/<int:id>", lead_updated, name="lead_updated"),
   path("AddNotes/<int:id>/", add_notes, name="add_notes"),
   path("search/agents/", agent_search_view, name="agent_search"),  # The endpoint for AJAX requests
   path("search/agent/", agent_search, name="agent_searchh"),  # The endpoint for AJAX requests
   path("search/outagents/", outagent_search_view, name="outagent_search"),
   path("color_code/<int:id>/", color_code, name="color_code"),

   path("Enq/Appointment/Save/<int:id>/", appointment_Save, name="appointment_Save"),
  
   
   # ------------------------- Lead Details --------------------------
   path('personalInfo/<int:id>/',personal_info,name="personal_info"),
   path('OtherDetails/<int:id>/',other_details,name="other_details"),
   path("Test/Score/Delete/<int:id>/", delete_test_score, name="delete_test_score"),
   path("Product/<int:id>/", editproduct_details, name="edit_product_details"),
   path("Documents/enquiry/<int:id>/",enq_documents,name="enq_documents"),

   path("delete_and_archive/<int:id>/", delete_and_archive, name="delete_and_archive"),
   path("restore/<int:id>/", restore, name="restore"),
   # ----------------------------------Report --------------


   path('sweetalert',sweet_alert,name="sweetalert"),
   path("packages/share/<int:pk>/", Packageshare, name="package_share"),

   path("Check/Status/",check_status,name="check_status"),
   
  
    
]
