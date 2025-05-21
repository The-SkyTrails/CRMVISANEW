import django_filters
from .models import Agent,OutSourcingAgent,Enquiry,SubAgnt
from django import forms

class AgentFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='registeron__date',lookup_expr='gte',label='Date',widget=forms.DateInput(attrs={'type':'date'}))
    end_date = django_filters.DateFilter(field_name='registeron__date',lookup_expr='lte',label='Date To',widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Agent
        fields = ('start_date','end_date')

class OutSourceAgentFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='registeron__date',lookup_expr='gte',label='Date',widget=forms.DateInput(attrs={'type':'date'}))
    end_date = django_filters.DateFilter(field_name='registeron__date',lookup_expr='lte',label='Date To',widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = OutSourcingAgent
        fields = ('start_date','end_date')





class EnquiryFilter(django_filters.FilterSet):
    class Meta:
        model = Enquiry
        fields = ['enquiry_number']



class SubAgentFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='created_on', lookup_expr='gte',
        label='From Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = django_filters.DateFilter(
        field_name='created_on', lookup_expr='lte',
        label='To Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = SubAgnt
        fields = []  # yahan aap kisi field par filter chahte ho to unka naam de sakte ho

