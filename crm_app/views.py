from django.shortcuts import render,redirect
from .forms import *
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import *
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import get_object_or_404
from wkhtmltopdf.views import PDFTemplateResponse
from django.urls import reverse
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
import requests

from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    TemplateView,
)
import requests
from django.http import HttpResponseRedirect
from django.core.cache import cache

from django.utils.dateparse import parse_date

from .models import Agent
from .filters import AgentFilter,OutSourceAgentFilter
from django.db.models import Prefetch



def get_visa_team_employee():
    return Employee.objects.filter(department="Visa Team")



# def dashboard(request):
#     now = datetime.now()
#     hour = now.hour
#     if 5 <= hour < 12:
#         greeting = "Good Morning"
#     elif 12 <= hour < 16:
#         greeting = "Good Afternoon"
#     else:
#         greeting = "Good Evening"
    
#     context = {
#         'greeting': greeting
#     }
#     return render(request,'crm/base/dashboard.html',context)

from datetime import datetime
def dashboard(request):
    now = datetime.now()  # This will work correctly now
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 16:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    context = {
        'greeting': greeting
    }
    return render(request, 'crm/base/dashboard.html', context)



class CustomLoginView(LoginView):
    template_name = 'crm/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')  # Redirect to the dashboard if user is logged in
        return super().dispatch(request, *args, **kwargs)



def signup(request):
    fm = CustomerRegistrationForm()
    context = {
        'form':fm
    }
    return render(request,'crm/signup.html',context)



def profile(request):


    user = request.user
    context = {
        'user': user,  # User details ko context mein pass karna
    }
    if user.user_type == '2':  # HOD
        try:
            
            superadmin_data = SuperAdminHOD.objects.get(superadmin=user)
            context['superadmin'] = superadmin_data
        except SuperAdminHOD.DoesNotExist:
            context['superadmin'] = None
    elif user.user_type == '3':  # Employee
        try:
            employee_data = Employee.objects.get(users=user)
            context['employee'] = employee_data
        except Employee.DoesNotExist:
            context['employee'] = None
    
    elif user.user_type == '4':  # Agent
        try:
            agent_data = Agent.objects.get(users=user)
            context['agent'] = agent_data
        except Agent.DoesNotExist:
            context['agent'] = None
    elif user.user_type == '5':  # Agent
        try:
            agent_data = OutSourcingAgent.objects.get(users=user)
            context['agent'] = agent_data
        except Agent.DoesNotExist:
            context['agent'] = None

    return render(request,'crm/profile.html')

def profile_setting(request):
   return render(request,'crm/profile_setting.html')



def visacountry_load(request):
   
   return render(request,'crm/Masters/VisaCountry/visacountry_load.html')




def visacountry_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   
   search_terms = search_query.split()
   
   query = Q()

   for term in search_terms:
        query &= Q(lastupdated_by__icontains=term) | Q(lastupdated_by__icontains=term) | Q(country__icontains=term) 


   admins = VisaCountry.objects.filter(query).order_by('-id')
  
   
   paginator = Paginator(admins, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/VisaCountry/visacountry_list.html',context)


def add_visacountry(request):
    if request.method == "POST":
        form = VisaCountryForm(request.POST or None)
        if form.is_valid():
            # Capitalize the first letter of each word in the country name
            country_name = form.cleaned_data["country"].title()
           
            user = request.user
            form.instance.lastupdated_by = user
            form.instance.country = country_name  # Ensure the correct value is saved

            # Check if the country already exists in the database
            if VisaCountry.objects.filter(country__iexact=country_name).exists():
                form.add_error('country', f'{country_name} already exists.')
            else:
                form.save()
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"{country_name} added."
                    })
                })
    else:
        form = VisaCountryForm()

    context = {
        'form': form
    }

    return render(request, 'crm/Masters/VisaCountry/add_visacountry.html', context)




def edit_visacountry(request, pk):
    visacountry = get_object_or_404(VisaCountry, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = VisaCountryForm(request.POST, instance=visacountry)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.lastupdated_by = f"{request.user.first_name} {request.user.last_name}"
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{visacountry.country} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = VisaCountryForm(instance=visacountry)

    context = {
        'form': form
    }
    return render(request, 'crm/Masters/VisaCountry/add_visacountry.html', context)




def delete_visacountry(request, pk):
    try:
        country = get_object_or_404(VisaCountry, pk=pk)
        country.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Admin {country.country} deleted."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Country not found")
    





def visacategory_load(request):
   
   return render(request,'crm/Masters/VisaCategory/visacategory_load.html')



def visacategory_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(lastupdated_by__icontains=term) | Q(lastupdated_by__icontains=term) | Q(visa_country_id__country__icontains=term) | Q(category__icontains=term) | Q(subcategory__icontains=term) 


   visacat = VisaCategory.objects.filter(query).order_by('-id')
  
   
   paginator = Paginator(visacat, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/VisaCategory/visacategory_list.html',context)


def add_visacategory(request):
    form = VisaCategoryForm(request.POST or None)

    if request.method == "POST":
        user = request.user
        form = VisaCategoryForm(request.POST)
        if form.is_valid():
            # Convert category and subcategory to title case and assign it to the form instance
            form.instance.category = form.cleaned_data["category"].title()
            form.instance.subcategory = form.cleaned_data["subcategory"].title()
            form.instance.lastupdated_by = user

            # Check if the combination of category, subcategory, and visa_country_id already exists
            visa_country_id = form.cleaned_data["visa_country_id"]
            if VisaCategory.objects.filter(
                category=form.instance.category,
                subcategory=form.instance.subcategory,
                visa_country_id=visa_country_id
            ).exists():
                # Add an error to the form if it already exists
                form.add_error('visa_country_id', 'Category/Subcategory already exists for the selected country')
            else:
                # Save the form if no conflict is found
                form.save()
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"{form.instance.category} {form.instance.subcategory} Added Successfully"
                    })
                })
    
    context = {
        'form': form
    }

    return render(request, 'crm/Masters/VisaCategory/add_visacategory.html', context)

    


def edit_visacategory(request, pk):
    visacategory = get_object_or_404(VisaCategory, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = VisaCategoryForm(request.POST, instance=visacategory)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.lastupdated_by = f"{request.user.first_name} {request.user.last_name}"
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{form.instance.category} {form.instance.subcategory} Updated Successfully"

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = VisaCategoryForm(instance=visacategory)

    context = {
        'form': form
    }
    return render(request, 'crm/Masters/VisaCategory/add_visacategory.html', context)




def delete_visacategory(request, pk):
    try:
        visacategory = get_object_or_404(VisaCategory, pk=pk)
        visacategory.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{visacategory.category} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("visacategory not found")
    

# -------------------- DocumentCategory -------------------




def document_category_load(request):
   
   return render(request,'crm/Masters/DocumentCategory/document_category_load.html')



def documentcategory_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(lastupdated_by__icontains=term) | Q(lastupdated_by__icontains=term) | Q(Document_category__icontains=term) 


   visacat = DocumentCategory.objects.filter(query).order_by('-id')
  
   
   paginator = Paginator(visacat, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/DocumentCategory/documentcategory_list.html',context)





def add_documentcategory(request):
    form = DocumentCategoryForm(request.POST or None)

    if request.method == "POST":
        user = request.user
        form = DocumentCategoryForm(request.POST)
        if form.is_valid():
            
            form.instance.Document_category = form.cleaned_data["Document_category"].title()
            form.instance.lastupdated_by = user

            # Check if the combination of category, subcategory, and visa_country_id already exists
            document_category_id = form.cleaned_data["Document_category"]
            if DocumentCategory.objects.filter(
                Document_category=form.instance.Document_category).exists():
                # Add an error to the form if it already exists
                form.add_error('Document_category', 'Document Cateogory already exists')
            else:
                # Save the form if no conflict is found
                form.save()
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"{form.instance.Document_category} Added Successfully"
                    })
                })
    
    context = {
        'form': form
    }

    return render(request, 'crm/Masters/DocumentCategory/add_documentcategory.html', context)





def edit_documentcategory(request, pk):
    documentcat = get_object_or_404(DocumentCategory, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = DocumentCategoryForm(request.POST, instance=documentcat)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.lastupdated_by = f"{request.user.first_name} {request.user.last_name}"
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{documentcat.Document_category} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = DocumentCategoryForm(instance=documentcat)

    context = {
        'form': form
    }
    return render(request, 'crm/Masters/DocumentCategory/add_documentcategory.html', context)




def delete_documentcategory(request, pk):
    try:
        documentcat = get_object_or_404(DocumentCategory, pk=pk)
        documentcat.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{documentcat.Document_category} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Document Category not found")
    

# ------------------------------- Documents --------------------------



def document_load(request):
   
   return render(request,'crm/Masters/Documents/documents_load.html')




def documents_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(lastupdated_by__first_name__icontains=term) | Q(lastupdated_by__last_name__icontains=term) | Q(document_name__icontains=term) | Q(document_category__Document_category__icontains=term) 


   document = Document.objects.filter(query).order_by('-id')
  
   
   paginator = Paginator(document, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/Documents/documents_list.html',context)




def add_document(request):
    form = DocumentForm(request.POST or None)

    if request.method == "POST":
        user = request.user
        form = DocumentForm(request.POST)
        if form.is_valid():
            
            # form.instance.Document_category = form.cleaned_data["Document_category"].title()
            form.instance.lastupdated_by = user

            # Check if the combination of category, subcategory, and visa_country_id already exists
            
            if Document.objects.filter(
                document_name=form.instance.document_name).exists():
                # Add an error to the form if it already exists
                form.add_error('document_name', 'Document  already exists')
            else:
                # Save the form if no conflict is found
                form.save()
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"{form.instance.document_name} Added Successfully"
                    })
                })
    
    context = {
        'form': form
    }

    return render(request, 'crm/Masters/Documents/add_document.html', context)




def edit_document(request, pk):
    document = get_object_or_404(Document, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = DocumentForm(request.POST, instance=document)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.lastupdated_by = request.user
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{document.document_name} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = DocumentForm(instance=document)

    context = {
        'form': form
    }
    return render(request, 'crm/Masters/Documents/add_document.html', context)



def delete_document(request, pk):
    try:
        document = get_object_or_404(Document, pk=pk)
        document.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{document.document_name} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Document not found")
    



# ------------------------------- Case Category Documents --------------------------



def case_Category_document_load(request):
   
   return render(request,'crm/Masters/CaseCategoryDocuments/case_category_documents_load.html')




def case_category_documents_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(last_updated_by__first_name__icontains=term) | Q(last_updated_by__last_name__icontains=term) | Q(country__country__icontains=term) | Q(category__category__icontains=term) | Q(document__document_name__icontains=term) 


#    casecategorydocument = CaseCategoryDocument.objects.filter(query).order_by('-id')
   casecategorydocument = CaseCategoryDocument.objects.filter(query).distinct().order_by('-id')
  
   
   paginator = Paginator(casecategorydocument, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/CaseCategoryDocuments/case_category_documents_list.html',context)




def case_category_document(request):
    form = CaseCategoryDocumentForm(request.POST or None)

    if request.method == "POST":
        user = request.user
        form = CaseCategoryDocumentForm(request.POST)
        if form.is_valid():
            
            # form.instance.Document_category = form.cleaned_data["Document_category"].title()
            form.instance.last_updated_by = user

            # Check if the combination of category, subcategory, and visa_country_id already exists
            
            # if CaseCategoryDocument.objects.filter(
            #     country=form.instance.country).exists():
            #     # Add an error to the form if it already exists
            #     form.add_error('country', 'country  already exists')
            
                # Save the form if no conflict is found
            form.save()
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged": None,
                    "showMessage": f"{form.instance.country} Added Successfully"
                })
            })
    
    context = {
        'form': form
    }

    return render(request, 'crm/Masters/CaseCategoryDocuments/add_case_category_document.html', context)




def edit_case_category_document(request, pk):
    document = get_object_or_404(CaseCategoryDocument, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = CaseCategoryDocumentForm(request.POST, instance=document)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.last_updated_by = request.user
            print("currents usersss......",request.user)
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{document.country} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = CaseCategoryDocumentForm(instance=document)

    context = {
        'form': form
    }
    # return render(request, 'crm/Masters/Documents/add_document.html', context)
    return render(request, 'crm/Masters/CaseCategoryDocuments/add_case_category_document.html', context)



def delete_case_category_document(request, pk):
    try:
        document = get_object_or_404(CaseCategoryDocument, pk=pk)
        document.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{document.country} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Document not found")
    


# ------------------------------- VisaSubcategory --------------------------



def visasubcategory_load(request):
   
   return render(request,'crm/Masters/VisaSubCategory/visasubcategory_load.html')



def visasubcategory_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(lastupdated_by__icontains=term) | Q(lastupdated_by__icontains=term) | Q(country_id__country__icontains=term) | Q(category_id__category__icontains=term) | Q(subcategory_name__subcategory__icontains=term) 


   visasubcat = VisaSubcategory.objects.filter(query).distinct().order_by('-id')
  
   
   paginator = Paginator(visasubcat, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/VisaSubCategory/visasubcategory_list.html',context)



# @login_required
def visasubcategory(request):
    country = VisaCountry.objects.all()
    category = VisaCategory.objects.all()

    context = {
        "country": country,
        "category": category,
    }

    if request.method == "POST":
        country_id = request.POST.get("country")
        category_id = request.POST.get("category")
        subcategory_name = request.POST.get("subcategory")
        amount = float(request.POST.get("amount") or 0)
        cgst = float(request.POST.get("cgst") or 0)
        sgst = float(request.POST.get("sgst") or 0)
        user = request.user

        # try:
        # Calculate the totalAmount
        total = amount + ((amount * (cgst + sgst)) / 100)

        pricing = VisaSubcategory.objects.create(
            country_id_id=country_id,
            category_id_id=category_id,
            subcategory_name_id=subcategory_name,
            estimate_amt=amount,
            cgst=cgst,
            sgst=sgst,
            totalAmount=total,
            lastupdated_by=f"{user.first_name}{user.last_name}",
        )
        pricing.save()
        return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged": None,
                    "showMessage": f"{subcategory_name} Added Successfully"
                })
            })

        # messages.success(request, "Pricing Added Successfully !!")
        # return redirect("subcategory_list")

    # return render(request, "Admin/mastermodule/Pricing/add_pricing.html", context)
    return render(request, 'crm/Masters/VisaSubCategory/add_visasubcategory.html',context)


def edit_visasubcategory(request, pk):
    visa_subcat = get_object_or_404(VisaSubcategory, pk=pk)
    country = VisaCountry.objects.all()
    category = VisaCategory.objects.all()

    if request.method == "POST":
        country_id = request.POST.get("country")
        category_id = request.POST.get("category")
        subcategory_name_id = request.POST.get("subcategory")  # Assuming this is an ID
        amount = float(request.POST.get("amount") or 0)
        cgst = float(request.POST.get("cgst") or 0)
        sgst = float(request.POST.get("sgst") or 0)
        user = request.user

        # Calculate the totalAmount
        total = amount + ((amount * (cgst + sgst)) / 100)

        # Update the visa_subcat instance
        visa_subcat.country_id = VisaCountry.objects.get(id=country_id)  # Use the model instance
        visa_subcat.category_id = VisaCategory.objects.get(id=category_id)  # Use the model instance
        visa_subcat.subcategory_name_id = subcategory_name_id  # Assuming it's already the ID of a subcategory
        visa_subcat.estimate_amt = amount
        visa_subcat.cgst = cgst
        visa_subcat.sgst = sgst
        visa_subcat.totalAmount = total
        visa_subcat.last_updated_by = user
        visa_subcat.save()

        return HttpResponse(status=204, headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{visa_subcat.subcategory_name} Updated."
            })
        })

    context = {
        'visa_subcat': visa_subcat,  # Pass the instance to the template
        'country': country,
        'category': category,
    }
    return render(request, 'crm/Masters/VisaSubCategory/add_visasubcategory.html', context)



def delete_visasubcategory(request, pk):
    try:
        visasubcat = get_object_or_404(VisaSubcategory, pk=pk)
        visasubcat.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{visasubcat.subcategory_name} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Visasubcategory not found")
    


# ------------------------------- Branch --------------------------



def branch_load(request):
   
   return render(request,'crm/Masters/Branch/branch_load.html')



def branch_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(last_updated_by__first_name__icontains=term) | Q(last_updated_by__last_name__icontains=term) | Q(branch_source__icontains=term) | Q(branch_name__icontains=term) 


   branch = Branch.objects.filter(query).distinct().order_by('-id')
  
   
   paginator = Paginator(branch, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/Branch/branch_list.html',context)


def add_branch(request):
    form = BranchForm(request.POST or None)

    if request.method == "POST":
        user = request.user
        if form.is_valid():
            # Capitalize the branch_name before saving
            branch_name = form.cleaned_data["branch_name"].capitalize()
            form.instance.branch_name = branch_name
            form.instance.last_updated_by = user

            # Check if the branch already exists
            if Branch.objects.filter(branch_name=branch_name).exists():
                form.add_error('branch_name', 'Branch already exists')
            else:
                # Save the form only if no conflicts are found
                form.save()
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"{branch_name} Added Successfully"
                    })
                })
    
    context = {
        'form': form
    }

    return render(request, 'crm/Masters/Branch/add_branch.html', context)




def edit_branch(request, pk):
    branch = get_object_or_404(Branch, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = BranchForm(request.POST, instance=branch)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.last_updated_by = request.user
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{branch.branch_name} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = BranchForm(instance=branch)

    context = {
        'form': form
    }
    
    return render(request, 'crm/Masters/Branch/add_branch.html', context)


def delete_branch(request, pk):
    try:
        branch = get_object_or_404(Branch, pk=pk)
        branch.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{branch.branch_name} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Branch not found")
    


# ------------------------------- Group --------------------------



def group_load(request):
   
   return render(request,'crm/Masters/Group/group_load.html')



def group_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(create_by__first_name__icontains=term) | Q(create_by__last_name__icontains=term) | Q(group_name__icontains=term) | Q(group_member__first_name__icontains=term) & Q(group_member__last_name__icontains=term) | Q(group_member__first_name__icontains=term) | Q(group_member__last_name__icontains=term) 


   group = Group.objects.filter(query).distinct().order_by('-id')
   
  
   
   paginator = Paginator(group, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/Masters/Group/group_list.html',context)


def add_group(request):
    form = GroupForm(request.POST or None)

    if request.method == "POST":
        user = request.user
        form = GroupForm(request.POST)

        if form.is_valid():
            group_name = form.cleaned_data["group_name"].capitalize()
            print("Group name is", group_name)

            # Check if the group name already exists
            if Group.objects.filter(group_name=group_name).exists():
               
                # Add an error to the form if it already exists
                form.add_error('group_name', f'{group_name} Group already exists')
            else:
                
                # Save the form if no conflict is found
                form.instance.create_by = user
                form.instance.group_name = group_name  # Set the capitalized group name
                form.save()
                
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"{form.instance.group_name} Added Successfully"
                    })
                })

    context = {
        'form': form
    }

    return render(request, 'crm/Masters/Group/add_group.html', context)


def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
            form.instance.create_by = request.user
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{group.group_name} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = GroupForm(instance=group)

    context = {
        'form': form
    }
    # return render(request, 'crm/Masters/Documents/add_document.html', context)
    return render(request, 'crm/Masters/Group/add_group.html', context)




def delete_group(request, pk):
    try:
        group = get_object_or_404(Group, pk=pk)
        group.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{group.group_name} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Group not found")
    




# ------------------------------- Group --------------------------



def package_load(request):
   
   return render(request,'crm/Product/product_load.html')



# def package_list(request):   
#     package_choices = Package.PACKAGE_CHOICES
#     packages_by_type = {}

#     # Fetch packages grouped by type
#     for package_type, _ in package_choices:
#         packages_by_type[package_type] = Package.objects.filter(package_type=package_type)

#     context = {
#         "package_choices": package_choices,
#         "packages_by_type": packages_by_type,  # Pass packages grouped by type
#     }
#     return render(request,'crm/Product/product.html',context)


def package_list(request):
    package_choices = Package.PACKAGE_CHOICES
    packages_by_type = {}

    # Fetch all packages and store them under 'All'
    all_packages = Package.objects.filter(approval="Yes")
    packages_by_type['all'] = all_packages  # This will hold all the packages

    # Fetch packages grouped by type
    for package_type, _ in package_choices:
        packages_by_type[package_type] = Package.objects.filter(package_type=package_type,approval="Yes")

    context = {
        "package_choices": package_choices,
        "packages_by_type": packages_by_type,  # Pass packages grouped by type
    }
    return render(request, 'crm/Product/product.html', context)


def add_package(request):
    if request.method == "POST":
        form = PackageForm(request.POST, request.FILES)  # Pass both POST data and files
        if form.is_valid():
            user = request.user
            
            form.instance.last_updated_by = user
            # form.instance.approval = "Yes"
            if user.user_type == '2':
                form.instance.approval = "Yes"
            else:
                form.instance.approval = "No"
            form.save()
            # Respond with a status 204 (no content) and an HTMX trigger if using HTMX
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged": None,
                    "showMessage": f"{form.instance.title}Package Added Successfully"
                })
            })
    else:
        form = PackageForm()

    context = {
        'form': form
    }

    return render(request, 'crm/Product/add_package.html', context)



def product_details(request,id):
   package = Package.objects.get(id=id)
   context = {
       'package':package
   }
   return render(request,'crm/Product/product-detail2.html',context)




def delete_package(request, pk):
    try:
        package = get_object_or_404(Package, pk=pk)
        package.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{package.title} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Group not found")
    
    
    
def after_Swap(request):
    return render(request,'crm/Product/swap.html')
   
    
# def tab(request):

   

#     search_query = request.GET.get('search', '')
#     search_terms = search_query.split()
#     query = Q()
#     for term in search_terms:
#         query &= Q(create_by__first_name__icontains=term) | Q(create_by__last_name__icontains=term) | Q(group_name__icontains=term) | Q(group_member__first_name__icontains=term) & Q(group_member__last_name__icontains=term) | Q(group_member__first_name__icontains=term) | Q(group_member__last_name__icontains=term) 

        
#     package_choices = Package.PACKAGE_CHOICES
#     packages_by_type = {}

#     # Fetch all packages and store them under 'All'
    
    
#     all_packages = Package.objects.filter(approval="Yes")
#     packages_by_type['all'] = all_packages  # This will hold all the packages
    

#     # Fetch packages grouped by type
#     for package_type, _ in package_choices:
#         packages_by_type[package_type] = Package.objects.filter(package_type=package_type,approval="Yes")

#     disapprove_pkg = Package.objects.filter(approval="No")

    
    
#     context = {
#         "package_choices": package_choices,
#         "packages_by_type": packages_by_type,  # Pass packages grouped by type
#         "disapprove_pkg":disapprove_pkg,
        
      
#     }
#     return render(request,'crm/vertical_Tabs.html',context)



from django.core.paginator import Paginator

def tab(request):
    search_query = request.GET.get('search', '')
    search_terms = search_query.split()
   
    query = Q()
    
    for term in search_terms:
        query &= (Q(last_updated_by__first_name__icontains=term) |
                  Q(last_updated_by__last_name__icontains=term) |
                  Q(title__icontains=term) |
                  Q(package_type__icontains=term) |
                  Q(description__icontains=term) |
                  Q(visa_category__category=term) |
                  Q(visa_country__country__icontains=term))

    package_choices = Package.PACKAGE_CHOICES
    packages_by_type = {}

    # Fetch all approved packages with the search query
    all_packages = Package.objects.filter(approval="Yes").filter(query)

    # Set up pagination for "All" packages
    paginator = Paginator(all_packages, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Store paginated results in 'all' key for template rendering
    packages_by_type['all'] = page_obj

    # Group packages by type with pagination if needed
    for package_type, _ in package_choices:
        type_packages = Package.objects.filter(package_type=package_type, approval="Yes").filter(query)
        type_paginator = Paginator(type_packages, 2)
        type_page_number = request.GET.get(f'page_{package_type}', 1)
        packages_by_type[package_type] = type_paginator.get_page(type_page_number)

    disapprove_pkg = Package.objects.filter(approval="No").filter(query)

    context = {
        "package_choices": package_choices,
        "packages_by_type": packages_by_type,
        "disapprove_pkg": disapprove_pkg,
        "search_query": search_query,
        "page_obj": page_obj,
    }
    return render(request, 'crm/vertical_Tabs.html', context)


# def tab(request):
#     search_query = request.GET.get('search', '')
#     search_terms = search_query.split()
#     query = Q()
    
#     for term in search_terms:
#         query &= (Q(create_by__first_name__icontains=term) |
#                    Q(create_by__last_name__icontains=term) |
#                    Q(group_name__icontains=term) |
#                    Q(group_member__first_name__icontains=term) |
#                    Q(group_member__last_name__icontains=term))

#     package_choices = Package.PACKAGE_CHOICES
#     packages_by_type = {}

#     # Fetch all approved packages with the search query
#     all_packages = Package.objects.filter(approval="Yes").filter(query)
  
    
#     # Set up pagination
#     paginator = Paginator(all_packages, 2)  # Show 3 packages per page
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
    
#     packages_by_type['all'] = page_obj  # Update to use the paginated results

#     # Fetch packages grouped by type, applying the search query
#     for package_type, _ in package_choices:
#         packages_by_type[package_type] = Package.objects.filter(
#             package_type=package_type,
#             approval="Yes"
#         ).filter(query)

#     disapprove_pkg = Package.objects.filter(approval="No").filter(query)
    
#     context = {
#         "package_choices": package_choices,
#         "packages_by_type": packages_by_type,
#         "disapprove_pkg": disapprove_pkg,
#         "search_query": search_query,
#         "page_obj": page_obj,  # Include paginated object in context
#     }
#     return render(request, 'crm/vertical_Tabs.html', context)



# from django.core.paginator import Paginator
# from django.db.models import Q

# def tab(request):
#     # Get the search query
#     search_query = request.GET.get('search', '')
#     search_terms = search_query.split()
#     query = Q()

#     # Build search query for Group
#     for term in search_terms:
#         query &= (
#             Q(create_by__first_name__icontains=term) |
#             Q(create_by__last_name__icontains=term) |
#             Q(group_name__icontains=term) |
#             Q(group_member__first_name__icontains=term) & Q(group_member__last_name__icontains=term) |
#             Q(group_member__first_name__icontains=term) |
#             Q(group_member__last_name__icontains=term)
#         )

#     # Package types for filtering and categorizing packages
#     package_choices = Package.PACKAGE_CHOICES
#     packages_by_type = {}

#     # Filter approved packages with search query for package title or description
#     package_query = Q(approval="Yes")
#     for term in search_terms:
#         package_query &= Q(title__icontains=term) | Q(description__icontains=term)

#     # Fetch all packages matching the search query
#     all_packages = Package.objects.filter(package_query).distinct()
    
#     # Paginate the 'all' packages list
#     paginator = Paginator(all_packages, 3)  # Show 3 packages per page
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)

#     # Group packages by type with approval filter
#     for package_type, _ in package_choices:
#         packages_by_type[package_type] = Package.objects.filter(
#             package_type=package_type, approval="Yes"
#         )

#     # Disapproved packages
#     disapprove_pkg = Package.objects.filter(approval="No")

#     # Context dictionary
#     context = {
#         "package_choices": package_choices,
#         "packages_by_type": packages_by_type,
#         "disapprove_pkg": disapprove_pkg,
#         "page_obj": page_obj,  # Pass paginated all_packages
#         "search_query": search_query,
#     }
    
#     return render(request, 'crm/vertical_Tabs.html', context)


def package_disapprove(request, pk):
    try:
        package = get_object_or_404(Package, pk=pk)

        if package.approval == "Yes":
            package.approval = "No"
        else:
            package.approval = "Yes"
        package.save()
        
        # Dynamically show the appropriate message based on the approval status
        message = f"Package {'disapproved' if package.approval == 'No' else 'approved'} successfully."
        
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged": None,
                    "showMessage": message
                })
            }
        )
        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Package not found")





# def package_pdf(request, id):
#     package = Package.objects.get(id=id)
    
#     context = {"hello": "hello", "package": package,'quiet': None, 'enable-local-file-access': True}

#     return PDFTemplateResponse(request, "crm/Product/package_pdf.html", context)



from django.http import HttpResponse
from wkhtmltopdf.views import PDFTemplateResponse

def package_pdf(request, id):
    package = Package.objects.get(id=id)
    context = {
        "hello": "hello",
        "package": package,
        'quiet': None,
        'enable-local-file-access': True
    }
    
    # Use PDFTemplateResponse and set 'Content-Disposition' to 'attachment'
    response = PDFTemplateResponse(
        request,
        "crm/Product/package_pdf.html",
        context,
        cmd_options={'quiet': False, 'enable-local-file-access': True}
    )
    
    # Set the filename and make the response downloadable
    response['Content-Disposition'] = 'attachment; filename="package.pdf"'
    return response

# ------------------------------- Success Story --------------------------


# @login_required


def succestory_load(request):
   
   return render(request,'crm/SuccessStory/success_storyLoad.html')



def add_successstory(request):
    form = SuccessStoryForm(request.POST)

    if request.method == "POST":
        user = request.user
        print("add succscc story.......")
        form = SuccessStoryForm(request.POST,request.FILES)

        if form.is_valid():
            print("workkkkkkk")
            success_story = form.save(commit=False)
            success_story.create_by = user
            success_story.save()
            print("donnnnnnnnnnn")
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged": None,
                    "showMessage": f"{form.instance.description} Added Successfully"
                })
            })

    context = {
        'form': form
    }

    return render(request, 'crm/SuccessStory/addsuccessstory.html', context)



# def add_successstory(request):
#     form = SuccessStoryForm(request.POST, request.FILES or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             user = request.user
#             success_story = form.save(commit=False)
#             success_story.create_by = user
#             success_story.save()
#             return JsonResponse({'success': True, 'redirect_url': reverse("Successstory_list")})
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors})

#     form = SuccessStoryForm()
#     successstory = SuccessStory.objects.all().order_by("-id")
#     context = {"form": form, "story": successstory}
#     return render(request, "crm/SuccessStory/addsuccessstory.html", context)


def successstory_list(request):
    successstory = SuccessStory.objects.all().order_by("-id")
    context = {"story": successstory}
    return render(request,'crm/SuccessStory/successstorylist.html',context)




def delete_successstory(request, pk):
    try:
        success_story = get_object_or_404(SuccessStory, pk=pk)
        success_story.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"{success_story.description} Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Success Story not found")
    



# ------------------------------- News --------------------------


# @login_required


def news_load(request):
   
   return render(request,'crm/News/newsLoad.html')



# def news_list(request):
   
   
#    search_query = request.GET.get('search', '')
   
#    search_terms = search_query.split()
#    query = Q()

#    for term in search_terms:
#         query &= Q(create_by__first_name__icontains=term) | Q(create_by__last_name__icontains=term) | Q(news__icontains=term)  


#    group = News.objects.filter(query).distinct().order_by('-id')
   
  
   
#    paginator = Paginator(group, 3)
#    page_number = request.GET.get('page', 1)
#    page_obj = paginator.get_page(page_number)
#    context = {
#        'page_obj' : page_obj,
#        'search_query':search_query,
      
#    }
#    return render(request,'crm/News/news_list.html',context)




def news_list(request):
    # Get the search query from the GET request
    search_query = request.GET.get('search', '')
   
    # Split the search query into terms
    search_terms = search_query.split()
    query = Q()

    # Build the search query
    for term in search_terms:
        query &= Q(create_by__first_name__icontains=term) | Q(create_by__last_name__icontains=term) | Q(news__icontains=term)

    # Check the user type and filter News accordingly
    user = request.user  # Get the logged-in user
    
    if user.user_type == "2":  # Admin user (user_type = 2)
        # Show all news for admin (no filter)
        group = News.objects.filter(query).distinct().order_by('-id')
    elif user.user_type == "3":  # Employee user (user_type = 3)
        # Show news relevant to employees (employee=True)
        group = News.objects.filter(employee=True).filter(query).distinct().order_by('-id')
    elif user.user_type == "4":  # Agent user (user_type = 4)
        # Show news relevant to agents (agent=True)
        group = News.objects.filter(agent=True).filter(query).distinct().order_by('-id')
    elif user.user_type == "5":  # Out Sourcing Agent user (user_type = 5)
        # Show news relevant to outsourcing agents (outsource_Agent=True)
        group = News.objects.filter(outsource_Agent=True).filter(query).distinct().order_by('-id')
    else:
        # If no valid user_type, return no news (or handle other user types)
        group = News.objects.none()

    # Pagination setup
    paginator = Paginator(group, 3)  # Show 3 news items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'crm/News/news_list.html', context)

def add_news(request):
    print("helooooooooo")
    form = NewsForm(request.POST or None)

    
       
    if form.is_valid():
        user = request.user
        form.instance.create_by = user
        form.save()

        
        
        return HttpResponse(status=204, headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": "News Added Successfully"
            })
        })

    context = {
        'form': form
    }

    return render(request, 'crm/News/add_news.html', context)



def edit_news(request, pk):
    news = get_object_or_404(News, pk=pk)  # Fetch the admin instance to edit
    

    if request.method == "POST":
        form = NewsForm(request.POST, instance=news)
        # Bind the form to the POST data and the admin instance
        

        if form.is_valid():
           
            form.save()
            
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":"News Updated Successfully."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = NewsForm(instance=news)

    context = {
        'form': form
    }
    # return render(request, 'crm/Masters/Documents/add_document.html', context)
    return render(request, 'crm/News/add_news.html', context)




def delete_news(request, pk):
    try:
        news = get_object_or_404(News, pk=pk)
        news.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": "News Deleted Successfully."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("News not found")
    
   
# ------------------------------- Activity Login --------------------------


def activity_log_load(request):
   
   return render(request,'crm/ActivityLogs/activityLoad.html')


# @login_required
def activity_log_view(request):
   
    # activity_logs = ActivityLog.objects.all().order_by("-id")

    # context = {"activity_logs": activity_logs}

     
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
    
        query &= Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term) | Q(action__icontains=term)  


   group = ActivityLog.objects.filter(query).distinct().order_by('-id')
   
  
   
   paginator = Paginator(group, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }

   return render(request, "crm/ActivityLogs/Activitylogs.html", context)



# ------------------------------- Login Log --------------------------

class loginlog(LoginRequiredMixin, ListView):
    model = LoginLog
    template_name = "crm/LoginLogs/Loginlogs.html"
    context_object_name = "loginlog"

    def get_queryset(self):
        return LoginLog.objects.exclude(user__user_type="1").order_by("-id")

   
# ------------------------------- Passport Enquiry --------------------------


def passport_enquiry_view(request):
    url = "https://back.theskytrails.com/skyTrails/api/user/passport/getAllPassportEnquiry"
    response = requests.get(url)
    
    
    if response.status_code == 200:
        data = response.json()
        for item in data['result']:
            item['id'] = item.pop('_id')
        return render(request, 'crm/PassportEnquiry/passport_Enq.html', {'passport_data': data})
    else:
        error_message = f"Failed to fetch data from API. Status code: {response.status_code}"
        return render(request, 'crm/PassportEnquiry/passport_Enq.html', {'error_message': error_message})

   
# ------------------------------- Queries --------------------------



# class queries_load(LoginRequiredMixin, ListView):
#     model = FAQ
#     template_name = "crm/Queries/queries_load.html"
#     context_object_name = "resolved_queries"
#     paginate_by = 1

#     def get_queryset(self):
        
#         return FAQ.objects.exclude(Q(answer="") | Q(answer__isnull=True))
       

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["pending_queries"] = FAQ.objects.filter(Q(answer="") | Q(answer__isnull=True))
       
#         return context




class queries_load(LoginRequiredMixin, ListView):
    model = FAQ
    template_name = "crm/Queries/queries_load.html"
    context_object_name = "resolved_queries"
   
    paginate_by = 1

    def get_queryset(self):
        user = self.request.user
       
        if user.user_type == '2':  # Adjust this if user_type is numeric or string
            # If user_type is 2, exclude FAQs where answer is empty or null
            return FAQ.objects.exclude(Q(answer="") | Q(answer__isnull=True))
        else:
            # For other user types, show only their own FAQs that are not empty or null
            return FAQ.objects.filter(user=user).exclude(Q(answer="") | Q(answer__isnull=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.user_type == '2':  # Adjust this if user_type is numeric or string
            # For user_type 2, show pending queries (with empty or null answers)
            context["pending_queries"] = FAQ.objects.filter(Q(answer="") | Q(answer__isnull=True))
        else:
            # For other user types, show pending queries only for that user
            context["pending_queries"] = FAQ.objects.filter(user=user).filter(Q(answer="") | Q(answer__isnull=True))
        
        return context


def queries_list(request):
    return render(request,'crm/Queries/queries_list.html')  

def add_Faq(request):
    if request.method == "POST":
       
        question = request.POST.get('question')
        faq = FAQ.objects.create(question=question,user=request.user)
        faq.save()
        return redirect('queries_load')


def add_answer(request):
    user = request.user
    if request.method == "POST":
        print("aswersssssssssssssssssss")
        question_id = request.POST.get("question_id")      
        answer = request.POST.get("answer")

        faq = FAQ.objects.get(id=question_id)
        print("question id",question_id)
        print("faq",faq)
        
        faq.answer = answer


        faq.save()
        # messages.success(request, "Question Updated successfully")
        return HttpResponseRedirect(reverse("queries_load"))

# ------------------------------- Employee --------------------------



def employee_load(request):
   
   return render(request,'crm/InternalManagement/Employee/employee_load.html')



def employee_list(request):
   
#    employee = Employee.objects.all()
   search_query = request.GET.get('search', '')
   print("searchhhhh",search_query)
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(users__first_name__icontains=term) | Q(users__last_name__icontains=term) | Q(users__email__icontains=term) | Q(emp_code__icontains=term) | Q(branch__branch_name__icontains=term) | Q(department__icontains=term) | Q(group__group_name__icontains=term) | Q(contact_no__icontains=term) | Q(country__icontains=term) | Q(state__icontains=term) | Q(City__icontains=term) | Q(Address__icontains=term) | Q(zipcode__icontains=term) 


   emp = Employee.objects.filter(query).order_by('-id')
   
  
   
   paginator = Paginator(emp, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/InternalManagement/Employee/employee_list.html',context)

# def add_employee(request):
#     branches = Branch.objects.all()
#     groups = Group.objects.all()
#     dep = Department_Choices
#     context = {"branch": branches, "group": groups, "dep": dep}
#     return render(request,'crm/InternalManagement/Employee/add_employee.html',context)



# @login_required
def add_employee(request):
    branches = Branch.objects.all()
    groups = Group.objects.all()
    dep = Department_Choices

    if request.method == "POST":

        department = request.POST.get("department")
        emp_code = request.POST.get("emp_code")
        branch_id = request.POST.get("branch_id")
        group_id = request.POST.get("group_id")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email").lower()
        contact = request.POST.get("contact")
        password = "123456"
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address = request.POST.get("address")
        zipcode = request.POST.get("zipcode")
        api_key = request.POST.get("api_key")
        authorization = request.POST.get("authorization")
        tata_tele_agent_no = request.POST.get("tata_tele_agent_no")
        files = request.FILES.get("file")

        

        if CustomUser.objects.filter(email=email).exists():
           
            # messages.warning(request, "Email Id already exists")

            sweetify.error(request, 'Error', text=f'employee {firstname} {lastname} already exists', persistent='OK')
            return redirect('employee_load')
        

        if not branch_id:
            # messages.warning(request, "Branch ID is required")
            return redirect("emp_personal_details")

        # try:

        branchh = Branch.objects.get(id=branch_id)
        group = Group.objects.get(id=group_id)

        max_id = CustomUser.objects.aggregate(max_id=Max("id"))["max_id"]
        new_customuser_id = max_id + 1 if max_id is not None else 1

        emp_max_id = Employee.objects.aggregate(max_id=Max("id"))["max_id"]
        new_employee_id = emp_max_id + 1 if emp_max_id is not None else 1
        user = CustomUser.objects.create_user(
            # id=new_customuser_id,
            username=email,
            first_name=firstname,
            last_name=lastname,
            email=email,
            password=password,
            user_type="3",
        )

        # employee = Employee.objects.create(users=user,department = department,branch = branchh,group = group,contact_no = contact,country = country,state = state,City = city,Address = address,zipcode = zipcode,tata_tele_api_key = api_key,tata_tele_authorization = authorization,tata_tele_agent_number = tata_tele_agent_no,file = files)

        # employee.save()
        # user.employee.id = new_employee_id
        user.employee.department = department
        user.employee.emp_code = emp_code
        user.employee.branch = branchh
        user.employee.group = group
        user.employee.contact_no = contact
        user.employee.country = country
        user.employee.state = state
        user.employee.City = city
        user.employee.Address = address
        user.employee.zipcode = zipcode
        user.employee.tata_tele_api_key = api_key
        user.employee.tata_tele_authorization = authorization
        user.employee.tata_tele_agent_number = tata_tele_agent_no
        user.employee.file = files
        # user.users = new_customuser_id
        user.save()

        

        # send_congratulatory_email(firstname, lastname, email, password, user_type="3")
        # messages.success(
        #     request,
        #     "Employee Added Successfully , Congratulation Mail Send Successfully!!",
        # )

        mobile = contact
        sweetify.success(request, 'successfull!', text=f'employee {firstname} {lastname} added', persistent='OK')
        return redirect("employee_load")
       
    context = {"branch": branches, "group": groups, "dep": dep}
    return render(request,'crm/InternalManagement/Employee/add_employee.html',context)




def edit_employee(request, pk):
    employee = Employee.objects.get(pk=pk)
    dep = Department_Choices
    branches = Branch.objects.all()
    groups = Group.objects.all()

    if request.method == "POST":
        print("Armmmmmmmmm")
        employee_id = request.POST.get("employee_id")
        department = request.POST.get("department")
        branch_id = request.POST.get("branch_id")
        contact = request.POST.get("contact")
        emp_code = request.POST.get("emp_code")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email").lower()
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address = request.POST.get("address")
        zipcode = request.POST.get("zipcode")

        api_key = request.POST.get("api_key")
        authorization = request.POST.get("authorization")
        tata_tele_agent_no = request.POST.get("tata_tele_agent_no")
        file = request.FILES.get("file")

        branch = Branch.objects.get(id=branch_id)

        user = CustomUser.objects.get(id=employee_id)

        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.employee.department = department
        user.employee.contact_no = contact
        user.employee.country = country
        user.employee.state = state
        user.employee.City = city
        user.employee.Address = address
        user.employee.zipcode = zipcode
        user.employee.branch = branch
        user.employee.emp_code = emp_code

        user.employee.tata_tele_authorization = authorization
        user.employee.tata_tele_api_key = api_key
        user.employee.tata_tele_agent_number = tata_tele_agent_no

        if file:
            user.employee.file = file
        user.save()
        # messages.success(request, "Employee Updated Successfully")
        sweetify.success(request, 'Updated!', text=f'employee {firstname} {lastname} Successfull!!', persistent='OK')
        return redirect("employee_load")

    context = {"employee": employee, "dep": dep,'branch':branches,'group':groups}

    return render(request, "crm/InternalManagement/Employee/add_employee.html", context)



def delete_employee(request, pk):
    
    try:
        
        employee = get_object_or_404(Employee, pk=pk)
        custom_user = employee.users
        custom_user.delete()
        employee.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Employee Deleted Successfully"
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Employee not found")
    
# def product(request):
#    package_choices = Package.PACKAGE_CHOICES
  
   
   
#    context = {
#        "package_choices":package_choices
#    }
#    return render(request,'crm/product.html',context)




# ------------------------------- VISA TEAM Employee --------------------------



def visa_team_load(request):
   
   return render(request,'crm/InternalManagement/Employee/VisaTeam/visateam_load.html')


def visa_team_list(request):
   
#    employee = Employee.objects.all()
   search_query = request.GET.get('search', '')
   print("searchhhhh",search_query)
   
   search_terms = search_query.split()
#    query = Q()
   query = Q(department="Visa Team")

   for term in search_terms:
        query &= Q(users__first_name__icontains=term) | Q(users__last_name__icontains=term) | Q(emp_code__icontains=term) | Q(branch__branch_name__icontains=term) | Q(department__icontains=term) | Q(group__group_name__icontains=term) | Q(contact_no__icontains=term) | Q(country__icontains=term) | Q(state__icontains=term) | Q(City__icontains=term) | Q(Address__icontains=term) | Q(zipcode__icontains=term) 


   emp = Employee.objects.filter(query).order_by('-id')
   
  
   
   paginator = Paginator(emp, 10)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/InternalManagement/Employee/VisaTeam/visateam_list.html',context)


def add_visa_team(request):
    if request.method == "POST":
        selected_user_ids = request.POST.getlist("selected_users")
        color_code = request.POST.get("color_code")

        for user_id in selected_user_ids:
            employee = get_object_or_404(Employee, users__id=user_id)
            employee.color_code = color_code
            employee.save()

        # messages.success(request, "Colour Added successfully")
        sweetify.success(request, 'successfull!', text=f'Color {color_code}  added', persistent='OK')
        return redirect("visa_team_load")

    visateam = get_visa_team_employee()
    context = {"visateam": visateam}
    return render(request,'crm/InternalManagement/Employee/VisaTeam/add_visateam.html',context)
# ---------------------------------------------------------------------



# @login_required
def visateamcolorupdate_view(request,id):
    users_id = get_object_or_404(Employee, id=id) 
    if request.method == "POST":
        print("GGGGGGGGGGGGGGGGGGGG")
        # users = request.POST.get("users_id")
        emppid = users_id.id
        color_code = request.POST.get("color_code")

        emp_id = Employee.objects.get(id=emppid)
        emp_id.color_code = color_code

        emp_id.save()
        # messages.success(request, "Team Updated successfully")
        sweetify.success(request, 'Team', text='Update successful!l', persistent='OK')
        return HttpResponseRedirect(reverse("visa_team_load"))
    context = {
        'users_id':users_id
    }
    return render(request,'crm/InternalManagement/Employee/VisaTeam/add_visateam.html',context)



# ------------------------------- VISA AGENT --------------------------


def agent_load(request):
   
   return render(request,'crm/InternalManagement/Agent/agent_load.html')



def agent_list(request):
    # Initialize the agent filter form with GET parameters
    agent_filter = AgentFilter(request.GET)

    # Get the filtered queryset from the filter form (includes any date range filters and other filters)
    agents = agent_filter.qs

    logged_in_user = request.user

    if hasattr(logged_in_user, 'employee'):  # Assuming `employee` is the related field for Employee model
        
        # If employee, filter agents by `assign_to_employee`
        Q(registerdby=logged_in_user) | Q(assign_employee=logged_in_user)
        agents = agents.filter( Q(registerdby=logged_in_user) | Q(assign_employee=logged_in_user))

    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # If there's a search query, build a Q object to filter agents based on multiple fields
    if search_query:
        search_terms = search_query.split()
        query = Q()

        for term in search_terms:
            query &= (Q(users__first_name__icontains=term) | 
                      Q(users__last_name__icontains=term) |
                      Q(contact_no__icontains=term) |
                      Q(country__icontains=term) |
                      Q(registeron__icontains=term) |
                      Q(registerdby__first_name__icontains=term) |
                      Q(registerdby__last_name__icontains=term) |
                      Q(assign_employee__first_name__icontains=term) |
                      Q(assign_employee__last_name__icontains=term))
        
        # Apply the search query on top of the filtered agents
        agents = agents.filter(query)

    # Get the start and end dates from the GET parameters (if they exist)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    print("start date.........",start_date_str)

    # Apply the date filters if they exist
    if start_date_str:
        start_date = parse_date(start_date_str)  # Parse as naive date object (YYYY-MM-DD)
        if start_date:
            # Use registeron__date lookup to filter only by date, ignoring time
            agents = agents.filter(registeron__date__gte=start_date)

    if end_date_str:
        end_date = parse_date(end_date_str)  # Parse as naive date object (YYYY-MM-DD)
        if end_date:
            # Use registeron__date lookup to filter only by date, ignoring time
            agents = agents.filter(registeron__date__lte=end_date)
    agents = agents.order_by('-id')

    # Paginate the filtered queryset
    paginator = Paginator(agents, 10)  # Adjust number of items per page if needed
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Prepare context to be rendered
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'agent_filter': agent_filter,  # This contains the form with date filters
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    
    # Render the response with the filtered agents
    return render(request, 'crm/InternalManagement/Agent/agent_list.html', context)





# # @login_required
# def add_agent(request):
#     logged_in_user = request.user
#     relevant_employees = Employee.objects.all()

#     if request.method == "POST":
#         type = request.POST.get("type")

#         firstname = request.POST.get("firstname")
#         lastname = request.POST.get("lastname")
#         email = request.POST.get("email").lower()
#         contact = request.POST.get("contact")
#         password = request.POST.get("password")
#         country = request.POST.get("country")
#         state = request.POST.get("state")
#         city = request.POST.get("city")
#         address = request.POST.get("address")
#         zipcode = request.POST.get("zipcode")
#         files = request.FILES.get("files")
#         fullname = str(firstname + lastname)

#         existing_agent = CustomUser.objects.filter(username=email)

#         try:
#             if existing_agent:
#                 # messages.warning(request, f'"{email}" already exists.')
#                 sweetify.error(request, 'Error!', text=f'{email}" already exists.', persistent='OK')
#                 return redirect("add_agent")

#             if type == "Outsourcing Partner":
#                 print("save for outsource partner")
#                 user = CustomUser.objects.create_user(
#                     username=email,
#                     first_name=firstname,
#                     last_name=lastname,
#                     email=email,
#                     password=password,
#                     user_type="5",
#                 )
#                 logged_in_user = request.user
#                 last_assigned_index = cache.get("last_assigned_index") or 0
#                 sales_team_employees = CustomUser.objects.filter(user_type__in=[2, 3])
#                 user.outsourcingagent.type = type
#                 user.outsourcingagent.contact_no = contact
#                 user.outsourcingagent.country = country
#                 user.outsourcingagent.state = state
#                 user.outsourcingagent.City = city
#                 user.outsourcingagent.Address = address
#                 user.outsourcingagent.zipcode = zipcode
#                 user.outsourcingagent.profile_pic = files
#                 user.outsourcingagent.registerdby = logged_in_user
                
#                 if sales_team_employees.exists():
#                     next_index = (
#                         last_assigned_index + 1
#                     ) % sales_team_employees.count()
#                     user.outsourcingagent.assign_employee = sales_team_employees[
#                         next_index
#                     ]
                   
#                     cache.set("last_assigned_index", next_index)
#                 user.save()
#                 # send_congratulatory_email(
#                 #     firstname, lastname, email, password, user_type="5"
#                 # )
#                 # messages.success(
#                 #     request,
#                 #     "OutSourceAgent Added Successfully , Congratulation Mail Send Successfully!!",
#                 # )
#                 sweetify.success(request, 'successfull!', text='OutSourceAgent Added', persistent='OK')

#                 mobile = contact
#                 # try:
#                 #     whatsapp_signup_mes(
#                 #         firstname, lastname, email, password, mobile, user_type="5"
#                 #     )
#                 # except:
#                 #     pass

#                 return redirect("agent_load")

#             else:
#                 print("save for agent")
#                 user = CustomUser.objects.create_user(
#                     username=email,
#                     first_name=firstname,
#                     last_name=lastname,
#                     email=email,
#                     password=password,
#                     user_type="4",
#                 )
#                 fullname = str(firstname + lastname)
#                 logged_in_user = request.user
#                 last_assigned_index = cache.get("last_assigned_index") or 0
#                 sales_team_employees = CustomUser.objects.filter(user_type__in=[2, 3])

#                 user.agent.type = type
#                 user.agent.contact_no = contact
#                 user.agent.country = country
#                 user.agent.state = state
#                 user.agent.City = city
#                 user.agent.Address = address
#                 user.agent.zipcode = zipcode
#                 user.agent.profile_pic = files
#                 user.agent.registerdby = logged_in_user
#                 if sales_team_employees.exists():
#                     next_index = (
#                         last_assigned_index + 1
#                     ) % sales_team_employees.count()
#                     user.agent.assign_employee = sales_team_employees[next_index]
#                     cache.set("last_assigned_index", next_index)
                    

#                 user.save()
#                 # send_congratulatory_email(
#                 #     firstname, lastname, email, password, user_type="4"
#                 # )
#                 # messages.success(
#                 #     request,
#                 #     "Agent Added Successfully , Congratulation Mail Send Successfully!!",
#                 # )

#                 mobile = contact
#                 # try:
#                 #     whatsapp_signup_mes(
#                 #         firstname, lastname, email, password, mobile, user_type="4"
#                 #     )
#                 # except:
#                 #     pass

#                 sweetify.success(request, 'successfull!', text='Agent Added', persistent='OK')

#                 return redirect("agent_load")

#         except Exception as e:
#             print('Error',e)
#             # messages.warning(request, e)

#     context = {
#         "employees": relevant_employees,
#     }

#     return render(request, "crm/InternalManagement/Agent/add_agent.html", context)


# @login_required
def add_agent(request):
    logged_in_user = request.user
    relevant_employees = Employee.objects.all()

    if request.method == "POST":
        type = request.POST.get("type")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email").lower()
        contact = request.POST.get("contact")
        password = request.POST.get("password")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address = request.POST.get("address")
        zipcode = request.POST.get("zipcode")
        files = request.FILES.get("files")
        fullname = str(firstname + lastname)

        existing_agent = CustomUser.objects.filter(username=email)

        try:
            if existing_agent:
                sweetify.error(request, 'Error!', text=f'{email} already exists.', persistent='OK')
                return redirect("add_agent")

            # If Outsourcing Partner
            if type == "Outsourcing Partner":
                user = CustomUser.objects.create_user(
                    username=email,
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    password=password,
                    user_type="5",
                )
                user.outsourcingagent.type = type
                user.outsourcingagent.contact_no = contact
                user.outsourcingagent.country = country
                user.outsourcingagent.state = state
                user.outsourcingagent.city = city
                user.outsourcingagent.address = address
                user.outsourcingagent.zipcode = zipcode
                user.outsourcingagent.profile_pic = files
                user.outsourcingagent.registerdby = logged_in_user
                
                # Check if the logged in user is an employee
                if logged_in_user.user_type == "3":  # Assuming '3' is the employee type
                    user.outsourcingagent.assign_employee = logged_in_user
                else:
                    # If logged in user is admin, assign from sales team
                    sales_team_employees = CustomUser.objects.filter(user_type__in=[2, 3])
                    if sales_team_employees.exists():
                        last_assigned_index = cache.get("last_assigned_index") or 0
                        next_index = (last_assigned_index + 1) % sales_team_employees.count()
                        user.outsourcingagent.assign_employee = sales_team_employees[next_index]
                        cache.set("last_assigned_index", next_index)
                    
                user.save()
                sweetify.success(request, 'Success!', text='OutSourceAgent Added', persistent='OK')
                return redirect("agent_load")

            # If Agent
            else:
                user = CustomUser.objects.create_user(
                    username=email,
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    password=password,
                    user_type="4",
                )
                user.agent.type = type
                user.agent.contact_no = contact
                user.agent.country = country
                user.agent.state = state
                user.agent.city = city
                user.agent.address = address
                user.agent.zipcode = zipcode
                user.agent.profile_pic = files
                user.agent.registerdby = logged_in_user
                
                # Check if the logged in user is an employee
                if logged_in_user.user_type == "3":  # Assuming '3' is the employee type
                    user.agent.assign_employee = logged_in_user
                else:
                    # If logged in user is admin, assign from sales team
                    sales_team_employees = CustomUser.objects.filter(user_type__in=[2, 3])
                    if sales_team_employees.exists():
                        last_assigned_index = cache.get("last_assigned_index") or 0
                        next_index = (last_assigned_index + 1) % sales_team_employees.count()
                        user.agent.assign_employee = sales_team_employees[next_index]
                        cache.set("last_assigned_index", next_index)

                user.save()
                sweetify.success(request, 'Success!', text='Agent Added', persistent='OK')
                return redirect("agent_load")

        except Exception as e:
            print('Error', e)
            sweetify.error(request, 'Error!', text=f"An error occurred: {e}", persistent='OK')

    context = {
        "employees": relevant_employees,
    }

    return render(request, "crm/InternalManagement/Agent/add_agent.html", context)



def update_assign(request, pk):
    
    agent = get_object_or_404(Agent, pk=pk)
   

    if request.method == "POST":
        assign_rm = request.POST.get("rmIdInput")
        rm = CustomUser.objects.get(id=assign_rm)
        agent.assign_employee = rm
        agent.save()
       
            
        return HttpResponse(status=204, headers={
            'HX-Trigger': json.dumps({
                "movieListChanged":None,
                "showMessage":f"RM Assigned Successfully"

                })
            })
            
   
    context={
       'agent':agent
   }
    
    return render(request, 'crm/InternalManagement/Agent/assign.html',context)



def rm_search_view(request):
    
    query = request.GET.get("q", "")  
    
    rms = CustomUser.objects.filter(Q(user_type__in=["2", "3"]) & 
    (Q(first_name__icontains=query) | Q(last_name__icontains=query))  
    )  
    # Format the response for Select2
    results = [
        {
            "id": rm.id,
            "text": f"{rm.first_name} {rm.last_name} - {rm.get_user_type_display()}",  
        }
        for rm in rms
    ]
    print("resultssss",results)

    return JsonResponse({"results": results})



def agent_delete(request, pk):
    
    try:
        agent = get_object_or_404(Agent, pk=pk)
        custom_user = agent.users
        custom_user.delete()
        agent.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Agent Deleted Successfully"
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Agent not found")
    

# def agent_details(request,id):
#     agent = get_object_or_404(Agent, id=id)
    
    
    
#     context = {
#         'agent':agent,
        
#     }

#     return render(request,'crm/InternalManagement/AgentDetails/agent_details.html',context)


from django.http import Http404 

# def agent_details(request, id):
#     # Try to get the Agent instance first
#     agent = None
#     try:
#         agent = Agent.objects.get(id=id)
#     except Agent.DoesNotExist:
#         agent = None

#     # If Agent is not found, try to get the OutsourceAgent instance
#     if agent is None:
#         try:
#             agent = OutSourcingAgent.objects.get(id=id)
#         except OutSourcingAgent.DoesNotExist:
#             # If neither is found, raise 404
#             raise Http404("No Agent or OutsourceAgent matches the given query.")

#     # Return the context with the found agent
#     context = {
        
#         'agent': agent,
#     }

#     return render(request, 'crm/InternalManagement/AgentDetails/agent_details.html', context)
    
def agent_details(request, id):
    # Try to get the Agent instance first
    agent = None
    is_outsource_agent = False
    try:
        agent = Agent.objects.get(id=id)
    except Agent.DoesNotExist:
        try:
            agent = OutSourcingAgent.objects.get(id=id)
            is_outsource_agent = True
        except OutSourcingAgent.DoesNotExist:
            raise Http404("No Agent or OutsourceAgent matches the given query.")

    # Prepare context with agent details
    context = {
        'agent': agent,
        'is_outsource_agent': is_outsource_agent,  # Identify the type of agent
    }

    return render(request, 'crm/InternalManagement/AgentDetails/agent_details.html', context)

# def agent_personal_details(request,id):
#     agent = get_object_or_404(Agent, id=id)
#     users = agent.users
#     user = request.user
#     # dep = user.employee.department
#     if request.method == "POST":
       
#         firstname = request.POST.get("first_name")
#         lastname = request.POST.get("last_name")

#         dob = request.POST.get("dob")
#         gender = request.POST.get("gender")
#         maritial = request.POST.get("maritial")
#         original_pic = request.FILES.get("original_pic")
#         organization = request.POST.get("organization")
#         business_type = request.POST.get("business_type")
#         registration = request.POST.get("registration")
#         address = request.POST.get("address")
#         country = request.POST.get("country")
#         state = request.POST.get("state")
#         city = request.POST.get("city")
#         zipcode = request.POST.get("zipcode")
#         accountholder = request.POST.get("accountholder")
#         bankname = request.POST.get("bankname")
#         branchname = request.POST.get("branchname")
#         account = request.POST.get("account")
#         ifsc = request.POST.get("ifsc")

#         if dob:
#             users.agent.dob = dob
#         if gender:
#             users.agent.gender = gender
#         if maritial:
#             users.agent.marital_status = maritial
#         if original_pic:
#             users.agent.profile_pic = original_pic

#         users.first_name = firstname
#         users.last_name = lastname

#         users.agent.organization_name = organization
#         users.agent.business_type = business_type
#         users.agent.registration_number = registration
#         users.agent.Address = address
#         users.agent.country = country
#         users.agent.state = state
#         users.agent.City = city
#         users.agent.zipcode = zipcode
#         users.agent.account_holder = accountholder
#         users.agent.bank_name = bankname
#         users.agent.branch_name = branchname
#         users.agent.account_no = account
#         users.agent.ifsc_code = ifsc

#         users.save()
#         sweetify.success(request, 'Successful', text='Personal Details Updated!', persistent='OK')
#         # messages.success(request, "Updated Successfully")
#         return redirect("agent_details", id)

#     context = {
#         'agent':agent,
#         # "dep": dep
#     }
#     return render(request,'crm/InternalManagement/AgentDetails/personal_details.html',context)



def agent_personal_details(request, id):
    # Fetch from Agent or OutSourcingAgent based on which model the ID belongs to
    try:
        agent = Agent.objects.get(id=id)  # Try to get an Agent first
    except Agent.DoesNotExist:
        # If not found in Agent, look in OutSourcingAgent
        agent = get_object_or_404(OutSourcingAgent, id=id)

    users = agent.users  # Associated user object

    if request.method == "POST":
        # Collect form data
        firstname = request.POST.get("first_name")
        lastname = request.POST.get("last_name")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        maritial = request.POST.get("maritial")
        original_pic = request.FILES.get("original_pic")
        organization = request.POST.get("organization")
        business_type = request.POST.get("business_type")
        registration = request.POST.get("registration")
        address = request.POST.get("address")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        accountholder = request.POST.get("accountholder")
        bankname = request.POST.get("bankname")
        branchname = request.POST.get("branchname")
        account = request.POST.get("account")
        ifsc = request.POST.get("ifsc")

        # Update agent details
        if dob:
            agent.dob = dob
        if gender:
            agent.gender = gender
        if maritial:
            agent.marital_status = maritial
        if original_pic:
            agent.profile_pic = original_pic

        users.first_name = firstname
        users.last_name = lastname
        agent.organization_name = organization
        agent.business_type = business_type
        agent.registration_number = registration
        agent.Address = address
        agent.country = country
        agent.state = state
        agent.City = city
        agent.zipcode = zipcode
        agent.account_holder = accountholder
        agent.bank_name = bankname
        agent.branch_name = branchname
        agent.account_no = account
        agent.ifsc_code = ifsc

        # Save changes
        users.save()
        agent.save()

        sweetify.success(request, 'Successful', text='Personal Details Updated!', persistent='OK')
        return redirect("agent_details", id=id)

    context = {
        'agent': agent,
    }
    return render(request, 'crm/InternalManagement/AgentDetails/personal_details.html', context)


# def agent_agreement(request,id):
#     agent = get_object_or_404(Agent, id=id)
#     agntagreement = AgentAgreement.objects.filter(agent=agent)
#     if request.method == "POST":
#         name = request.POST.get("agreement_name")
#         file = request.FILES.get("file")
#         agreement = AgentAgreement.objects.create(
#             agent=agent, agreement_name=name, agreement_file=file
#         )
#         agreement.save()
#         sweetify.success(request, 'successful!', text='Agreement Added..', persistent='OK')
#         # messages.success(request, "Agreement Updated Succesfully...")
#         return redirect("agent_details", id)
#     context = {"agent": agent, "agreement": agntagreement}
    

#     return render(request,'crm/InternalManagement/AgentDetails/agent_agreement.html',context)



def agent_agreement(request, id):
   
    # Fetch from Agent or OutSourcingAgent based on the given ID
    try:
        agent = Agent.objects.get(id=id)  # Try to get an Agent first
        print("agentssssssssssssss",agent)
        is_outsource_agent = False
    except Agent.DoesNotExist:
        # If not found in Agent, look in OutSourcingAgent
        agent = get_object_or_404(OutSourcingAgent, id=id)
       
        is_outsource_agent = True
    if is_outsource_agent:
        agntagreement = AgentAgreement.objects.filter(outsourceagent=agent)
    else:

        # Fetch agreements for the agent
        agntagreement = AgentAgreement.objects.filter(agent=agent)
        

    if request.method == "POST":
        name = request.POST.get("agreement_name")
        file = request.FILES.get("file")
        if is_outsource_agent:
        
        # Create and save a new agreement
            agreement = AgentAgreement.objects.create(
                outsourceagent=agent, agreement_name=name, agreement_file=file
            )
            agreement.save()

            sweetify.success(request, 'Successful!', text='Agreement Added..', persistent='OK')
            return redirect("agent_details", id)
        else:
             
            agreement = AgentAgreement.objects.create(
                agent=agent, agreement_name=name, agreement_file=file
            )
            agreement.save()

            sweetify.success(request, 'Successful!', text='Agreement Added..', persistent='OK')
            return redirect("agent_details", id)

    context = {"agent": agent, "agreement": agntagreement}
    return render(request, 'crm/InternalManagement/AgentDetails/agent_agreement.html', context)



def edit_agent_agreement(request, id):


    try:
        agree = get_object_or_404(AgentAgreement, id=id)
        agent = agree.agent
       
        is_outsource_agent = False
    except Agent.DoesNotExist:
        # If not found in Agent, look in OutSourcingAgent
        agent = agree.outsourceagent
       
       
        is_outsource_agent = True


    
    if is_outsource_agent:
    
        agntagreement = AgentAgreement.objects.filter(outsourceagent=agent)
    else:
        agntagreement = AgentAgreement.objects.filter(agent=agent)
   
   
    if request.method == "POST":
       
        agntagreement = AgentAgreement.objects.get(id=id)
        agreement_name = request.POST.get("agreement_name")
        file = request.FILES.get("file")

        agntagreement.agreement_name = agreement_name
        if file:
            agntagreement.agreement_file = file
        agntagreement.save()
        return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f" Updated."

                    })
                })
        # messages.success(request, "Agreement Updated Successfully...")
        # return redirect("employee_agent_agreement", agent.id)
    context = {
        'agent':agent,
        'agree':agree,
    }
    return render(request,'crm/InternalManagement/AgentDetails/edit_agreement.html',context)




def delete_agent_agreement(request, pk):
    try:
        
        agree = get_object_or_404(AgentAgreement, pk=pk)
       
        # agent = agree.agent  # This will also delete the associated SuperAdminHOD because of cascade delete
        agreement = AgentAgreement.objects.get(pk=pk)
        agreement.delete()
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Agreement Deleted Successfully...",
                
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Agreement not found")
    

def agent_kyc(request,id):
    kyc_id = None

    try:
        agent = Agent.objects.get(id=id)  # Try to get an Agent first
        print("agentssssssssssssss",agent)
        is_outsource_agent = False
    except Agent.DoesNotExist:
        # If not found in Agent, look in OutSourcingAgent
        agent = get_object_or_404(OutSourcingAgent, id=id)    
        is_outsource_agent = True
    if is_outsource_agent:
        kyc_agent = AgentKyc.objects.filter(outsourceagent=agent).first
        
   
    else:
       
        kyc_agent = AgentKyc.objects.filter(agent=agent).first
        
   

       
        







   
    
    
    adhar_details = ['Aadhar Card Front','Aadhar Card Back','Pancard']
    context = {"agent": agent, "kyc_id": kyc_id, "kyc_agent": kyc_agent,"adhar_details": adhar_details,}


    return render(request,'crm/InternalManagement/AgentDetails/kyc.html',context)

def add_agent_kyc(request,id):
    # agent = Agent.objects.get(id=id)

    try:
        agent = Agent.objects.get(id=id)  # Try to get an Agent first
        print("agentssssssssssssss",agent)
        is_outsource_agent = False
    except Agent.DoesNotExist:
        # If not found in Agent, look in OutSourcingAgent
        agent = get_object_or_404(OutSourcingAgent, id=id)    
        is_outsource_agent = True
    document_type = request.GET.get('document')
    
    
    if request.method == "POST":
        adharfront_file = request.FILES.get("adharfront_file")
        adharback_file = request.FILES.get("adharback_file")
        pan_file = request.FILES.get("pan_file")
        registration_file = request.FILES.get("registration_file")
        try:
            if is_outsource_agent:
                kyc_id = AgentKyc.objects.get(outsourceagent=agent)
            else:
                kyc_id = AgentKyc.objects.get(agent=agent)


            if kyc_id:
                if adharfront_file:
                    kyc_id.adhar_card_front = adharfront_file
                if adharback_file:
                    kyc_id.adhar_card_back = adharback_file
                if pan_file:
                    kyc_id.pancard = pan_file
                if registration_file:
                    kyc_id.registration_certificate = registration_file
                kyc_id.save()
                return HttpResponse(
                    status=204,
                    headers={
                        'HX-Trigger': json.dumps({
                            "movieListChanged": None,
                            "showMessage": f"Kyc Updated Successfully"
                        })
                    })
               
            else:
                pass
        
        except AgentKyc.DoesNotExist:
            kyc_id = None

            # Create a new KYC record with the appropriate agent field
            if is_outsource_agent:
                kyc = AgentKyc.objects.create(
                    outsourceagent=agent,
                    adhar_card_front=adharfront_file,
                    adhar_card_back=adharback_file,
                    pancard=pan_file,
                    registration_certificate=registration_file,
                )
            else:
                kyc = AgentKyc.objects.create(
                    agent=agent,
                    adhar_card_front=adharfront_file,
                    adhar_card_back=adharback_file,
                    pancard=pan_file,
                    registration_certificate=registration_file,
                )

            kyc.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"Kyc Updated Successfully"
                    })
                }
            )


        # except AgentKyc.DoesNotExist:
        #     kyc_id = None
            

        #     kyc = AgentKyc.objects.create(
        #         agent=agent,
        #         adhar_card_front=adharfront_file,
        #         adhar_card_back=adharback_file,
        #         pancard=pan_file,
        #         registration_certificate=registration_file,
        #     )
        #     kyc.save()
        #     return HttpResponse(
        #         status=204,
        #         headers={
        #             'HX-Trigger': json.dumps({
        #                 "movieListChanged": None,
        #                 "showMessage": f"Kyc Updated Successfully"
        #             })
        #         })
            
    context ={
        'agent':agent,
        'document_type': document_type
    }
    return render(request,'crm/InternalManagement/AgentDetails/upload_kyc.html',context)



# ---------------------------OutSource Agent-------------------------


def outsource_agent_list(request):
    # Initialize the agent filter form with GET parameters
    agent_filter = OutSourceAgentFilter(request.GET)
    

    # Get the filtered queryset from the filter form (includes any date range filters and other filters)
    agents = agent_filter.qs
    logged_in_user = request.user

    if hasattr(logged_in_user, 'employee'):  # Assuming `employee` is the related field for Employee model
        
        # If employee, filter agents by `assign_to_employee`
        agents = agents.filter(assign_employee=logged_in_user)


    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # If there's a search query, build a Q object to filter agents based on multiple fields
    if search_query:
        search_terms = search_query.split()
        query = Q()

        for term in search_terms:
            query &= (Q(users__first_name__icontains=term) | 
                      Q(users__last_name__icontains=term) |
                      Q(contact_no__icontains=term) |
                      Q(country__icontains=term) |
                      Q(registeron__icontains=term) |
                      Q(registerdby__first_name__icontains=term) |
                      Q(registerdby__last_name__icontains=term) |
                      Q(assign_employee__first_name__icontains=term) |
                      Q(assign_employee__last_name__icontains=term))
        
        # Apply the search query on top of the filtered agents
        agents = agents.filter(query)

    # Get the start and end dates from the GET parameters (if they exist)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    print("start dateeee",start_date_str)

    # Apply the date filters if they exist
    if start_date_str:
        start_date = parse_date(start_date_str)  # Parse as naive date object (YYYY-MM-DD)
        if start_date:
            # Use registeron__date lookup to filter only by date, ignoring time
            agents = agents.filter(registeron__date__gte=start_date)

    if end_date_str:
        end_date = parse_date(end_date_str)  # Parse as naive date object (YYYY-MM-DD)
        if end_date:
            # Use registeron__date lookup to filter only by date, ignoring time
            agents = agents.filter(registeron__date__lte=end_date)

    # Paginate the filtered queryset
    paginator = Paginator(agents, 10)  # Adjust number of items per page if needed
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Prepare context to be rendered
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'agent_filter': agent_filter,  # This contains the form with date filters
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    
    # Render the response with the filtered agents
    return render(request, 'crm/InternalManagement/OutsourceAgent/Outsourceagent_list.html', context)




def outsource_agent_delete(request, pk):
    
    try:
        agent = get_object_or_404(OutSourcingAgent, pk=pk)
        custom_user = agent.users
        custom_user.delete()
        agent.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"OutSourceAgent Deleted Successfully"
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("OutsourceAgent not found")
    



def update_outsourceassign(request, pk):
    
    agent = get_object_or_404(OutSourcingAgent, pk=pk)
   

    if request.method == "POST":
        assign_rm = request.POST.get("rmIdInput")
        rm = CustomUser.objects.get(id=assign_rm)
        agent.assign_employee = rm
        agent.save()
       
            
        return HttpResponse(status=204, headers={
            'HX-Trigger': json.dumps({
                "movieListChanged":None,
                "showMessage":f"RM Assigned Successfully"

                })
            })
            
   
    context={
       'agent':agent
   }
    
    return render(request, 'crm/InternalManagement/Agent/assign.html',context)
 
# ----------------------------------------------------

def click(request):
    return redirect("product_details")

def product(request):
    # Get all packages grouped by their package_type
    package_choices = Package.PACKAGE_CHOICES
    packages_by_type = {}

    # Fetch packages grouped by type
    for package_type, _ in package_choices:
        packages_by_type[package_type] = Package.objects.filter(package_type=package_type)

    context = {
        "package_choices": package_choices,
        "packages_by_type": packages_by_type,  # Pass packages grouped by type
    }
    return render(request, 'crm/product.html', context)


def test(request):
   return render(request,'crm/test.html')


def emp_list(request):
   return render(request,'crm/employee_list.html')


def help_emp(request):
   return render(request,'crm/help.html')

def admin_load(request):
   
   return render(request,'crm/SuperAdmin/admin_load.html')


def admin_list(request):
   
   
   search_query = request.GET.get('search', '')
   
   search_terms = search_query.split()
   query = Q()

   for term in search_terms:
        query &= Q(superadmin__first_name__icontains=term) | Q(superadmin__last_name__icontains=term) | Q(superadmin__email__icontains=term) | Q(mobile__icontains=term)


   admins = Admin.objects.filter(query).order_by('-id')
   
   paginator = Paginator(admins, 3)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   return render(request,'crm/SuperAdmin/admin_list.html',context)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    
def admin_index(request):
   
   return render(request,'crm/SuperAdmin/index.html')

# def add_admin(request):
   
#    return render(request,'crm/SuperAdmin/add_admin.html')


from django.http import HttpResponse
import json


def add_admin(request):
    
    if request.method == "POST":
        # form = SuperAdminHODForm(request.POST)
        form = SuperAdminHODForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['mobile']
            password = form.cleaned_data['password']
            profile_pic = form.cleaned_data['profile_pic']

            if CustomUser.objects.filter(username=email).exists():
                
                    form.add_error('email', 'A user with this email already exists.')
            elif len(mobile) < 10:  # Check if mobile length is less than 10
                form.add_error('mobile', 'Mobile number must be at least 10 digits.')
            elif SuperAdminHOD.objects.filter(mobile=mobile).exists():
                    form.add_error('mobile', 'A user with this Mobile No already exists.')
            else:
                customuser = CustomUser.objects.create_user(username=email,first_name=first_name,last_name=last_name,email=email,password=password,user_type="2")
            
                customuser.superadminhod.mobile=mobile
                customuser.superadminhod.profile_pic=profile_pic


                customuser.save()
                return HttpResponse(status=204, headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged":None,
                        "showMessage":f"{customuser.first_name} {customuser.last_name} added."

                        })
                })

        
                # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        
    else:
        form = SuperAdminHODForm()

    context = {
        'form':form
    }
    
   
    return render(request, 'crm/SuperAdmin/add_admin.html',context)



def edit_admin(request, pk):
    admin = get_object_or_404(CustomUser, pk=pk)  # Fetch the admin instance to edit
    super_admin_hod_instance = admin.admin  # Get the related SuperAdminHOD instance

    if request.method == "POST":
        # Bind the form to the POST data and the admin instance
        form = SuperAdminHODForm(request.POST, request.FILES, instance=admin, user_instance=super_admin_hod_instance)

        if form.is_valid():
            print("okkkk")
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['contact_no']
            profile_pic = form.cleaned_data['profile_pic'] if form.cleaned_data['profile_pic'] else super_admin_hod_instance.file
            
            # Handle password separately
            password = form.cleaned_data['password']
            if password:  # Only update if a new password is provided
                admin.set_password(password)

            admin.first_name = first_name
            admin.last_name = last_name
            admin.email = email
            super_admin_hod_instance.mobile = mobile
            super_admin_hod_instance.profile_pic = profile_pic
            admin.save()
            super_admin_hod_instance.save()  # Don't forget to save the related instance
            print("custom userssss", admin)
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"{admin.first_name} {admin.last_name} Updated."

                    })
                })
            # return HttpResponse(status=204, headers={'HX-Trigger': 'movieListChanged'})
        else:
            print("Form errors:", form.errors)  # Print errors to see what's wrong

    else:
        # Initialize the form with the admin instance to pre-populate fields
        form = SuperAdminHODForm(instance=admin, user_instance=super_admin_hod_instance)

    context = {
        'form': form
    }
    return render(request, 'crm/SuperAdmin/add_admin.html', context)

from django.http import HttpResponse, HttpResponseNotFound

def delete_admin(request, pk):
    try:
        admin = get_object_or_404(CustomUser, pk=pk)
        admin.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Admin {admin.first_name} {admin.last_name} deleted."
            })
        })

        
        # return HttpResponse(status=204, headers={
        #     'HX-Trigger': json.dumps({
        #         "showMessage": f"Admin {admin.first_name} {admin.last_name} deleted."
        #     })
        # })
        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound("Admin not found")
    
from django.http import JsonResponse

def delete_multiple_admins(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')  # HTMX sends it as a list
        if ids:
            CustomUser.objects.filter(pk__in=ids).delete()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})






import sweetify

# def sweet_alert(request):
#     custom_html = '''
#         <div class="swal2-html-container">
#             <div class="mt-3">
#                 <lord-icon src="https://cdn.lordicon.com/gsqxdxog.json" trigger="loop" 
#                     colors="primary:#f7b84b,secondary:#f06548" style="width:100px;height:100px"></lord-icon>
#                 <div class="mt-4 pt-2 fs-15 mx-5">
#                     <h4>Are you Sure?</h4>
#                     <p class="text-muted mx-4 mb-0">Are you sure you want to delete this account?</p>
#                 </div>
#             </div>
#         </div>
#     '''
#     sweetify.warning(
#         request,
#         '',
#         html=custom_html,  # Custom HTML content
       
#         persistent='Ok',
        
#     )
#     # sweetify.success(request, 'Success!', text='Your operation was successful', persistent='Ok')
    
#     return render(request,'crm/home.html')



def sweet_alert(request):
    # custom_html = '''
    #     <div class="swal2-html-container">
    #         <div class="mt-3">
    #             <lord-icon src="https://cdn.lordicon.com/gsqxdxog.json" trigger="loop" 
    #                 colors="primary:#f7b84b,secondary:#f06548" style="width:100px;height:100px"></lord-icon>
    #             <div class="mt-4 pt-2 fs-15 mx-5">
    #                 <h4>Are you Sure?</h4>
    #                 <p class="text-muted mx-4 mb-0">Are you sure you want to delete this account?</p>
    #             </div>
    #         </div>
    #     </div>
    # '''
    
    # sweetify.sweetalert(
    #     request,
    #     title='',  # Leave title empty if you want to rely on custom HTML entirely
    #     html=custom_html,  # Custom HTML content
    #     persistent='Ok',
    #     icon=None  # Remove the default icon
    # )
    # sweetify.sweetalert(
    #     request,
    #     title='',  # Keep the title empty to rely on custom HTML
    #     html=custom_html,  # Custom HTML content
    #     showCancelButton=True,  # Display Cancel button
    #     confirmButtonText='Yes, Delete It!',
    #     confirmButtonClass='btn btn-primary w-xs me-2 mb-1',  # Custom confirm button class
    #     cancelButtonText='yes',
    #     cancelButtonClass='btn btn-danger w-xs mb-1',  # Custom cancel button class
    #     # buttonsStyling=False,  # Disable default SweetAlert button styling for custom buttons
    #     showCloseButton=True,  # Show the close button (X)
    #     persistent='Cancel',
    # )
    
    sweetify.success(request, 'Operation successful!', text='Your operation was completed.', persistent='OK')
    
    return render(request, 'crm/home.html')





def bulkMsg_load(request):
   
   return render(request,'crm/BulkMsg/bulkmsg_load.html')





# def bulkMsg_list(request):
   
   
#    search_query = request.GET.get('search', '')
   
#    search_terms = search_query.split()
#    query = Q()

#    for term in search_terms:
#         query &= Q(added_by__first_name__icontains=term) | Q(added_by__last_name__icontains=term) | Q(message__icontains=term)  | Q(added_at__icontains=term) 


#    admins = BulkMessage.objects.filter(query).order_by('-id')
  
   
#    paginator = Paginator(admins, 3)
#    page_number = request.GET.get('page', 1)
#    page_obj = paginator.get_page(page_number)
#    context = {
#        'page_obj' : page_obj,
#        'search_query':search_query,
      
#    }
#    return render(request,'crm/BulkMsg/bulkmsg_list.html',context)


def bulkMsg_list(request):
    # Get the search query from GET request
    search_query = request.GET.get('search', '')
    search_terms = search_query.split()
    query = Q()

    # Construct the search query
    for term in search_terms:
        query &= (Q(added_by__first_name__icontains=term) |
                  Q(added_by__last_name__icontains=term) |
                  Q(message__icontains=term) |
                  Q(added_at__icontains=term))

    # Get the logged-in user
    user = request.user

    # Check if the user is an admin or employee and filter accordingly
    if user.user_type == '2':  # Admin (user_type = 2)
        # Admin can see all messages
        admins = BulkMessage.objects.filter(query).order_by('-id')
    elif user.user_type == '3':  # Employee (user_type = 3)
        # Employee can only see their own messages
        admins = BulkMessage.objects.filter(added_by=user).filter(query).order_by('-id')
    else:
        # You can handle other user types here if needed
        admins = BulkMessage.objects.none()  # Return no results for non-admin/non-employee users

    # Set up pagination
    paginator = Paginator(admins, 3)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Context to pass to the template
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }

    # Return the rendered template with the context
    return render(request, 'crm/BulkMsg/bulkmsg_list.html', context)





# def add_bulkmsg(request):
#     if request.method == "POST":
#         form = BulkMessageForm(request.POST, request.FILES or None)
#         if form.is_valid():
#             user = request.user
#             form.instance.added_by = user
#             bulk_message_instance = form.save()
#             aisensy_api_url = "https://backend.aisensy.com/campaign/t1/api/v2"
#             api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1Zjk4M2ZmZTMxNWI1NDVjZDQ1Nzk3ZSIsIm5hbWUiOiJ0aGVza3l0cmFpbCA4NDEzIiwiYXBwTmFtZSI6IkFpU2Vuc3kiLCJjbGllbnRJZCI6IjY1Zjk4M2ZmZTMxNWI1NDVjZDQ1Nzk3NCIsImFjdGl2ZVBsYW4iOiJCQVNJQ19NT05USExZIiwiaWF0IjoxNzEwODUxMDcxfQ.XnS_3uclP8c0J6drYjBCAQmbE6bHxGuD2IAGPaS4N9Y" 
#             sample1 = bulk_message_instance.message
#             attachment_url = request.build_absolute_uri(bulk_message_instance.image.url)
#             agents = Agent.objects.filter(assign_employee=user)
#             outsourcing_agents = OutSourcingAgent.objects.filter(assign_employee=user)

#             for agent in agents:
#                 contact = agent.contact_no

#             if not contact.startswith("91"):
#                 contact = "91" + contact

#             payload = {
#                 "apiKey": api_key,
#                 "campaignName": "Updates",
#                 "destination": contact,  
#                 "userName": "Theskytrail 8413",
#                 "templateParams": [sample1],
#                 "source": "new-landing-page form",
#                 "media": {
#                     "url": attachment_url,
#                     "filename": bulk_message_instance.image.file.name
#                 },
#                 "buttons": [],
#                 "carouselCards": [],
#                 "location": {}
#             }

#             response = requests.post(aisensy_api_url, json=payload)
#             if response.status_code == 200:
#                 print("WhatsApp message sent successfully!")
#             else:
#                 print("Failed to send WhatsApp message:", response.text)

#             for outsourcing_agent in outsourcing_agents:
#                 contact = outsourcing_agent.contact_no

#             if not contact.startswith("91"):
#                 contact = "91" + contact

#             payload = {
#                 "apiKey": api_key,
#                 "campaignName": "Updates",
#                 "destination": contact,  
#                 "userName": "Theskytrail 8413",
#                 "templateParams": [sample1],
#                 "source": "new-landing-page form",
#                 "media": {
#                     "url": attachment_url,
#                     "filename": bulk_message_instance.image.file.name
#                 },
#                 "buttons": [],
#                 "carouselCards": [],
#                 "location": {}
#             }


#             headers = {"Content-Type": "application/json"}
#             response = requests.post(aisensy_api_url, json=payload,headers=headers)
#             if response.status_code == 200:
#                 print("WhatsApp message sent successfully!")
#             else:
#                 print("Failed to send WhatsApp message:", response.text)
#         # messages.success(request, "Bulk Messages sent successfully")
#         return HttpResponse(status=204, headers={
#                 'HX-Trigger': json.dumps({
#                     "movieListChanged": None,
#                     "showMessage": f" added."
#                 })
#             })
#         # return HttpResponseRedirect(reverse("emp_bulk_message_list"))
#     context = {"form": form}
#     return render(request, 'crm/BulkMsg/add_bulkmsg.html', context)
    




# def get_contact_number(user):
#     # Method to get the contact number based on user type
#     if user.user_type == "2":
#         return SuperAdminHOD.objects.get(superadmin=user).mobile
#     elif user.user_type == "3":
#         return Employee.objects.get(users=user).contact_no
#     elif user.user_type == "4":
#         return Agent.objects.get(users=user).contact_no
#     elif user.user_type == "5":
#         return OutSourcingAgent.objects.get(users=user).contact_no

#     return None


def get_contact_number(user):
    # Method to get the contact number based on user type
    if user.user_type == "2":
        superadmin = SuperAdminHOD.objects.filter(superadmin=user).first()
        return superadmin.mobile if superadmin else None
    elif user.user_type == "3":
        employee = Employee.objects.filter(users=user).first()
        return employee.contact_no if employee else None
    elif user.user_type == "4":
        agent = Agent.objects.filter(users=user).first()
        return agent.contact_no if agent else None
    elif user.user_type == "5":
        outsourcing_agent = OutSourcingAgent.objects.filter(users=user).first()
        return outsourcing_agent.contact_no if outsourcing_agent else None

    return None

# @login_required

def add_bulkmsg(request):
    # Initialize the form first, so it’s always available
    form = BulkMessageForm(request.POST, request.FILES or None)

    # Handle POST request
    if request.method == "POST":
        if form.is_valid():
           
            user = request.user
            

            
            form.instance.added_by = user
            bulk_message_instance = form.save()

            aisensy_api_url = "https://backend.aisensy.com/campaign/t1/api/v2"
            api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1Zjk4M2ZmZTMxNWI1NDVjZDQ1Nzk3ZSIsIm5hbWUiOiJ0aGVza3l0cmFpbCA4NDEzIiwiYXBwTmFtZSI6IkFpU2Vuc3kiLCJjbGllbnRJZCI6IjY1Zjk4M2ZmZTMxNWI1NDVjZDQ1Nzk3NCIsImFjdGl2ZVBsYW4iOiJCQVNJQ19NT05USExZIiwiaWF0IjoxNzEwODUxMDcxfQ.XnS_3uclP8c0J6drYjBCAQmbE6bHxGuD2IAGPaS4N9Y" 

            user_types = ["2", "3", "4", "5", "6"]


            sample1 = bulk_message_instance.message
            attachment_url = request.build_absolute_uri(bulk_message_instance.image.url)

            message_content = bulk_message_instance.message
            # agents = Agent.objects.filter(assign_employee=user)
            # print("agentssssssssssss",agents)
            # outsourcing_agents = OutSourcingAgent.objects.filter(assign_employee=user)

            for user_type in user_types:
                users = CustomUser.objects.filter(user_type=user_type)
                for user in users:
                    contact = get_contact_number(user) 
                    print("contact no",contact)
                # contact = agent.contact_no
                # if not contact.startswith("91"):
                #     contact = "91" + contact
                # print("contactttt",contact)

                    payload = {
                        "apiKey": api_key,
                        "campaignName": "Updates",
                        "destination": contact,  
                        "userName": "theskytrail 8413",
                        "templateParams": [sample1],
                        "source": "new-landing-page form",
                        "media": {
                            "url": attachment_url,
                            "filename": bulk_message_instance.image.file.name
                        },
                        "buttons": [],
                        "carouselCards": [],
                        "location": {}
                    }

                    response = requests.post(aisensy_api_url, json=payload)
                    if response.status_code == 200:
                        print(response.status_code)
                        print(response.text)

                        print("WhatsApp message sent successfully!")
                    else:
                        print("Failed to send WhatsApp message:", response.text)

            # for outsourcing_agent in outsourcing_agents:
            #     contact = outsourcing_agent.contact_no
            #     if not contact.startswith("91"):
            #         contact = "91" + contact

            #     payload = {
            #         "apiKey": api_key,
            #         "campaignName": "Updates",
            #         "destination": contact,  
            #         "userName": "theskytrail 8413",
            #         "templateParams": [sample1],
            #         "source": "new-landing-page form",
            #         "media": {
            #             "url": attachment_url,
            #             "filename": bulk_message_instance.image.file.name
            #         },
            #         "buttons": [],
            #         "carouselCards": [],
            #         "location": {}
            #     }

            #     headers = {"Content-Type": "application/json"}
            #     response = requests.post(aisensy_api_url, json=payload, headers=headers)
            #     if response.status_code == 200:
            #         print(response.status_code)
            #         print(response.text)
            #         print("WhatsApp message sent successfully!")
            #     else:
            #         print("Failed to send WhatsApp message:", response.text)

            # After processing the form, send the response
            return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged": None,
                    "showMessage": f"added."
                })
            })

    # If not a POST request or if the form is invalid, render the page with the form
    context = {"form": form}
    return render(request, 'crm/BulkMsg/add_bulkmsg.html', context)





def delete_bulkmsg(request, pk):
    try:
        bulkmsg = get_object_or_404(BulkMessage, pk=pk)
        bulkmsg.delete()  # This will also delete the associated SuperAdminHOD because of cascade delete
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Successfully deleted."
            })
        })

        
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound(" not found")
    




# ------------------------------- Reports --------------------------


# @login_required
def report_load(request):
   
   return render(request,'crm/Report/reportLoad.html')




def report_list(request):
    # Get the search query from the GET request
   
    search_query = request.GET.get('search', '')
   
    # Split the search query into terms
    search_terms = search_query.split()
    query = Q()

    # Build the search query
    for term in search_terms:
        query &= Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term) | Q(notes__icontains=term)

    # Check the user type and filter News accordingly
    user = request.user  # Get the logged-in user
    print("ggggggg",user)
    
    if user.user_type == "2":  # Admin user (user_type = 2)
        # Show all news for admin (no filter)
        report = Report.objects.filter(query).distinct().order_by('-id')
    elif user.user_type == "3":  # Employee user (user_type = 3)
        # Show news relevant to employees (employee=True)
        report = Report.objects.filter(query).distinct().order_by('-id')
    elif user.user_type == "4":  # Agent user (user_type = 4)
        # Show news relevant to agents (agent=True)
        report = Report.objects.filter(user=user).filter(query).distinct().order_by('-id')
    elif user.user_type == "5":  # Out Sourcing Agent user (user_type = 5)
        # Show news relevant to outsourcing agents (outsource_Agent=True)
        report = Report.objects.filter(user=user).filter(query).distinct().order_by('-id')
    else:
        # If no valid user_type, return no news (or handle other user types)
        report = Report.objects.none()

    # Pagination setup
    paginator = Paginator(report, 3)  # Show 3 news items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'crm/Report/report_list.html', context)





# ------------------------------------ Lead -------------------



# def add_lead(request):
   
#    return render(request,'crm/Leads/add_lead.html')


class add_lead(LoginRequiredMixin, CreateView):
    def get(self, request):
        form = EnquiryForm1()
        return render(
            request,
            "crm/Leads/add_lead1.html",
            {"form": form},
        )

    def post(self, request):
        form = EnquiryForm1(request.POST)
        agent_id = request.POST.get('agent')
        
        if form.is_valid():
            cleaned_data = {
                "FirstName": form.cleaned_data["FirstName"],
                "LastName": form.cleaned_data["LastName"],
                "email": form.cleaned_data["email"],
                "contact": form.cleaned_data["contact"],
                "Dob": form.cleaned_data["Dob"].strftime("%Y-%m-%d"),
                "Gender": form.cleaned_data["Gender"],
                "Country": form.cleaned_data["Country"],
                "passport_no": form.cleaned_data["passport_no"],
                "refusal": form.cleaned_data["refusal"],
                "refusal_country": form.cleaned_data["refusal_country"],
                "assign_to_agent":agent_id
            }
            request.session["enquiry_form1"] = cleaned_data
            return redirect("enquiry_form2")

        return render(
            request,
            "crm/Leads/lead2.html",
            {"form": form},
        )



class Enquiry2View(LoginRequiredMixin, CreateView):
    def get(self, request):
        form = EnquiryForm2()
        return render(
            request,
            "crm/Leads/lead2.html",
            {"form": form},
        )

    def post(self, request):
        form = EnquiryForm2(request.POST)
        if form.is_valid():
            # Retrieve personal details from session
            enquiry_form1 = request.session.get("enquiry_form1", {})

            cleaned_data = {
                "spouse_name": form.cleaned_data["spouse_name"],
                "spouse_no": form.cleaned_data["spouse_no"],
                "spouse_email": form.cleaned_data["spouse_email"],
                "spouse_passport": form.cleaned_data["spouse_passport"],
                "spouse_relation": form.cleaned_data["spouse_relation"],
                "spouse_name1": form.cleaned_data["spouse_name1"],
                "spouse_no1": form.cleaned_data["spouse_no1"],
                "spouse_email1": form.cleaned_data["spouse_email1"],
                "spouse_passport1": form.cleaned_data["spouse_passport1"],
                "spouse_relation1": form.cleaned_data["spouse_relation1"],
                "spouse_name2": form.cleaned_data["spouse_name2"],
                "spouse_no2": form.cleaned_data["spouse_no2"],
                "spouse_email2": form.cleaned_data["spouse_email2"],
                "spouse_passport2": form.cleaned_data["spouse_passport2"],
                "spouse_relation2": form.cleaned_data["spouse_relation2"],
                "spouse_name3": form.cleaned_data["spouse_name3"],
                "spouse_no3": form.cleaned_data["spouse_no3"],
                "spouse_email3": form.cleaned_data["spouse_email3"],
                "spouse_passport3": form.cleaned_data["spouse_passport3"],
                "spouse_relation3": form.cleaned_data["spouse_relation3"],
                "spouse_name4": form.cleaned_data["spouse_name4"],
                "spouse_no4": form.cleaned_data["spouse_no4"],
                "spouse_email4": form.cleaned_data["spouse_email4"],
                "spouse_passport4": form.cleaned_data["spouse_passport4"],
                "spouse_relation4": form.cleaned_data["spouse_relation4"],
                "spouse_name5": form.cleaned_data["spouse_name5"],
                "spouse_no5": form.cleaned_data["spouse_no5"],
                "spouse_email5": form.cleaned_data["spouse_email5"],
                "spouse_passport5": form.cleaned_data["spouse_passport5"],
                "spouse_relation5": form.cleaned_data["spouse_relation5"],
            }

            for i in range(1, 6):
                spouse_dob = form.cleaned_data.get("spouse_dob")
                spouse_dob = form.cleaned_data.get(f"spouse_dob{i}")

                if spouse_dob:
                    cleaned_data["spouse_dob"] = spouse_dob.strftime("%Y-%m-%d")
                    cleaned_data[f"spouse_dob{i}"] = spouse_dob.strftime("%Y-%m-%d")

            # Merge personal details with receiver details
            merged_data = {**enquiry_form1, **cleaned_data}

            # Save the merged data to the session
            request.session["enquiry_form2"] = merged_data
            return redirect("enquiry_form3")

        return render(
            request,
            "crm/Leads/lead2.html",
            {"form": form},
        )



class Enquiry3View(LoginRequiredMixin, CreateView):
    def get(self, request):
        form = EnquiryForm3()
        return render(
            request,
            "crm/Leads/lead3.html",
            {"form": form},
        )

    def post(self, request):
        form1_data = request.session.get("enquiry_form1", {})
        form2_data = request.session.get("enquiry_form2", {})
        form3 = EnquiryForm3(request.POST)

        if form3.is_valid():
            user = self.request.user

            # Merge data from all three forms
            merged_data = {
                **form1_data,
                **form2_data,
                **form3.cleaned_data,
            }

            assign_to_agent_id = merged_data.get("assign_to_agent")
            if assign_to_agent_id:
                try:
                    agent_instance = Agent.objects.get(id=assign_to_agent_id)
                except Agent.DoesNotExist:
                    agent_instance = None
            else:
                agent_instance = None
            merged_data["assign_to_agent"] = agent_instance


            # if "spouse_name" in form2_data:
            #     # Convert the input string into a list for spouse_name
            #     spouse_names = [
            #         item.strip() for item in form2_data["spouse_name"].split(",")
            #     ]
            #     merged_data["spouse_name"] = spouse_names
            # merged_data["spouse_name"] = spouse_names

            # Save the merged data to the database
            enquiry = Enquiry(**merged_data)
            # ---------------------------------------

            last_assigned_index = cache.get("last_assigned_index") or 0
            # If no student is assigned, find the next available student in a circular manner
            presales_team_employees = Employee.objects.filter(department="Presales")

            if presales_team_employees.exists():
                next_index = (last_assigned_index + 1) % presales_team_employees.count()
                enquiry.assign_to_employee = presales_team_employees[next_index]
                enquiry.assign_to_employee.save()

                cache.set("last_assigned_index", next_index)

            # ------------------------------
            enquiry.created_by = user
            enquiry.save()
            lead_id = enquiry.id

            # create_notification(enquiry.assign_to_employee, "New Enquiry Added")
            # create_notification(enquiry.assign_to_employee, "New Enquiry Added",lead_id=lead_id,is_admin=False)

            # current_count = Notification.objects.filter(
            #     is_seen=False, employee=enquiry.assign_to_employee
            # ).count()
            try:
                employee_id = enquiry.assign_to_employee.id
                # send_notification(employee_id, "New Enquiry Added", current_count)
            except Exception as e:
                pass

            # messages.success(request, "Enquiry Added successfully")

            # Clear session data after successful submission
            request.session.pop("enquiry_form1", None)
            request.session.pop("enquiry_form2", None)

            return redirect("enquiry_form4", id=enquiry.id)

        return render(
            request,
            "crm/Leads/lead3.html",
            {"form": form3},
        )

    def get_success_url(self):
        enquiry_id = self.object.id
        return reverse_lazy("enquiry_form4", kwargs={"id": enquiry_id})


# def enquiry4(request,id):
#     enq = Enquiry.objects.get(id=id)
    
#     document = Document.objects.all()
#     doc_file = DocumentFiles.objects.filter(enquiry_id=enq)
#     case_categories = CaseCategoryDocument.objects.filter(country=enq.Visa_country)
#     documents_prefetch = Prefetch(
#         "document",
#         queryset=Document.objects.select_related("document_category", "lastupdated_by"),
#     )
#     case_categories = case_categories.prefetch_related(documents_prefetch)

#     grouped_documents = {}

#     for case_category in case_categories:
#         for document in case_category.document.all():
#             document_category = document.document_category
#             testing = document.document_category.id

#             if document_category not in grouped_documents:
#                 grouped_documents[document_category] = []

#             grouped_documents[document_category].append(document)

#     context = {
#         "enq": enq,
#         "grouped_documents": grouped_documents,
#         "doc_file": doc_file,
#     }

#     return render(request,'crm/Leads/lead4.html',context)


from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch

def enquiry4(request, id):
    # Fetch the Enquiry object or return a 404 error
    print("sooopppppppppppppppppppppp")
    enq = get_object_or_404(Enquiry, id=id)

    # Fetch DocumentFiles associated with the enquiry
    doc_file = DocumentFiles.objects.filter(enquiry_id=enq)

    # Prefetch related documents for case categories
    case_categories = CaseCategoryDocument.objects.filter(country=enq.Visa_country).prefetch_related(
        Prefetch(
            "document",
            queryset=Document.objects.select_related("document_category", "lastupdated_by"),
        )
    )

    # Group documents by their category
    grouped_documents = {}
    for case_category in case_categories:
        for document in case_category.document.all():
            document_category = document.document_category
            if document_category not in grouped_documents:
                grouped_documents[document_category] = []
            grouped_documents[document_category].append(document)

    # Context for the template
    expected_path = f"/enquiry/{enq.id}/"
    context = {
        "enq": enq,
        "expected_path":expected_path
        # "grouped_documents": grouped_documents,
        # "doc_file": doc_file,
    }

    return render(request, 'crm/Leads/lead4.html', context)

def enquiry_details(request,id):

    enq = get_object_or_404(Enquiry, id=id)

    # Fetch DocumentFiles associated with the enquiry
    doc_file = DocumentFiles.objects.filter(enquiry_id=enq)

    # Prefetch related documents for case categories
    case_categories = CaseCategoryDocument.objects.filter(country=enq.Visa_country).prefetch_related(
        Prefetch(
            "document",
            queryset=Document.objects.select_related("document_category", "lastupdated_by"),
        )
    )

    # Group documents by their category
    grouped_documents = {}
    for case_category in case_categories:
        for document in case_category.document.all():
            document_category = document.document_category
            if document_category not in grouped_documents:
                grouped_documents[document_category] = []
            grouped_documents[document_category].append(document)

    # Context for the template
    context = {
        "enq": enq,
        "grouped_documents": grouped_documents,
        "doc_file": doc_file,
    }

    return render(request, 'crm/Leads/enquiry/denqiry_details.html',context)


def upload_document(request,id):
    enquiry_id = request.GET.get('enquiry_id')
    
    # print("idddd",id)
    if request.method == "POST":
        document_id = id
        print("document issss",document_id)
        enq_id = request.POST.get("enq_id")
        document = Document.objects.get(pk=document_id)
        document_file = request.FILES.get("document_file")
        enq = Enquiry.objects.get(id=enq_id)
       
        documest_files = DocumentFiles.objects.create(
            document_file=document_file,
            document_id=document,
            enquiry_id=enq,
            lastupdated_by=request.user,
        )
        documest_files.save()
        return HttpResponse(
                    status=204,
                    headers={
                        'HX-Trigger': json.dumps({
                            "movieListChanged": None,
                            "showMessage": f"Document Uploaded Successfully!!"
                        })
                    })
        # return redirect("enquiry_form4", id)
    context = {
        'enquiry_id':enquiry_id
    }
    return render(request,'crm/Leads/upload_document.html',context)


def delete_docfile(request, id):
    doc_id = DocumentFiles.objects.get(id=id)
    enq_id = Enquiry.objects.get(id=doc_id.enquiry_id.id)
    enqq = enq_id.id

    doc_id.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Document Deleted."
            })
        })

       
        
    # except CustomUser.DoesNotExist:
    #     return HttpResponseNotFound("Country not found")
    
    # return redirect("enquiry_form4", enqq)



def agent_search_view(request):
    print("ggggggggooooooooooooo")
    
    query = request.GET.get("q", "")  # The search query from the dropdown
    # Fetch a limited number of agents that match the query
    agents = Agent.objects.filter(
        Q(users__first_name__icontains=query) |  # Match on first name
        Q(users__last_name__icontains=query)    # Match on last name
              # Match on agent type
    )  # Limit results to avoid too many results at once

    # Format the response for Select2
    results = [
        {
            "id": agent.id,
            "text": f"{agent.users.first_name} {agent.users.last_name} - {agent.type}",  # How results appear in the dropdown
        }
        for agent in agents
    ]

    return JsonResponse({"results": results})


from django.http import JsonResponse
from .models import Agent

def agent_search(request):
    print("ooooooooooo")
    query = request.GET.get('q', '')  # Get the search query from the request
    if query:
        # Search agents based on name (case-insensitive)
        # agents = Agent.objects.filter(name__icontains=query)
        agents = Agent.objects.filter(
        Q(users__first_name__icontains=query) |  # Match on first name
        Q(users__last_name__icontains=query)    # Match on last name
              # Match on agent type
        
    )  # Limit results to avoid too many results at once

        print("agentsssss",agents)


    else:
        agents = Agent.objects.none()  # If no query, return empty queryset

    # Format agents for Select2
    # results = [{'id': agent.id, 'text': agent.name} for agent in agents]
    results = [
        {
            "id": agent.id,
            "text": f"{agent.users.first_name} {agent.users.last_name} - {agent.type}",  # How results appear in the dropdown
        }
        for agent in agents
    ]

    return JsonResponse({'results': results})



def outagent_search_view(request):
   
    
    query = request.GET.get("q", "")  # The search query from the dropdown
    # Fetch a limited number of agents that match the query
    outagents = OutSourcingAgent.objects.filter(
        Q(users__first_name__icontains=query) |  # Match on first name
        Q(users__last_name__icontains=query)    # Match on last name
              # Match on agent type
    ) # Limit results to avoid too many results at once

    # Format the response for Select2
    results = [
        {
            "id": outagent.id,
            "text": f"{outagent.users.first_name} {outagent.users.last_name} - {outagent.type}",  # How results appear in the dropdown
        }
        for outagent in outagents
    ]

    return JsonResponse({"results": results})




def color_code(request, id):
    enquiry = Enquiry.objects.get(id=id)
   
    if request.method == "POST":
        color_code = request.POST.get("color_code")
        
        enquiry.color_code = color_code
        enquiry.save()
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Colour code updated Successfully !!"
            })
        })
        # messages.success(request, f"Lead Color {color_code} Updated Successfully...")

    context = {
        'enquiry':enquiry
    }
    return render(request,'crm/Leads/color_modal.html',context)


def lead_updated(request, id):
    excluded_statuses = ["Accept","Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    enquiry = Enquiry.objects.get(id=id)
    if request.method == "POST":
        lead_status = request.POST.get("lead_status")
        
        enquiry.lead_status = lead_status
        enquiry.save()
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Lead Status Updated Successfully!!"
            })
        })
        # messages.success(request, f"Lead {lead_status} Status Updated Successfully...")

        
        # redirect_to = request.POST.get("redirect_to")
        # redirect_url = redirect_to
        
        # return redirect(redirect_url)
    context = {
        'enquiry_id':enquiry,
        "lead": lead,
    }
    return render(request,'crm/Leads/lead_status_update_modal.html',context)


def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        data = response.json()
        return data["ip"]
    except Exception as e:
        # Handle the exception (e.g., log the error)
        return None


def add_notes(request,id):
    enq = Enquiry.objects.get(id=id)
    print("enquiry.....",enq)
    if request.method == "POST":
        
        notes_text = request.POST.get("notes")
        file = request.FILES.get("file")
        user = request.user

        try:
            # enq = Enquiry.objects.get(id=enq_id)
            ip_address = get_public_ip()

            notes = Notes.objects.create(
                enquiry=enq,
                notes=notes_text,
                file=file,
                ip_address=ip_address,
                created_by=user,
            )
            notes.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"Notes Added Successfully!!"
                    })
                })
            # messages.success(request, "Notes Added Successfully...")
        except Enquiry.DoesNotExist:
            pass

        
        # redirect_to = request.POST.get("redirect_to")
        # redirect_url = redirect_to
        
        # return redirect(redirect_url)
    return render(request,'crm/Leads/add_notes_modal.html')




def appointment_Save(request,id):
    if request.method == "POST":
        # enq = request.POST.get("enq_id")
        enq_id = Enquiry.objects.get(id=id)

        desc = request.POST.get("description")
        date = request.POST.get("date")
        time = request.POST.get("time")

        try:
            enqapp = EnqAppointment.objects.get(enquiry=enq_id)

            # Existing EnqAppointment found

            enqapp.description = desc
            enqapp.enquiry = enq_id
            enqapp.date = date
            enqapp.time = time
            enqapp.created_by = request.user
            enqapp.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"Appointment Added Successfully!!"
                    })
                })
        except EnqAppointment.DoesNotExist:
            # No existing EnqAppointment found, create a new one
            appt = EnqAppointment.objects.create(
                enquiry=enq_id,
                description=desc,
                date=date,
                time=time,
                created_by=request.user,
            )
            appt.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "movieListChanged": None,
                        "showMessage": f"Appointment Added Successfully!!"
                    })
                })

        # return redirect("admin_new_leads_details")
    return render(request,'crm/Leads/add_appointment_lead_modal.html')


def lead_load(request):
   
   return render(request,'crm/Leads/lead_load.html')



def all_lead(request):
    
    
   search_query = request.GET.get('search', '')
   search_terms = search_query.split()
   query  = Q(archive=False)
   for term in search_terms:
    
        # query &= Q(lastupdated_by__first_name__icontains=term) | Q(lastupdated_by__last_name__icontains=term) | Q(country__icontains=term) 
        query &= Q(FirstName__icontains=term) | Q(LastName__icontains=term) | Q(enquiry_number__icontains=term) | Q(passport_no__icontains=term) | Q(registered_on__icontains=term) | Q(Visa_country__country__icontains=term) | Q(Visa_type__icontains=term) | Q(created_by__username__icontains=term) | Q(Visa_category__category__icontains=term) | (Q(assign_to_agent__users__first_name__icontains=term) |  # Both First Name
     Q(assign_to_agent__users__last_name__icontains=term)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=term) |  Q(assign_to_outsourcingagent__users__last_name__icontains=term)) |   Q(Dob__icontains=term)

   all_lead = Enquiry.objects.filter(query).order_by("-id")
   
   paginator = Paginator(all_lead, 5)
   page_number = request.GET.get('page', 1)
   page_obj = paginator.get_page(page_number)
   context = {
       'page_obj' : page_obj,
       'search_query':search_query,
      
   }
   
   return render(request,'crm/Leads/all_lead.html',context)
def get_agent():
    return Agent.objects.all()


def get_outsourcepartner():
    return OutSourcingAgent.objects.all()

# def enrolled_lead(request):
   
    
#     excluded_statuses = ["Accept","Reject"]
#     lead = [status for status in leads_status if status[0] not in excluded_statuses]
#     enquiry = Enquiry.objects.filter(lead_status="Enrolled").order_by("-id")

#     search_query = request.GET.get('query', '')
#     print('searchhhh queryss')
   
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')

#     queries = Q(lead_status="Enrolled") & Q(archive=False)
#     if search_query:
#         search_parts = search_query.split()
#         print("search queryyyyy",search_parts)
#         for part in search_parts:
#             # queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part)
#             queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) |  # Both First Name                                                                                                                                                                                                                                                                                                                                                              
#             Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) |  Q(assign_to_outsourcingagent__users__last_name__icontains=part)) |   Q(Dob__icontains=part)

#     if start_date:
#         start_date = parse_date(start_date)
#         queries &= Q(registered_on__date__gte=start_date)

#     if end_date:
#         end_date = parse_date(end_date)
#         queries &= Q(registered_on__date__lte=end_date)




#     enquiry_list = Enquiry.objects.filter(queries).order_by("-id")

#     paginator = Paginator(enquiry_list, 10)
#     page_number = request.GET.get('page')
    
    
#     page = paginator.get_page(page_number)

#     presales_employees = get_presale_employee()
#     sales_employees = get_sale_employee()
#     documentation_employees = get_documentation_team_employee()
#     visa_team = get_visa_team_employee()
#     assesment_employee = get_assesment_employee()
#     agent = get_agent()
#     outsourcepartner = get_outsourcepartner()

#     context = {
#         # "enquiry": enquiry,
#         "presales_employees": presales_employees,
#         "sales_employees": sales_employees,
#         "documentation_employees": documentation_employees,
#         "visa_team": visa_team,
#         "assesment_employee": assesment_employee,
#         "agent": agent,
#         "outsourcepartner": outsourcepartner,
#         "lead": lead,
#         "page_obj": page,
#         # "base_url":base_url,
#         "search_query":search_query,
#         'start_date': start_date,
#         'end_date': end_date
#     }
    
   
#     return render(request,'crm/Leads/enrolled_lead.html',context)


def enrolled_lead(request):
    search_query = request.GET.get('search', '')  # 'search' ko 'query' se replace karen
   

    # Aapke existing query logic ko aap jese hain waisa use kar sakte hain
    queries = Q(lead_status="Enrolled") & Q(archive=False)
    if search_query:
        search_parts = search_query.split()
       
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part)

    # Start date and end date logic (same as existing)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")

    paginator = Paginator(enquiry_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'crm/Leads/enrolled_lead.html', context)



# def lead_cancel(request):
#     excluded_statuses = ["Accept","Reject"]
#     lead = [status for status in leads_status if status[0] not in excluded_statuses]
   
#     search_query = request.GET.get('query', '')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')

#     queries = Q(archive=True)
#     if search_query:
#         search_parts = search_query.split()
#         for part in search_parts:
#             # queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part)
#             queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) |  # Both First Name                                                                                                                                                                                                                                                                                                                                                              
#             Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) |  Q(assign_to_outsourcingagent__users__last_name__icontains=part)) |   Q(Dob__icontains=part)

#     if start_date:
#         start_date = parse_date(start_date)
#         queries &= Q(registered_on__date__gte=start_date)

#     if end_date:
#         end_date = parse_date(end_date)
#         queries &= Q(registered_on__date__lte=end_date)




#     enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
   
#     paginator = Paginator(enquiry_list, 10)
#     page_number = request.GET.get('page')
    
    
#     page = paginator.get_page(page_number)

  
#     visa_team = get_visa_team_employee()
    
#     agent = get_agent()
#     outsourcepartner = get_outsourcepartner()

#     context = {
#         # "enquiry": enquiry,
       
#         "visa_team": visa_team,
        
#         "agent": agent,
#         "outsourcepartner": outsourcepartner,
#         "lead": lead,
#         "page_obj": page,
#         # "base_url":base_url,
#         "search_query":search_query,
#         'start_date': start_date,
#         'end_date': end_date
#     }
#     print("start deta..................",start_date )
   
   
#     return render(request,'crm/Leads/lead_cancel.html',context)


def lead_cancel(request):
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(archive=True)
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    visa_team = get_visa_team_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "visa_team": visa_team,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   
    return render(request, 'crm/Leads/lead_cancel.html', context)


def lead_active(request):
   
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="Active") | Q(lead_status="PreEnrolled")
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   
   
    return render(request,'crm/Leads/active_lead.html',context)

def lead_inprocess(request):
   
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="Inprocess") | Q(lead_status="Ready To Submit")
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   
   
    return render(request,'crm/Leads/inprocess_lead.html',context)

def lead_appointment(request):
    
   
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="Appointment") 
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   
   
    return render(request,'crm/Leads/appointment_lead.html',context)

def result_awaited(request):


    
   
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="Result Awaited") 
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   

    
   
   
    return render(request,'crm/Leads/result_awaited.html',context)

def lead_new(request):

    
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="New Lead")
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    print("ggggggggggg",enquiry_list.count())
    
    # Pagination
    paginator = Paginator(enquiry_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   

    


   
    return render(request,'crm/Leads/new_lead.html',context)

def lead_approved(request):
   
   
   
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="Approved") 
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   
   
    return render(request,'crm/Leads/lead_approved.html',context)

def lead_completed(request):
    
   
    excluded_statuses = ["Accept", "Reject"]
    lead = [status for status in leads_status if status[0] not in excluded_statuses]
    
    # Get the search query
    search_query = request.GET.get('search', '')  # Here 'search' is used instead of 'query'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Define the base query
    queries = Q(lead_status="Ready To Collection") 
    
    # Add search filter to the query if there's a search term
    if search_query:
        search_parts = search_query.split()
        for part in search_parts:
            queries &= Q(FirstName__icontains=part) | Q(LastName__icontains=part) | Q(enquiry_number__icontains=part) | Q(passport_no__icontains=part) | Q(registered_on__icontains=part) | Q(Visa_country__country__icontains=part) | Q(Visa_type__icontains=part) | Q(created_by__username__icontains=part) | Q(Visa_category__category__icontains=part) | (Q(assign_to_agent__users__first_name__icontains=part) | Q(assign_to_agent__users__last_name__icontains=part)) | (Q(assign_to_outsourcingagent__users__first_name__icontains=part) | Q(assign_to_outsourcingagent__users__last_name__icontains=part)) | Q(Dob__icontains=part)

    # Add date filters to the query if provided
    if start_date:
        start_date = parse_date(start_date)
        queries &= Q(registered_on__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        queries &= Q(registered_on__date__lte=end_date)

    # Fetch the filtered enquiry list
    enquiry_list = Enquiry.objects.filter(queries).order_by("-id")
    
    # Pagination
    paginator = Paginator(enquiry_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    # Context to render
    presales_employees = get_presale_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    assesment_employee = get_assesment_employee()
    agent = get_agent()
    outsourcepartner = get_outsourcepartner()

    context = {
        "presales_employees": presales_employees,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
        "assesment_employee": assesment_employee,
        "agent": agent,
        "outsourcepartner": outsourcepartner,
        "lead": lead,
        "page_obj": page,
        "search_query": search_query,
        'start_date': start_date,
        'end_date': end_date
    }
   
    return render(request,'crm/Leads/lead_completed.html',context)



def get_presale_employee():
    return Employee.objects.filter(department="Presales")


def get_assesment_employee():
    return Employee.objects.filter(department="Assesment")


def get_sale_employee():
    return Employee.objects.filter(department="Sales")




def get_documentation_team_employee():
    return Employee.objects.filter(department="Documentation")


def get_visa_team_employee():
    return Employee.objects.filter(department="Visa Team")


# @login_required
def update_assigned_employee(request, id):
    enquiry = Enquiry.objects.get(id=id)
    presales_employees = get_presale_employee()
    assesment_employee = get_assesment_employee()
    sales_employees = get_sale_employee()
    documentation_employees = get_documentation_team_employee()
    visa_team = get_visa_team_employee()
    if request.method == "POST":
        ######### ASSIGN CODE #########
        try:
            assign_to_employee = request.POST.get("assign_to_employee")
            
            emp = Employee.objects.get(id=assign_to_employee)
            enquiry.assign_to_employee = emp
            employee_id = emp.id
            lead_id=enquiry.id
            # create_notification(emp, "New Lead Assign Added",lead_id=lead_id,is_admin=False)

            # current_count = Notification.objects.filter(
            #     is_seen=False, employee=assign_to_employee
            # ).count()
            # assign_notification(employee_id, "New Lead Assign Added", current_count)

        except Employee.DoesNotExist:
            if enquiry.assign_to_employee is None:
                enquiry.assign_to_employee = None
            else:
                pass

        try:
            assign_to_assesment_employee = request.POST.get(
                "assign_to_assesment_employee"
            )
            emp = Employee.objects.get(id=assign_to_assesment_employee)
            enquiry.assign_to_assesment_employee = emp

            employee_id = emp.id
            lead_id=enquiry.id
            # create_notification(emp, "New Assign Added")
            # create_notification(emp, "Lead Active assign Added",lead_id=lead_id,is_admin=False)

            # current_count = Notification.objects.filter(
            #     is_seen=False, employee=employee_id
            # ).count()
            # assign_notification(employee_id, "Lead Active Assign Added", current_count)

        except Employee.DoesNotExist:
            if enquiry.assign_to_assesment_employee is None:
                enquiry.assign_to_assesment_employee = None
            else:
                pass

        try:
            assign_to_sales_employee = request.POST.get("assign_to_sales_employee")
            emp = Employee.objects.get(id=assign_to_sales_employee)
            enquiry.assign_to_sales_employee = emp

            employee_id = emp.id
            lead_id=enquiry.id
            # create_notification(emp, "New Assign Added")
            # create_notification(emp, "PreEnrolled Lead assign Added",lead_id=lead_id,is_admin=False)

            # current_count = Notification.objects.filter(
            #     is_seen=False, employee=employee_id
            # ).count()
            # assign_notification(employee_id, "PreEnrolled Lead assign Added", current_count)

        except Employee.DoesNotExist:
            if enquiry.assign_to_sales_employee is None:
                enquiry.assign_to_sales_employee = None
            else:
                pass

        try:
            assign_to_documentation_employee = request.POST.get(
                "assign_to_documentation_employee"
            )
            emp = Employee.objects.get(id=assign_to_documentation_employee)
            enquiry.assign_to_documentation_employee = emp

            employee_id = emp.id
            lead_id=enquiry.id
            # create_notification(emp, "New Lead Assign Added")
            # create_notification(emp, "Documentation Lead assign Added",lead_id=lead_id,is_admin=False)


            # current_count = Notification.objects.filter(
            #     is_seen=False, employee=employee_id
            # ).count()
            # assign_notification(employee_id, "Documentation Lead assign Added", current_count)

        except Employee.DoesNotExist:
            if enquiry.assign_to_documentation_employee is None:
                enquiry.assign_to_documentation_employee = None
            else:
                pass

        try:
            assign_to_visa_team_employee = request.POST.get(
                "assign_to_visa_team_employee"
            )
            emp = Employee.objects.get(id=assign_to_visa_team_employee)
            enquiry.assign_to_visa_team_employee = emp

            employee_id = emp.id
            lead_id=enquiry.id
            # create_notification(emp, "New Assign Added")
            # create_notification(emp, "Visa Team Lead assign Added",lead_id=lead_id,is_admin=False)

            # current_count = Notification.objects.filter(
            #     is_seen=False, employee=employee_id
            # ).count()
            # assign_notification(employee_id, "Visa Team Lead assign Added", current_count)

        except Employee.DoesNotExist:
            if enquiry.assign_to_visa_team_employee is None:
                enquiry.assign_to_visa_team_employee = None
            else:
                pass
        enquiry.save()
        # messages.success(request, "Lead Assigned Successfully...")
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Document Deleted."
            })
        })
        # redirect_to = request.POST.get("redirect_to")
        # redirect_url = redirect_to
        
        # return redirect(redirect_url)
    context = {
        'enquiry':enquiry,
        "presales_employees": presales_employees,
        "assesment_employee": assesment_employee,
        "sales_employees": sales_employees,
        "documentation_employees": documentation_employees,
        "visa_team": visa_team,
    }
    return render(request,'crm/Leads/assign_to_employee_modal.html',context)
    



# @login_required
def update_assigned_agent(request, id):
    enquiry = Enquiry.objects.get(id=id)
    if request.method == "POST":
       
        try:
            assign_to_agent = request.POST.get("agent_id")
            agent = Agent.objects.get(id=assign_to_agent)
            enquiry.assign_to_agent = agent

            agent_id = agent.id
            # create_notification_agent(agent, "New Lead Assign Added")
         

        except Agent.DoesNotExist:
            if enquiry.assign_to_agent is None:
                enquiry.assign_to_agent = None
            else:
                pass

        enquiry.save()
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Lead Assigned Successfully..."
            })
        })
    context = {
        'enquiry':enquiry
    }
    return render(request,'crm/Leads/assign_to_agent_modal.html',context)
        # messages.success(request, "Lead Assigned Successfully...")
        
        
        # redirect_to = request.POST.get("redirect_to")
        # redirect_url = redirect_to
        
        # return redirect(redirect_url)




# @login_required
def update_assigned_op(request, id):
    enquiry = Enquiry.objects.get(id=id)
    if request.method == "POST":
        try:
            assign_to_outsourcingagent = request.POST.get("opagent_id")
            
            outsourcepartner = OutSourcingAgent.objects.get(
                id=assign_to_outsourcingagent
            )
            enquiry.assign_to_outsourcingagent = outsourcepartner

            agent_id = assign_to_outsourcingagent
            # create_notification_outsourceagent(
            #     outsourcepartner, "New Lead Assign Added"
            # )

            # current_count = Notification.objects.filter(
            #     is_seen=False, outsourceagent=assign_to_outsourcingagent
            # ).count()
            # assignop_notification(agent_id, "New Lead Assign Added", current_count)

        except OutSourcingAgent.DoesNotExist:
            if enquiry.assign_to_outsourcingagent is None:
                enquiry.assign_to_outsourcingagent = None
            else:
                pass

        enquiry.save()
        return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps({
                "movieListChanged": None,
                "showMessage": f"Lead Assigned Successfully..."
            })
        })
    context = {
        'enquiry':enquiry
    }
    return render(request,'crm/Leads/assign_to_op_modal.html',context)
        # messages.success(request, "Lead Assigned Successfully...")
        
        
        # redirect_to = request.POST.get("redirect_to")
        # redirect_url = redirect_to
        
        # return redirect(redirect_url)



# def personal_info(request,id):
#     enquiry = Enquiry.objects.get(id=id)
#     context = {
#         'enquiry':enquiry
#     }
#     # crm/Leads/add_lead1.html
#     return render(request,'crm/Leads/enquiry/edit_personalinfo.html',context)


from datetime import datetime

def personal_info(request,id):
    # enquiry = Enquiry.objects.get(id=id)
    # context = {
    #     'enquiry':enquiry
    # }
    enquiry = Enquiry.objects.get(id=id)
    country = VisaCountry.objects.all()
    category = VisaCategory.objects.all()
    # notifications = Notification.objects.filter(lead_id=enquiry.id)
    # for notification in notifications:
    #     if not notification.is_seen:
    #         notification.is_seen = True
    #         notification.save()

    context = {
        "enquiry": enquiry,
        "country": country,
        "category": category,
    }

    if request.method == "POST":
        print("oooggggggggggggggggg")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        dob = request.POST.get("dob")
        print("gggggggggg",firstname)
        
        try:
            dob_obj = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            dob_obj = None

        gender = request.POST.get("gender")
        maritialstatus = request.POST.get("maritialstatus")
        digitalsignature = request.FILES.get("digitalsignature")
        spouse_name = request.POST.get("spouse_name")
        spouse_no = request.POST.get("spouse_no")
        spouse_email = request.POST.get("spouse_email")
        spouse_passport = request.POST.get("spouse_passport")
        spouse_dob = request.POST.get("spouse_dob")
        spouse_relation = request.POST.get("spouse_relation")

        spouse_name1 = request.POST.get("spouse_name1")
        spouse_no1 = request.POST.get("spouse_no1")
        spouse_email1 = request.POST.get("spouse_email1")
        spouse_passport1 = request.POST.get("spouse_passport1")
        spouse_dob1 = request.POST.get("spouse_dob1")
        spouse_relation1 = request.POST.get("spouse_relation1")

        spouse_name2 = request.POST.get("spouse_name2")
        spouse_no2 = request.POST.get("spouse_no2")
        spouse_email2 = request.POST.get("spouse_email2")
        spouse_passport2 = request.POST.get("spouse_passport2")
        spouse_dob2 = request.POST.get("spouse_dob2")
        spouse_relation2 = request.POST.get("spouse_relation2")

        spouse_name3 = request.POST.get("spouse_name3")
        spouse_no3 = request.POST.get("spouse_no3")
        spouse_email3 = request.POST.get("spouse_email3")
        spouse_passport3 = request.POST.get("spouse_passport3")
        spouse_dob3 = request.POST.get("spouse_dob3")
        spouse_relation3 = request.POST.get("spouse_relation3")

        spouse_name4 = request.POST.get("spouse_name4")
        spouse_no4 = request.POST.get("spouse_no4")
        spouse_email4 = request.POST.get("spouse_email4")
        spouse_passport4 = request.POST.get("spouse_passport4")
        spouse_dob4 = request.POST.get("spouse_dob4")
        spouse_relation4 = request.POST.get("spouse_relation4")

        spouse_name5 = request.POST.get("spouse_name5")
        spouse_no5 = request.POST.get("spouse_no5")
        spouse_email5 = request.POST.get("spouse_email5")
        spouse_passport5 = request.POST.get("spouse_passport5")
        spouse_dob5 = request.POST.get("spouse_dob5")
        spouse_relation5 = request.POST.get("spouse_relation5")
        refusal = request.POST.get("refusal")
        if refusal == "on":
            refusal = "True"
        else :
            refusal = "False"
        refusal_country = request.POST.get("refusal_country")

        try:
            spouse_dob_obj = datetime.strptime(spouse_dob, "%Y-%m-%d").date()
        except ValueError:
            spouse_dob_obj = None

        try:
            spouse_dob_obj1 = datetime.strptime(spouse_dob1, "%Y-%m-%d").date()
        except ValueError:
            spouse_dob_obj1 = None

        try:
            spouse_dob_obj2 = datetime.strptime(spouse_dob2, "%Y-%m-%d").date()
        except ValueError:
            spouse_dob_obj2 = None

        try:
            spouse_dob_obj3 = datetime.strptime(spouse_dob3, "%Y-%m-%d").date()
        except ValueError:
            spouse_dob_obj3 = None

        try:
            spouse_dob_obj4 = datetime.strptime(spouse_dob4, "%Y-%m-%d").date()
        except ValueError:
            spouse_dob_obj4 = None

        try:
            spouse_dob_obj5 = datetime.strptime(spouse_dob5, "%Y-%m-%d").date()
        except ValueError:
            spouse_dob_obj5 = None

        email = request.POST.get("email").lower()
        contact = request.POST.get("contact")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        Country = request.POST.get("Country")

        emergencyname = request.POST.get("emergencyname")
        emergencyphone = request.POST.get("emergencyphone")
        emergencyemail = request.POST.get("emergencyemail")
        applicantrelation = request.POST.get("applicantrelation")

        passportnumber = request.POST.get("passportnumber")
        issuedate = request.POST.get("issuedate")
        try:
            issuedate_obj = datetime.strptime(issuedate, "%Y-%m-%d").date()
        except ValueError:
            issuedate_obj = None

        expirydate = request.POST.get("expirydate")
        try:
            expirydate_obj = datetime.strptime(expirydate, "%Y-%m-%d").date()
        except ValueError:
            expirydate_obj = None

        issue_country = request.POST.get("issuecountry")
        birthcity = request.POST.get("birthcity")
        country_of_birth = request.POST.get("country_of_birth")

        nationality = request.POST.get("nationality")
        citizenship = request.POST.get("citizenships")
        more_than_one_country = request.POST.get("more_than_one_country")
        studyin_in_other_country = request.POST.get("studyin_in_other_country")

        citizenstatus = request.POST.get("citizenstatus")
        studystatus = request.POST.get("studystatus")

        citizen = request.POST.get("citizen")

        enquiry.FirstName = firstname
        enquiry.LastName = lastname
        enquiry.Dob = dob_obj
        enquiry.Gender = gender
        enquiry.marital_status = maritialstatus
        if digitalsignature:
            enquiry.digital_signature = digitalsignature
        enquiry.spouse_name = spouse_name
        enquiry.spouse_no = spouse_no
        enquiry.spouse_email = spouse_email
        enquiry.spouse_passport = spouse_passport
        enquiry.spouse_dob = spouse_dob_obj
        enquiry.spouse_relation = spouse_relation
        enquiry.spouse_name1 = spouse_name1
        enquiry.spouse_no1 = spouse_no1
        enquiry.spouse_email1 = spouse_email1
        enquiry.spouse_passport1 = spouse_passport1
        enquiry.spouse_dob1 = spouse_dob_obj1
        enquiry.spouse_relation1 = spouse_relation1

        enquiry.spouse_name2 = spouse_name2
        enquiry.spouse_no2 = spouse_no2
        enquiry.spouse_email2 = spouse_email2
        enquiry.spouse_passport2 = spouse_passport2
        enquiry.spouse_dob2 = spouse_dob_obj2
        enquiry.spouse_relation2 = spouse_relation2

        enquiry.spouse_name3 = spouse_name3
        enquiry.spouse_no3 = spouse_no3
        enquiry.spouse_email3 = spouse_email3
        enquiry.spouse_passport3 = spouse_passport3
        enquiry.spouse_dob3 = spouse_dob_obj3
        enquiry.spouse_relation3 = spouse_relation3

        enquiry.spouse_name4 = spouse_name4
        enquiry.spouse_no4 = spouse_no4
        enquiry.spouse_email4 = spouse_email4
        enquiry.spouse_passport4 = spouse_passport4
        enquiry.spouse_dob4 = spouse_dob_obj4
        enquiry.spouse_relation4 = spouse_relation4

        enquiry.spouse_name5 = spouse_name5
        enquiry.spouse_no5 = spouse_no5
        enquiry.spouse_email5 = spouse_email5
        enquiry.spouse_passport5 = spouse_passport5
        enquiry.spouse_dob5 = spouse_dob_obj5
        enquiry.spouse_relation5 = spouse_relation5
        enquiry.email = email
        enquiry.contact = contact
        enquiry.Country = Country
        enquiry.state = state
        enquiry.city = city
        enquiry.address = address

        enquiry.passport_no = passportnumber
        enquiry.issue_date = issuedate_obj
        enquiry.expirty_Date = expirydate_obj
        enquiry.issue_country = issue_country
        enquiry.city_of_birth = birthcity
        enquiry.country_of_birth = country_of_birth
        enquiry.nationality = nationality
        enquiry.citizenship = citizenship
        enquiry.more_than_one_country = more_than_one_country
        enquiry.studyin_in_other_country = studyin_in_other_country
        enquiry.emergency_name = emergencyname
        enquiry.emergency_phone = emergencyphone
        if emergencyemail != "None":
            enquiry.emergency_email = emergencyemail
        enquiry.relation_With_applicant = applicantrelation
        enquiry.refusal = refusal
        enquiry.refusal_country = refusal_country
        enquiry.save()
        

    return render(request,'crm/Leads/enquiry/edit_personalinfo.html',context)
def other_details(request,id):
    # enquiry = Enquiry.objects.get(id=id)
    # context = {
    #     'enquiry':enquiry
    # }
    enquiry = get_object_or_404(Enquiry, id=id)
    education_summary = Education_Summary.objects.filter(enquiry_id=enquiry).first
    work_exp = Work_Experience.objects.filter(enquiry_id=enquiry).first
    bk_info = Background_Information.objects.filter(enquiry_id=enquiry).first

    if request.method == "POST":
        print("workinggg")
        # Education Summary
        education_summary, created = Education_Summary.objects.get_or_create(
            enquiry_id=enquiry
        )
        education_summary.highest_level_education = request.POST.get(
            "highest_education"
        )
        education_summary.grading_scheme = request.POST.get("gradingscheme")
        education_summary.grade_avg = request.POST.get("gradeaverage")
        education_summary.recent_college = request.POST.get("recent_college")
        education_summary.country_of_education = request.POST.get("educationcountry")
        education_summary.country_of_institution = request.POST.get("institutecountry")
        education_summary.name_of_institution = request.POST.get("institutename")
        education_summary.primary_language = request.POST.get("instructionlanguage")
        education_summary.institution_from = request.POST.get("institutionfrom")
        try:
            education_summary.institution_from_obj = datetime.strptime(
                education_summary.institution_from, "%Y-%m-%d"
            ).date()
        except ValueError:
            education_summary.institution_from = None
        education_summary.institution_to = request.POST.get("institutionto")
        try:
            education_summary.institution_to_obj = datetime.strptime(
                education_summary.institution_to, "%Y-%m-%d"
            ).date()
        except ValueError:
            education_summary.institution_to = None
        education_summary.degree_Awarded = request.POST.get("degreeawarded")
        education_summary.degree_Awarded_On = request.POST.get("degreeawardedon")
        education_summary.save()

        # Test Score
        examtype = request.POST.get("examtype")
        exam_date = request.POST.get("examdate")

        try:
            exam_date = datetime.strptime(exam_date, "%Y-%m-%d").date()
        except ValueError:
            exam_date = None
        reading = request.POST.get("reading")
        listening = request.POST.get("listening")
        speaking = request.POST.get("speaking")
        writing = request.POST.get("writing")
        overall_score = request.POST.get("overallscore")

        existing_test_score = TestScore.objects.filter(
            exam_type=examtype, enquiry_id=enquiry
        ).first()
        if reading or exam_date or listening or speaking or writing or overall_score:
            if existing_test_score is None:
                test_scores = TestScore.objects.create(
                    enquiry_id=enquiry,
                    exam_type=examtype,
                    exam_date=exam_date,
                    reading=reading,
                    listening=listening,
                    speaking=speaking,
                    writing=writing,
                    overall_score=overall_score,
                )

            else:
                existing_test_score.exam_date = exam_date
                existing_test_score.reading = reading
                existing_test_score.listening = listening
                existing_test_score.speaking = speaking
                existing_test_score.writing = writing
                existing_test_score.overall_score = overall_score
                existing_test_score.save()

        # Handle Background Information
        background_info, created = Background_Information.objects.get_or_create(
            enquiry_id=enquiry
        )
        background_info.background_information = request.POST.get("australliabefore")
        background_info.save()

        # Handle Work Experience
        work_exp, created = Work_Experience.objects.get_or_create(enquiry_id=enquiry)
        work_exp.company_name = request.POST.get("companyname")
        work_exp.designation = request.POST.get("designation")
        work_exp.from_date = request.POST.get("fromdate")
        try:
            work_exp.from_date_obj = datetime.strptime(
                work_exp.from_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            work_exp.from_date = None
        work_exp.to_date = request.POST.get("todate")
        try:
            work_exp.to_date_obj = datetime.strptime(
                work_exp.to_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            work_exp.to_date = None
        work_exp.address = request.POST.get("address")
        work_exp.city = request.POST.get("city")
        work_exp.state = request.POST.get("state")
        work_exp.describe = request.POST.get("workdetails")
        work_exp.save()

        return redirect("other_details", id=id)

    test_scores = TestScore.objects.filter(enquiry_id=enquiry)

    context = {
        "enquiry": enquiry,
        "test_scores": test_scores,
        "education_summary": education_summary,
        "work_exp": work_exp,
        "bk_info": bk_info,
    }

    return render(request,'crm/Leads/enquiry/other_details.html',context)




@login_required
def delete_test_score(request, id):
    print("okkkkk")
    test_score = get_object_or_404(TestScore, id=id)
    # test_score = TestScore.objects.get(id=id)
    enquiry_id = test_score.enquiry_id.id
    test_score.delete()
    
    return redirect("other_details", id=enquiry_id)




@login_required
def editproduct_details(request, id):
    enquiry = Enquiry.objects.get(id=id)
    country = VisaCountry.objects.all()
    category = VisaCategory.objects.all()
    product = Package.objects.all()
    context = {
        "enquiry": enquiry,
        "country": country,
        "category": category,
        "product": product,
    }

    if request.method == "POST":
        source = request.POST.get("source")
        reference = request.POST.get("reference")
        visatype = request.POST.get("visatype")
        visacountry_id = request.POST.get("visacountry_id")
        visacategory_id = request.POST.get("visacategory_id")
        visasubcategory_id = request.POST.get("visasubcategory")
        product_id = request.POST.get("Package")

        visa_country = VisaCountry.objects.get(id=visacountry_id)
        visa_category = VisaCategory.objects.get(id=visacategory_id)
        visa_subcategory = VisaCategory.objects.get(id=visacategory_id)
        package = Package.objects.get(id=product_id)

        enquiry.Source = source
        enquiry.Reference = reference
        enquiry.Visa_type = visatype
        enquiry.Visa_country = visa_country
        enquiry.Visa_category = visa_category
        enquiry.Visa_subcategory = visa_subcategory
        enquiry.Package = package

        enquiry.save()

        return redirect("edit_product_details", id=id)

    return render(request,"crm/Leads/enquiry/product_selection.html",context,)




def enq_documents(request, id):
    # Fetch the Enquiry object or return a 404 error
    enq = get_object_or_404(Enquiry, id=id)

    # Fetch DocumentFiles associated with the enquiry
    doc_file = DocumentFiles.objects.filter(enquiry_id=enq)

    # Prefetch related documents for case categories
    case_categories = CaseCategoryDocument.objects.filter(country=enq.Visa_country).prefetch_related(
        Prefetch(
            "document",
            queryset=Document.objects.select_related("document_category", "lastupdated_by"),
        )
    )

    # Group documents by their category
    grouped_documents = {}
    for case_category in case_categories:
        for document in case_category.document.all():
            document_category = document.document_category
            if document_category not in grouped_documents:
                grouped_documents[document_category] = []
            grouped_documents[document_category].append(document)

    # Context for the template
    expected_path = f"/enquiry/{enq.id}/"
    context = {
        "enq": enq,
        "expected_path":expected_path,
        "is_document" : True
        # "grouped_documents": grouped_documents,
        # "doc_file": doc_file,
    }

    return render(request, 'crm/Leads/enquiry/documents_details.html', context)



@login_required
def delete_and_archive(request, id):
    instance = get_object_or_404(Enquiry, id=id)

    instance.archive = True
    instance.save()
    return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"Lead Deleted !!"

                    })
                })
    # return redirect("admin_new_leads_details")


@login_required
def restore(request, id):
    instance = get_object_or_404(Enquiry, id=id)

    instance.archive = False
    instance.save()
    return HttpResponse(status=204, headers={
                'HX-Trigger': json.dumps({
                    "movieListChanged":None,
                    "showMessage":f"Lead Restore !!"

                    })
                })

    # return redirect("Archive_list")
