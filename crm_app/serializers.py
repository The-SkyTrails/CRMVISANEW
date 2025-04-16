from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    Booking,
    FrontWebsiteEnquiry,
    VisaCountry,
    VisaCategory,
    Package,
    Enquiry,
    DocumentFiles,
    CustomUser,
    Admin,
    Employee,
    Wallet
)


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


class VisaCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaCountry
        fields = [
            "id",
            "country",
        ]


class VisaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaCategory
        fields = ["id", "category","subcategory"]


class FrontWebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontWebsiteEnquiry
        fields = [
            "name",
            "email",
            "appointment_date",
            "phone",
            "country_name",
            "category_name",
            "message",
            "image",
        ]


class ProductSerializer(serializers.ModelSerializer):
    visa_country = VisaCountrySerializer()
    visa_category = VisaCategorySerializer()

    class Meta:
        model = Package
        fields = "__all__"


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = "__all__"

class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFiles
        fields = "__all__"






from rest_framework import serializers
from .models import CaseCategoryDocument, DocumentCategory, DocumentCategory, Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id','document_name', 'document_category']

class DocumentCategorySerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = DocumentCategory
        fields = ['id', 'Document_category', 'documents']

    def get_documents(self, obj):
        documents = Document.objects.filter(document_category=obj)
        return DocumentSerializer(documents, many=True).data
    
class CaseCategoryDocumentSerializer(serializers.ModelSerializer):
    document_categories = serializers.SerializerMethodField()

    class Meta:
        model = CaseCategoryDocument
        fields = ['id', 'country', 'category', 'document_categories', 'last_updated_by', 'last_updated_on']

    def get_document_categories(self, obj):
        categories = DocumentCategory.objects.all()
        return DocumentCategorySerializer(categories, many=True).data






# ----------------- Login ------------------------


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        print("usernamee",email)
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User is deactivated.")
                data["user"] = user
            else:
                raise serializers.ValidationError("Invalid credentials.")
        else:
            raise serializers.ValidationError("Both fields are required.")
        return data



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'user_type']


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['department', 'contact_no', 'file']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'updated_at']