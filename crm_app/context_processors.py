from .models import *
from django.db.models import Q
from datetime import datetime, timedelta 
from django.utils.timezone import make_aware
from decimal import Decimal

def faq_count(request):
    # Initialize a dictionary to store all counts
    counts = {
        "faq_count": 0,  # Default value for non-authenticated users
        "agent_count": 0,
        "outsourceagent_count": 0,
        "total_agent_count": 0,
        "employee_count": 0,
        "leadarchive_count": 0,
        "leadaccept_count": 0,
        "leadinprocess_count": 0,
        "leadnew_count": 0,
        "leadpending_count": 0,
        "leadappoint_count": 0,
        "result_awaited_count": 0,
        "completed_count": 0,
        "leadresult_count": 0,
        "agents_added_today_count": 0,
        "total_agents_registered_by_user": 0,
        "agent_count": 0,
        "outsourceagent_count": 0,
        "lead_count": 0,
        "leadaccept_count_agent": 0,
        "agents": 0,
    }

    user = request.user
    if user.is_authenticated:
        try:
            wallet = Wallet.objects.get(user=user)
            counts["wallet_balance"] = wallet.balance
            
        except Wallet.DoesNotExist:
            counts["wallet_balance"] = Decimal("0.00")
        if user.user_type == "2":  # Example: Check for specific user type
            counts["agent_count"] = Agent.objects.all().count()
            counts["outsourceagent_count"] = OutSourcingAgent.objects.all().count()
            counts["total_agent_count"] = (
                counts["agent_count"] + counts["outsourceagent_count"]
            )
            counts["employee_count"] = Employee.objects.all().count()
            counts["leadarchive_count"] = Enquiry.objects.filter(archive=True).count()
            counts["leadaccept_count"] = Enquiry.objects.filter(
                lead_status="Enrolled", archive=False
            ).count()
            counts["leadinprocess_count"] = Enquiry.objects.filter(
                Q(lead_status="Inprocess") | Q(lead_status="Ready To Submit"),
                archive=False,
            ).count()
            counts['leadappoint_count'] = Enquiry.objects.filter(lead_status="Appointment" ,archive = False).count()
            counts['result_awaited_count'] = Enquiry.objects.filter(lead_status="Result Awaited" ,archive = False).count()
            counts['completed_count'] = Enquiry.objects.filter(lead_status="Ready To Collection",archive = False).count()
            counts['leadpending_count'] = Enquiry.objects.filter(
            Q(lead_status="Active",) | Q(lead_status="PreEnrolled"),archive = False
            ).count()
            leadtotal_count = Enquiry.objects.filter(archive = False).count()


            counts['leadnew_count']= Enquiry.objects.filter(lead_status="New Lead", archive = False).count()
            # leadnew_count = Enquiry.objects.filter(lead_status="New Lead", archive = False).count()
            
            
            counts['leadresult_count'] = Enquiry.objects.filter(lead_status="Approved",archive = False).count()


            
        # FAQ count for authenticated users

        if user.user_type == "3":
            today = datetime.now().date()
            start_of_day = make_aware(datetime.combine(today, datetime.min.time()))
            counts["agents_added_today_count"] = Agent.objects.filter(
            registeron__gte=start_of_day,
            registerdby=user
            ).count()
            counts["total_agents_registered_by_user"] = Agent.objects.filter(
            registerdby=user
            ).count()
            counts["agent_count"] = Agent.objects.filter(
                Q(registerdby=user)
                | Q(assign_employee=user)
            ).count

            counts["outsourceagent_count"] = OutSourcingAgent.objects.filter(
                registerdby=user
            ).count
        
        if user.user_type == "4":

            counts["agents"] = Agent.objects.get(users=user)

            
            counts["lead_count"] = Enquiry.objects.filter( Q(created_by=user)
            | Q(assign_to_agent=user.agent),archive = False).count()

            counts["leadaccept_count_agent"] = Enquiry.objects.filter(Q(assign_to_agent=user.agent) & Q(lead_status="Enrolled") | Q(lead_status="Appointment") | Q(lead_status="Inprocess") | Q(lead_status="Ready To Submit") | Q(lead_status="Ready To Collection") | Q(lead_status="Result") | Q(lead_status="Delivery") |  Q(created_by=user) & Q(lead_status="Enrolled") | Q(lead_status="Appointment") | Q(lead_status="Inprocess") | Q(lead_status="Ready To Submit") | Q(lead_status="Ready To Collection") | Q(lead_status="Result") | Q(lead_status="Delivery")).count()
        
        if user.user_type == '5': 
            counts["agents"] = OutSourcingAgent.objects.get(users=user)
            counts["lead_count"] = Enquiry.objects.filter( Q(created_by=user)
            | Q(assign_to_outsourcingagent=user.outsourcingagent),archive = False).count()

            counts["leadaccept_count_agent"] = Enquiry.objects.filter(Q(assign_to_outsourcingagent=user.outsourcingagent) & Q(lead_status="Enrolled") | Q(lead_status="Appointment") | Q(lead_status="Inprocess") | Q(lead_status="Ready To Submit") | Q(lead_status="Ready To Collection") | Q(lead_status="Result") | Q(lead_status="Delivery") |  Q(created_by=user) & Q(lead_status="Enrolled") | Q(lead_status="Appointment") | Q(lead_status="Inprocess") | Q(lead_status="Ready To Submit") | Q(lead_status="Ready To Collection") | Q(lead_status="Result") | Q(lead_status="Delivery")).count()
             
            
            
        counts["faq_count"] = FAQ.objects.filter(answer__exact="").exclude(
            answer__isnull=True
        ).count()

        
        

    return counts

# def faq_count(request):
#     if request.user.is_authenticated:
#         print("usersss hai",request.user.user_type)
#         count = (
#             FAQ.objects.filter(answer__exact="").exclude(answer__isnull=True).count()
#         )
#         print("countingsss",count)
#     else:
#         count = 0
#     return {"faq_count": count}



# def current_login(request):
#     if request.user and request.user.is_authenticated:
#         if request.user.user_type == "4":
#             user = request.user
#             agent_id = user.agent.id
#             notification = Notification.objects.filter(
#                 agent=agent_id, is_seen__in=[False]
#             ).order_by("-id")
#             notification_Count = Notification.objects.filter(
#                 agent=agent_id, is_seen__in=[False]
#             ).count()

#             return {
#                 "agent_id": agent_id,
#                 "notification": notification,
#                 "notification_Count": notification_Count,
#             }
#         elif request.user.user_type == "5":
#             user = request.user
#             agent_id = user.outsourcingagent.id
#             notification = Notification.objects.filter(
#                 outsourceagent=agent_id, is_seen__in=[False]
#             ).order_by("-id")
#             notification_Count = Notification.objects.filter(
#                 outsourceagent=agent_id, is_seen__in=[False]
#             ).count()

#             return {
#                 "agent_id": agent_id,
#                 "notification": notification,
#                 "notification_Count": notification_Count,
#             }
#         elif request.user.user_type == "3":
#             user = request.user
#             emp_idd = user.employee.id
#             notification = Notification.objects.filter(employee=emp_idd,is_seen=False,is_admin=False).order_by("-id")
#             # notification = Notification.objects.filter(
#             #     employee=emp_idd, is_seen__in=[False]
#             # ).order_by("-id")
#             notification_Count = Notification.objects.filter(
#                 employee=user.employee, is_seen=False,is_admin=False
#             ).count()
#             print("NO...............",notification)

#             return {
#                 "emp_idd": emp_idd,
#                 "notification": notification,
#                 "notification_Count": notification_Count,
#             }

#         elif request.user.user_type == "2":
            
#             user = request.user

            
#             notification = Notification.objects.filter(is_seen=False,is_admin=True).order_by("-id")
            
#             notification_Count = Notification.objects.filter(is_seen=False,is_admin=True).count()
#             print("notificationsss counts::",notification_Count)
#             return {
#                 "notification": notification,
#                 "notification_Count": notification_Count,
#             }

           
            
#     return {}
    
