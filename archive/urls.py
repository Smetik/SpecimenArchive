from django.urls import path

from .views import (
    IncidentCreateView,
    IncidentDeleteView,
    IncidentDetailView,
    IncidentListView,
    IncidentUpdateView,
    ResolutionLogDetailView,
    SpecimenCreateView,
    SpecimenDeleteView,
    SpecimenDetailView,
    SpecimenListView,
    SpecimenUpdateView,
    execute_protocol_session,
    home,
    incident_filter,
    specimen_filter,
)

urlpatterns = [
    path('', home, name='home'),
    path('specimens/', SpecimenListView.as_view(), name='specimen_list'),
    path('specimens/filter/', specimen_filter, name='specimen_filter'),
    path('specimens/create/', SpecimenCreateView.as_view(), name='specimen_create'),
    path('specimens/<int:pk>/', SpecimenDetailView.as_view(), name='specimen_detail'),
    path('specimens/<int:pk>/edit/', SpecimenUpdateView.as_view(), name='specimen_update'),
    path('specimens/<int:pk>/delete/', SpecimenDeleteView.as_view(), name='specimen_delete'),
    path('protocol/execute/', execute_protocol_session, name='execute_protocol_session'),
    path('sessions/<int:pk>/', ResolutionLogDetailView.as_view(), name='resolution_log_detail'),
    path('incidents/', IncidentListView.as_view(), name='incident_list'),
    path('incidents/filter/', incident_filter, name='incident_filter'),
    path('incidents/create/', IncidentCreateView.as_view(), name='incident_create'),
    path('incidents/<int:pk>/', IncidentDetailView.as_view(), name='incident_detail'),
    path('incidents/<int:pk>/edit/', IncidentUpdateView.as_view(), name='incident_update'),
    path('incidents/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident_delete'),
]
