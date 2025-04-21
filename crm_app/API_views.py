import requests
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import (
    Booking,
    FrontWebsiteEnquiry,
    VisaCountry,
    VisaCategory,
    Package,
    Enquiry,
    DocumentFiles,
    CaseCategoryDocument,
    Admin, 
    Employee,
    Wallet,
    RechargeHistory
    
)
from .serializers import (
    BookingSerializer,
    FrontWebsiteSerializer,
    VisaCategorySerializer,
    VisaCountrySerializer,
    ProductSerializer,
    EnquirySerializer,
    DocumentsSerializer,
    CaseCategoryDocumentSerializer,
    UserLoginSerializer,
    CustomUserSerializer, 
    AdminSerializer, 
    EmployeeSerializer,
    WalletSerializer,
    RechargeHistorySerializer
)
from rest_framework.viewsets import ViewSet, ModelViewSet


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class FrontWebsite(ModelViewSet):
    queryset = FrontWebsiteEnquiry.objects.all()
    serializer_class = FrontWebsiteSerializer


class apiVisaCountry(ModelViewSet):
    queryset = VisaCountry.objects.all()
    serializer_class = VisaCountrySerializer


class apiVisaCategory(ModelViewSet):
    queryset = VisaCategory.objects.all()
    serializer_class = VisaCategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.filter(approval="Yes")
    serializer_class = ProductSerializer


class EnquiryViewSet(viewsets.ModelViewSet):
    # queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer

    def get_queryset(self):
        contact = self.request.query_params.get("contact")
        queryset = Enquiry.objects.filter(contact=contact)
        return queryset


def WebsitePackage(request):
    url = "https://back.theskytrails.com/skyTrails/packages/getAllcrm"
    response = requests.get(url)
    data = response.json()
    packages = data["data"]["pakage"]

    for package in packages:
        package["id"] = package.pop("_id")

    context = {"packages": packages}

    return render(request, "Admin/WebsitePackage/webPackage.html", context)


def EmployeeWebsitePackage(request):
    url = "https://back.theskytrails.com/skyTrails/packages/getAllcrm"
    response = requests.get(url)
    data = response.json()
    packages = data["data"]["pakage"]

    for package in packages:
        package["id"] = package.pop("_id")

    context = {"packages": packages}

    return render(request, "Employee/WebsitePackage/webPackage.html", context)


def AgentWebsitePackage(request):
    url = "https://back.theskytrails.com/skyTrails/packages/getAllcrm"
    response = requests.get(url)
    data = response.json()
    packages = data["data"]["pakage"]

    for package in packages:
        package["id"] = package.pop("_id")

    context = {"packages": packages}

    return render(request, "Agent/WebsitePackage/webPackage.html", context)




class DocumentsWebsite(ModelViewSet):
    queryset = DocumentFiles.objects.all()
    serializer_class = DocumentsSerializer



class DocumentsWebsite(ModelViewSet):
    queryset = DocumentFiles.objects.all()
    serializer_class = DocumentsSerializer



class CaseCategoryDocumentViewSet(viewsets.ModelViewSet):
    queryset = CaseCategoryDocument.objects.all()
    serializer_class = CaseCategoryDocumentSerializer





class LoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Token Generate
            refresh = RefreshToken.for_user(user)

            user_data = CustomUserSerializer(user).data

            # Add role-specific data
            user_type = user.user_type
            extra_data = {}

            if user_type == "2":  # Admin
                try:
                    admin = Admin.objects.get(users=user)
                    extra_data = AdminSerializer(admin).data
                except Admin.DoesNotExist:
                    extra_data = {}
            elif user_type == "3":  # Employee
                try:
                    emp = Employee.objects.get(users=user)
                    extra_data = EmployeeSerializer(emp).data
                except Employee.DoesNotExist:
                    extra_data = {}

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data,
                'extra': extra_data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class UserProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         data = {
#             "id": user.id,
#             "username": user.username,
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#             "user_type": user.user_type,
#         }

#         return Response(data)



# api_views.py

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        extra_data = {}

        if user.user_type == "2":  # Admin
            try:
                admin = Admin.objects.get(users=user)
                extra_data = {
                    "department": admin.department,
                    "contact_no": admin.contact_no,
                    "file": admin.file.url if admin.file else None,
                }
            except Admin.DoesNotExist:
                extra_data = {}

        elif user.user_type == "3":  # Employee
            try:
                employee = Employee.objects.get(users=user)
                extra_data = {
                    "emp_code": employee.emp_code,
                    "department": employee.department,
                    "branch": employee.branch.name if employee.branch else None,
                    "group": employee.group.name if employee.group else None,
                    "contact_no": employee.contact_no,
                    "city": employee.City,
                    "address": employee.Address,
                    "zipcode": employee.zipcode,
                    "file": employee.file.url if employee.file else None,
                }
            except Employee.DoesNotExist:
                extra_data = {}

        # Similarly add for Agent (user_type == "4") and Out Sourcing Agent (user_type == "5") if you have models

        data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "user_type": user.user_type,
            "extra": extra_data
        }

        return Response(data)


# class WalletAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         wallet, created = Wallet.objects.get_or_create(user=request.user)
#         serializer = WalletSerializer(wallet)
#         return Response(serializer.data)


from decimal import Decimal

class WalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    def put(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        increment_amount = request.data.get("balance")

        try:
            increment_amount = Decimal(increment_amount)
        except:
            return Response({"error": "Invalid balance value"}, status=status.HTTP_400_BAD_REQUEST)

        if increment_amount < 0:
            return Response({"error": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance += increment_amount
        wallet.save()

        return Response({
            "message": f"Balance incremented by {increment_amount}",
            "new_balance": wallet.balance
        })

    def patch(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        decrement_amount = request.data.get("balance")
        dec_type = request.data.get("type")
        booking_id = request.data.get("booking_id")
        
        print("decremeenttt",decrement_amount)

        try:
            decrement_amount = Decimal(decrement_amount)
        except:
            return Response({"error": "Invalid balance value"}, status=status.HTTP_400_BAD_REQUEST)

        if decrement_amount < 0:
            return Response({"error": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        if wallet.balance < decrement_amount:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= decrement_amount
        wallet.type = dec_type
        wallet.booking_id = booking_id
        
        wallet.save()

        return Response({
            "message": f"Balance decremented by {decrement_amount}",
            "new_balance": wallet.balance,
            "type": wallet.type,
            "booking_id": wallet.booking_id,
            
        })

    


class RechargeHistoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RechargeHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # user ko yahan assign kar rahe
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)