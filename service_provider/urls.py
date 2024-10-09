from django.urls import path
from service_provider.views import ComplaintViewSet 


urlpatterns = [
     # List and Create Complaints
    path('complaints/', ComplaintViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='complaint-list'),

    # Retrieve, Update, and Delete a Complaint
    path('complaints/<int:id>/', ComplaintViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='complaint-detail'),

    # List Active Complaints
    path('complaints/active/', ComplaintViewSet.as_view({
        'get': 'list_active_complaints'
    }), name='complaint-active-list'),

    # List Completed Complaints
    path('complaints/completed/', ComplaintViewSet.as_view({
        'get': 'list_completed_complaints'
    }), name='complaint-completed-list'),


    path('complaints/rejected/', ComplaintViewSet.as_view({
        'get': 'list_rejected_complaints'
    }), name='complaint-rejected-list'),

]
