from django.urls import path
from . import views

app_name = 'netbox_scion'

urlpatterns = (
    # Plugin home
    path('', views.PluginHomeView.as_view(), name='home'),
    # AJAX URLs
    path('ajax/isdas-appliances/', views.get_isdas_appliances, name='isdas_appliances_ajax'),
    
    # Organization URLs
    path('organizations/', views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/add/', views.OrganizationEditView.as_view(), name='organization_add'),
    path('organizations/delete/', views.OrganizationBulkDeleteView.as_view(), name='organization_bulk_delete'),
    path('organizations/<int:pk>/', views.OrganizationView.as_view(), name='organization'),
    path('organizations/<int:pk>/edit/', views.OrganizationEditView.as_view(), name='organization_edit'),
    path('organizations/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name='organization_delete'),
    path('organizations/<int:pk>/changelog/', views.OrganizationChangeLogView.as_view(), name='organization_changelog'),

    # ISD-AS URLs
    path('isd-ases/', views.ISDAListView.as_view(), name='isdas_list'),
    path('isd-ases/add/', views.ISDAEditView.as_view(), name='isdas_add'),
    path('isd-ases/delete/', views.ISDABulkDeleteView.as_view(), name='isdas_bulk_delete'),
    path('isd-ases/<int:pk>/', views.ISDAView.as_view(), name='isdas'),
    path('isd-ases/<int:pk>/edit/', views.ISDAEditView.as_view(), name='isdas_edit'),
    path('isd-ases/<int:pk>/delete/', views.ISDADeleteView.as_view(), name='isdas_delete'),
    path('isd-ases/<int:pk>/changelog/', views.ISDAChangeLogView.as_view(), name='isdas_changelog'),
    # Appliance management URLs
    path('isd-ases/<int:pk>/add-appliance/', views.add_appliance_to_isdas, name='add_appliance'),
    path('isd-ases/<int:pk>/edit-appliance/<str:appliance_name>/', views.edit_appliance_in_isdas, name='edit_appliance'),
    path('isd-ases/<int:pk>/remove-appliance/<str:appliance_name>/', views.remove_appliance_from_isdas, name='remove_appliance'),

    # SCION Link Assignment URLs
    path('link-assignments/', views.SCIONLinkAssignmentListView.as_view(), name='scionlinkassignment_list'),
    path('link-assignments/add/', views.SCIONLinkAssignmentEditView.as_view(), name='scionlinkassignment_add'),
    path('link-assignments/delete/', views.SCIONLinkAssignmentBulkDeleteView.as_view(), name='scionlinkassignment_bulk_delete'),
    path('link-assignments/<int:pk>/', views.SCIONLinkAssignmentView.as_view(), name='scionlinkassignment'),
    path('link-assignments/<int:pk>/edit/', views.SCIONLinkAssignmentEditView.as_view(), name='scionlinkassignment_edit'),
    path('link-assignments/<int:pk>/delete/', views.SCIONLinkAssignmentDeleteView.as_view(), name='scionlinkassignment_delete'),
    path('link-assignments/<int:pk>/changelog/', views.SCIONLinkAssignmentChangeLogView.as_view(), name='scionlinkassignment_changelog'),
)
