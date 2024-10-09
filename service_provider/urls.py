from django.urls import path
from service_provider.views import ComplaintViewSet 


urlpatterns = [
    
    path('complaints/', ComplaintViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='complaint-list'),

    
    path('complaints/<int:id>/', ComplaintViewSet.as_view({
        'get': 'retrieve',
    }), name='complaint-detail'),

    # List Active Complaints
    path('complaints/active/', ComplaintViewSet.as_view({
        'get': 'list_active_complaints'
    }), name='complaint-active-list'),

    # List Completed Complaints
    path('complaints/completed/', ComplaintViewSet.as_view({
        'get': 'list_completed_complaints'
    }), name='complaint-completed-list'),

     # List Rejected Complaints
    path('complaints/rejected/', ComplaintViewSet.as_view({
        'get': 'list_rejected_complaints'
    }), name='complaint-rejected-list'),

]
