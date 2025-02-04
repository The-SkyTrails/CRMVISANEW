from rest_framework import serializers
from .models import (
    Booking,
    FrontWebsiteEnquiry,
    VisaCountry,
    VisaCategory,
    Package,
    Enquiry,
    DocumentFiles
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