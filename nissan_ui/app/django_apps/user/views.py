
from django.utils import timezone
import re
# Create your views here.
# some_app/views.py
import pandas as pd
import datetime
from django.db.models.functions import Trim
from rest_framework.response import Response
from rest_framework import permissions
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView, TemplateView, CreateView
from django.views import View
from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from .models import ForwarderCodeGenerator, ForwarderMailConfig, LotLocation, NissanMaster, Forwardercompany, ForwarderCodePattern, AuctionRecord, NamingfwdPattern, BaseSetting
from .forms import ForwaderForm, MailConfigEditForm, MailConfigForm, CreateCodeForm
from rest_framework.views import APIView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Trim
from .utils import addresskey_function, agentkey_function


from django.shortcuts import redirect


class ForwarderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):

        data = Forwardercompany.objects.select_related('forwarder_created_by_pattern', 'forwardercodegenerator').values_list('forwarder_short_code', 'forwarder_long_name', 'forwardercodegenerator__code_prefix',
                                                                                                                             'forwardercodegenerator__code', 'forwardercodegenerator__code_suffix', 'forwardercodegenerator__max_code_value', 'forwarder_created_by_pattern__pattern_of_code')
        records = {
            "data": data
        }
        return Response(records)


class ApprovedAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        now = timezone.now().date()

        data = NissanMaster.objects.filter(
            Q(review=2) & Q(deleted_at__isnull=True) & Q(review_date__date=now)).values_list('code', 'name', 'address', 'city', 'state', 'zip', 'forwarder', 'agentkey', 'addresskey', 'agent', 'address_1', 'fwd_agent', 'fwd_address')

        records = {
            "data": data
        }
        return Response(records)


class MasterInsertAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        now = timezone.now().date()

        data = NissanMaster.objects.filter(
            Q(review=0) & Q(deleted_at__isnull=True) & Q(created_at__date=now)).values_list('code', 'name', 'address', 'city', 'state', 'zip', 'forwarder', 'agentkey', 'addresskey', 'agent', 'address_1', 'fwd_agent', 'fwd_address')

        records = {
            "data": data
        }
        return Response(records)


class LocationInsertAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        now = timezone.now().date()

        data = LotLocation.objects.filter(
            Q(deleted_at__isnull=True) & Q(created_at__date=now)).values_list('repo_agent_id', 'repo_name', 'repo_st_addr1', 'repo_city_name', 'repo_state_cd', 'repo_zip_cd', 'fwd')

        records = {
            "data": data
        }
        return Response(records)


class DataInsightView(TemplateView):

    model = NissanMaster
    template_name = 'user_master.html'


class ForwarderView(ListView):

    template_name = 'forwarders.html'

    queryset = Forwardercompany.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forwarders_records'] = Forwardercompany.objects.all().values(
            'id', 'forwarder_short_code')
        context['forwarderform'] = ForwaderForm
        return context

    def post(self, request, *args, **kwargs):

        fwd_obj = Forwardercompany.objects.get(
            id=int(request.POST.get('forwarder_name')))
        if fwd_obj:
            obj_pattern = ForwarderCodePattern.objects.filter(
                forwarder_id=fwd_obj)
            obj_gen = ForwarderCodeGenerator.objects.filter(
                forwarder_id=fwd_obj)
            if not obj_pattern and not obj_gen:
                ForwarderCodePattern.objects.get_or_create(
                    pattern_of_code=str(request.POST.get(
                        "code_regex_pattern")).upper(),
                    created_by=request.user,
                    updated_by=request.user,
                    forwarder_id=fwd_obj
                )

                ForwarderCodeGenerator.objects.get_or_create(
                    code_prefix=str(request.POST.get("siebel_prefix")).upper(),
                    code=request.POST.get("code"),
                    code_suffix=str(request.POST.get("siebel_suffix")).upper(),
                    max_code_value=request.POST.get("max_code"),
                    forwarder_id=fwd_obj,
                    created_by=request.user,
                    updated_by=request.user

                )
                messages.success(
                    request, 'Forwarder details updated successfully')
            else:
                messages.error(
                    request, 'not updated, Forwarder details already exist')

            return HttpResponseRedirect(reverse('user-data:forwarder'))
        else:

            return HttpResponseRedirect(reverse('user-data:forwarder'))


class LotLocationView(ListView):

    model = LotLocation
    template_name = 'lot-location.html'
    # now = timezone.now().date()

    queryset = LotLocation.objects.filter(
        Q(deleted_at__isnull=True))


class ForwarderMailConfigView(ListView):

    model = ForwarderMailConfig
    template_name = 'forwarder-config.html'


class ForwarderMailConfigAddView(SuccessMessageMixin, CreateView):
    
    model = ForwarderMailConfig
    form_class = MailConfigForm
    template_name = 'forwarder-config-add.html'
    success_message = 'Mail config added successfully!'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('user-data:mailconfig')


class ForwarderMailConfigEditView(SuccessMessageMixin, UpdateView):

    model = ForwarderMailConfig
    form_class = MailConfigEditForm
    template_name = 'forwarder-config-edit.html'
    success_message = 'Mail config updated successfully!'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('user-data:mailconfig')


class CodeGeneratorView(ListView):

    model = ForwarderCodeGenerator
    template_name = 'code-generator.html'


class CodeGeneratorEditView(SuccessMessageMixin, UpdateView):

    model = ForwarderCodeGenerator
    template_name = 'code-generator-edit.html'
    fields = ['max_code_value']
    success_message = 'Max code updated successfully!'

    def get_success_url(self):
        return reverse('user-data:codegen')


class DashboardView(TemplateView):

    template_name = 'user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_master_count'] = NissanMaster.objects.filter(
            Q(review__in=[0, 2]) & Q(deleted_at__isnull=True)).count()
        context['table_lot_count'] = LotLocation.objects.filter(
            deleted_at__isnull=True).count()
        return context


class ApprovalView(ListView):

    model = NissanMaster
    template_name = "user_approval_queue.html"
    queryset = NissanMaster.objects.filter(
        Q(review=1) & Q(deleted_at__isnull=True))


class UpdateApproval(View):

    def get(self, request, *args, **kwargs):
        action = kwargs.get('action')
        lot_id = kwargs.get('lot')
        object = NissanMaster.objects.get(id=lot_id)

        if action == '0':

            object.review = 2
            object.review_date = datetime.datetime.utcnow().isoformat()
            object.save()
            return HttpResponseRedirect(reverse('user-data:request'))
        elif action == '1':
            object.review = 3
            object.review_date = datetime.datetime.utcnow().isoformat()
            object.save()
            return HttpResponseRedirect(reverse('user-data:request'))


class NissanMasterDetailView(ListView):

    model = NissanMaster
    template_name = 'nissanmaster_list.html'
    queryset = NissanMaster.objects.filter(
        Q(review__in=[0, 2]) & Q(deleted_at__isnull=True))

    def group_records(self, records):
        pass

    def get_context_data(self, **kwargs):
        context = super(NissanMasterDetailView,
                        self).get_context_data(**kwargs)
        queryset = NissanMaster.objects.filter(
            Q(review__in=[0, 2]) & Q(deleted_at__isnull=True))
        review_item = NissanMaster.objects.get(
            id=int(self.kwargs['lot']))
        context['review_item'] = review_item

        city_filtered = queryset.filter(
            city__icontains=self.kwargs['city']).order_by('address')

        if city_filtered:
            context['hide_code'] = 1

            city_records = pd.DataFrame(city_filtered.values(
                'code', 'name', 'address', 'city', 'state', 'zip', 'forwarder', 'address_1', 'id'))
            city_records = city_records.astype(str)
            city_records[city_records.columns] = city_records.apply(
                lambda x: x.str.strip())

            city_records = city_records.groupby(
                ['address', 'city', 'state', 'zip', 'forwarder']).max().reset_index()

            city_records = city_records.sort_values(
                by=['address'], ascending=True)

            context['city_details'] = city_records.to_dict('records')

            try:
                city_input = str(self.kwargs['city']).strip()
                if " " in city_input:
                    city_input = city_input.split(" ")[0]
                auction = LotLocation.objects.filter(
                    Q(deleted_at__isnull=True) & Q(repo_city_name__icontains=city_input) & Q(repo_state_cd=str(self.kwargs['state']).strip())).order_by('-id').first()
                complete_auction = [
                    {
                        "id": auction.id,
                        "auct_id": f"{auction.auct_id}-{auction.auct_name}"
                    }
                ]
                context['default_auction'] = complete_auction
            except (IndexError, AttributeError) as e:
                print(e)
                auction = AuctionRecord.objects.filter(
                    deleted_at__isnull=True).values_list('id', 'auct_id', 'auct_name')
                complete_auction = [
                    {
                        "id": i[0],
                        "auct_id": f"{i[1]}-{i[2]}"
                    }for i in auction
                ]
                context['default_auction'] = complete_auction

        else:
            context['hide_code'] = 0
            auction = AuctionRecord.objects.filter(
                deleted_at__isnull=True).values_list('id', 'auct_id', 'auct_name')
            complete_auction = [
                {
                    "id": i[0],
                    "auct_id": f"{i[1]}-{i[2]}"
                }for i in auction
            ]
            context['default_auction'] = complete_auction
        return context

    def create_lot_location(self, request, object, auction_record=None):

        nm_ptn = NamingfwdPattern.objects.filter(
            Q(deleted_at__isnull=True) & Q(mbsi_code=object.forwarder))
        # print(object.forwarder, nm_ptn, object.code)
        regex_pattern = nm_ptn[0].nmac_regex
        code_val = re.search(regex_pattern, object.code_trimmed).group(1)

        if auction_record:
            location_dict = dict(repo_agent_id=code_val,
                                 repo_name=object.name,
                                 repo_st_addr1=object.address,
                                 repo_city_name=object.city,
                                 repo_state_cd=object.state,
                                 repo_zip_cd=object.zip,
                                 fwd=object.forwarder,
                                 auct_id=auction_record.auct_id,
                                 nmac_auct_id=auction_record.nmac_auct_id,
                                 auct_name=auction_record.auct_name,
                                 auct_st_addr_text=auction_record.auct_st_addr_text,
                                 auct_city_name=auction_record.auct_city_name,
                                 auct_state_cd=auction_record.auct_state_cd,
                                 auct_zip_cd=auction_record.auct_zip_cd,
                                 auct_phon_num=auction_record.auct_phon_num,
                                 created_by=request.user.username,
                                 updated_by=request.user.username)

            LotLocation.objects.get_or_create(defaults=location_dict,
                                              repo_name=object.name,
                                              repo_st_addr1=object.address,
                                              repo_city_name=object.city,
                                              repo_state_cd=object.state,
                                              repo_zip_cd=object.zip,
                                              fwd=object.forwarder,
                                              deleted_at=None
                                              )
        else:
            location_dict = dict(repo_agent_id=int(code_val),
                                 repo_name=object.name,
                                 repo_st_addr1=object.address,
                                 repo_city_name=object.city,
                                 repo_state_cd=object.state,
                                 repo_zip_cd=object.zip,
                                 fwd=object.forwarder,
                                 created_by=request.user.username,
                                 updated_by=request.user.username)
            LotLocation.objects.get_or_create(defaults=location_dict,
                                              repo_name=object.name,
                                              repo_st_addr1=object.address,
                                              repo_city_name=object.city,
                                              repo_state_cd=object.state,
                                              repo_zip_cd=object.zip,
                                              fwd=object.forwarder,
                                              deleted_at=None
                                              )
        return

    def post(self, request, *args, **kwargs):
        condition_selected = None
        record_to_review = request.POST['lotId']
        record_reviewed = request.POST['reviewed']

        code_trimmed = NissanMaster.objects.annotate(
            code_trimmed=Trim('code'))

        original_record = code_trimmed.filter(
            id=int(record_reviewed)).first()
        object = code_trimmed.filter(id=int(record_to_review)).first()
        if int(record_to_review) == int(record_reviewed):
            condition_selected = '1'
        elif str(object.forwarder).lower().strip() == str(original_record.forwarder).lower().strip():
            condition_selected = '2'
        elif str(object.forwarder).lower().strip() != str(original_record.forwarder).lower().strip():
            condition_selected = '3'

        if condition_selected == '1':
            # Keep new location code; create address key - both tables get records
            auction_detail = request.POST['auction-detail']
            try:
                auction_record = LotLocation.objects.get(
                    id=int(auction_detail))
            except LotLocation.DoesNotExist:
                auction_record = AuctionRecord.objects.get(
                    id=int(auction_detail))

            object.review = 2
            object.review_date = timezone.now()
            object.reviewed_by = request.user.username
            object.updated_by = request.user.username
            object.condition_selected = '1-NEW - never seen before based on address'
            self.create_lot_location(
                request, object, auction_record=auction_record)
            object.save()

            messages.success(
                request, 'Success')

        elif condition_selected == '2':
            #     # Replace location code, add new address for same address key to Master table only
            object.code = original_record.code_trimmed
            # object.agentkey = original_record.agentkey
            # object.addresskey = original_record.addresskey # not updating agentkey & addresskey since that will be unique to the new address
            object.agent = original_record.agent
            object.address_1 = original_record.address_1
            object.fwd_agent = original_record.fwd_agent
            object.fwd_address = original_record.fwd_address
            object.review = 2
            object.matching_master_record = record_reviewed
            object.review_date = timezone.now()
            object.reviewed_by = request.user.username
            object.updated_by = request.user.username
            object.condition_selected = '2-Matches an address (kind of) for the forwarder'
            object.save()
            messages.success(
                request, 'Success')
        elif condition_selected == '3':
            # Keep new location code; clone address key - both tables get records
            object.code = object.code_trimmed
            object.agentkey = original_record.agentkey
            object.addresskey = original_record.addresskey
            object.agent = original_record.agent
            object.address_1 = original_record.address_1
            object.fwd_agent = f"{object.forwarder}{object.agent}"
            object.fwd_address = f"{object.forwarder}{object.address_1}"
            object.review = 2
            object.matching_master_record = record_reviewed
            object.condition_selected = '3-Matches an address (kind of) but not for this forwarder'
            object.review_date = timezone.now()
            object.reviewed_by = request.user.username
            object.updated_by = request.user.username

            city_input = str(self.kwargs['city']).strip()
            if " " in city_input:
                city_input = city_input.split(" ")[0]

            auction = LotLocation.objects.filter(
                Q(deleted_at__isnull=True) & Q(repo_city_name__icontains=city_input) & Q(repo_state_cd=str(self.kwargs['state']).strip())).order_by('-id').first()

            # create record on lot location
            self.create_lot_location(request, object, auction_record=auction)

            object.save()

            messages.success(
                request, 'Success')

        else:
            messages.warning(
                request, 'No matching found')
        return HttpResponseRedirect(reverse('user-data:request'))


class CreateCodeView(CreateView):
        
    form_class = CreateCodeForm
    template_name = 'create_code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forwarders'] = Forwardercompany.objects.all()
        return context

    def form_valid(self, form):
        name = self.request.POST.get("name")
        address = self.request.POST.get("address")
        city = self.request.POST.get("city")
        state = self.request.POST.get("state")
        zip = self.request.POST.get("zip")

        forwarder = Forwardercompany.objects.get(
                    id=int(self.request.POST.get('forwarder_name')))
            
        agentkey = agentkey_function(name, address, city, state)
        addresskey = addresskey_function(address, zip)

        address_code = BaseSetting.objects.get(setting_name='address_code')
        agent_code = BaseSetting.objects.get(setting_name='agent_code')

        NissanMaster.objects.get_or_create(
            code=self.request.POST.get("code").upper(),
            name=name.upper(),
            address=address.upper(),
            city=city.upper(),
            state=state.upper(),
            zip=zip,
            forwarder=forwarder,
            agentkey=agentkey.upper(),
            addresskey=addresskey.upper(),
            agent=agent_code.setting_value,
            address_1=address_code.setting_value,
            fwd_agent=str(forwarder)+str(agent_code.setting_value).upper(),
            fwd_address=str(forwarder)+str(address_code.setting_value).upper(),
            created_by=self.request.user.username,
            updated_by=self.request.user.username
        )
       
        messages.success(self.request, 'Details added successfully')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('user-data:createcode')
    