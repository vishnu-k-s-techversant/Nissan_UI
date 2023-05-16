from django.urls import path
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from .views import ApprovalView, ApprovedAPIView, ForwarderAPIView, ForwarderMailConfigAddView, ForwarderMailConfigEditView, ForwarderMailConfigView, LocationInsertAPIView, MasterInsertAPIView, UpdateApproval, NissanMasterDetailView, DataInsightView, LotLocationView, ForwarderView, \
    CodeGeneratorView, CodeGeneratorEditView, DashboardView, CreateCodeView
app_name = 'user-data'

urlpatterns = [
    path('dashboard/', login_required(DashboardView.as_view()),
         name='dashboard'),

    path('requests/', login_required(ApprovalView.as_view()),
         name='request'),
    path('approve/<int:lot>/<str:action>/', login_required(UpdateApproval.as_view()),
         name='approve'),
    path('city-details/<str:city>/<int:lot>/<str:state>/', login_required(NissanMasterDetailView.as_view()),
         name='masterdetail'),
    path('master/', login_required(DataInsightView.as_view()),
         name='master'),
    path('forwarder/', login_required(ForwarderView.as_view()),
         name='forwarder'),
    path('lot-location/', login_required(LotLocationView.as_view()),
         name='lotlocation'),
    path('code-gen/', login_required(CodeGeneratorView.as_view()),
         name='codegen'),
    path('code-gen-edit/<int:pk>/', login_required(CodeGeneratorEditView.as_view()),
         name='codegenedit'),
    path('mail-config/', login_required(ForwarderMailConfigView.as_view()),
         name='mailconfig'),
    path('mail-config-edit/<int:pk>/<str:forwarder>/', login_required(ForwarderMailConfigEditView.as_view()),
         name='mailconfigedit'),
    path('mail-config-add/', login_required(ForwarderMailConfigAddView.as_view()),
         name='mailconfigadd'),
    path('forwarder-dt/', login_required(ForwarderAPIView.as_view()),
         name='forwarder-dt'),
    path('approved-dt/', login_required(ApprovedAPIView.as_view()),
         name='approved-dt'),
    path('master-insert-dt/', login_required(MasterInsertAPIView.as_view()),
         name='master-insert-dt'),
    path('location-dt/', login_required(LocationInsertAPIView.as_view()),
         name='location-dt'),
    path('create/', login_required(CreateCodeView.as_view()),
         name='createcode'),
]
