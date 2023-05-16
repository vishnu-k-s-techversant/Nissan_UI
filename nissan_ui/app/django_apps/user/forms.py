import re
# import form class from django
from django import forms

from .models import ForwarderCodeGenerator, ForwarderMailConfig, NissanMaster, Forwardercompany, ForwarderCodePattern
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# create a ModelForm


class ForwaderForm(forms.Form):

    siebel_prefix = forms.CharField(label='Siebel Prefix', max_length=100, widget=forms.TextInput(
        attrs={"class": "form-control autocapitalize", "placeholder": "prefix"}))
    code = forms.CharField(label='Code', max_length=100, widget=forms.TextInput(
        attrs={"class": "form-control autocapitalize", "placeholder": "code"}))
    siebel_suffix = forms.CharField(label='Siebel Suffix', max_length=100, widget=forms.TextInput(
        attrs={"class": "form-control autocapitalize", "placeholder": "suffix"}))
    max_code = forms.CharField(label='Max Code', max_length=100, widget=forms.TextInput(
        attrs={"class": "form-control autocapitalize", "placeholder": "max code"}))
    code_regex_pattern = forms.CharField(label='Code Regex Pattern', max_length=100, widget=forms.TextInput(
        attrs={"class": "form-control autocapitalize", "placeholder": "regex pattern"}))


class CodeForm(forms.ModelForm):
    class Meta:
        model = ForwarderCodeGenerator
        fields = ['code_prefix', 'code', 'code_suffix',
                  'max_code_value', 'forwarder_id']


class MailConfigForm(forms.ModelForm):

    class Meta:
        model = ForwarderMailConfig
        fields = ('forwarder', 'forwarder_contact_person',
                  'forwarder_email', 'cc_email', 'is_enabled',)

    def clean_forwarder(self):
        forwarder = self.cleaned_data['forwarder']

        if ForwarderMailConfig.objects.filter(forwarder=self.cleaned_data['forwarder']).exists():
            raise forms.ValidationError(
                'This Forwarder already have emails configured')
        return forwarder

    def clean_forwarder_email(self):
        forwarder_email_original = self.cleaned_data['forwarder_email']
        forwarder_email = forwarder_email_original.split(",")
        if len(forwarder_email) == 1:

            try:
                forwarder_email = forwarder_email[0].lower().strip()
                validate_email(forwarder_email)
            except ValidationError as e:
                raise forms.ValidationError('Enter a valid email address.')
        elif len(forwarder_email) > 1:
            error = list()
            for email in forwarder_email:
                forwarder_email = email.lower().strip()
                try:
                    forwarder_email = forwarder_email.lower().strip()
                    validate_email(forwarder_email)
                except ValidationError as e:
                    error.append(1)

            if len(error) > 0:
                raise forms.ValidationError('Enter a valid email address.')

        return "".join(forwarder_email_original.split()) if forwarder_email_original else forwarder_email_original

    def clean_cc_email(self):
        cc_email_original = self.cleaned_data['cc_email']
        if cc_email_original:
            cc_emails = cc_email_original.split(",")
            if len(cc_emails) == 1:
                cc_email = cc_emails[0].lower().strip()
                if not cc_email.endswith("@mbsicorp.com"):
                    raise forms.ValidationError(
                        'Only MBSiCorp emails allowed in CC')
            elif len(cc_emails) > 1:
                error = list()
                for email in cc_emails:
                    cc_email = email.lower().strip()
                    if not cc_email.endswith("@mbsicorp.com"):
                        error.append(1)
                if len(error) > 0:
                    raise forms.ValidationError(
                        'Only MBSiCorp emails allowed in CC')

        return "".join(cc_email_original.split()) if cc_email_original else cc_email_original

class MailConfigEditForm(forms.ModelForm):
    
    class Meta:
        model = ForwarderMailConfig
        fields = ('forwarder_contact_person',
                  'forwarder_email', 'cc_email', 'is_enabled',)



    def clean_forwarder_email(self):
        forwarder_email_original = self.cleaned_data['forwarder_email']
        forwarder_email = forwarder_email_original.split(",")
        if len(forwarder_email) == 1:

            try:
                forwarder_email = forwarder_email[0].lower().strip()
                validate_email(forwarder_email)
            except ValidationError as e:
                raise forms.ValidationError('Enter a valid email address.')
        elif len(forwarder_email) > 1:
            error = list()
            for email in forwarder_email:
                forwarder_email = email.lower().strip()
                try:
                    forwarder_email = forwarder_email.lower().strip()
                    validate_email(forwarder_email)
                except ValidationError as e:
                    error.append(1)

            if len(error) > 0:
                raise forms.ValidationError('Enter a valid email address.')

        return "".join(forwarder_email_original.split()) if forwarder_email_original else forwarder_email_original

    def clean_cc_email(self):
        cc_email_original = self.cleaned_data['cc_email']
        if cc_email_original:
            cc_emails = cc_email_original.split(",")
            if len(cc_emails) == 1:
                cc_email = cc_emails[0].lower().strip()
                if not cc_email.endswith("@mbsicorp.com"):
                    raise forms.ValidationError(
                        'Only MBSiCorp emails allowed in CC')
            elif len(cc_emails) > 1:
                error = list()
                for email in cc_emails:
                    cc_email = email.lower().strip()
                    if not cc_email.endswith("@mbsicorp.com"):
                        error.append(1)
                if len(error) > 0:
                    raise forms.ValidationError(
                        'Only MBSiCorp emails allowed in CC')

        return "".join(cc_email_original.split()) if cc_email_original else cc_email_original


class CreateCodeForm(forms.ModelForm):

    class Meta:
        model = NissanMaster
        fields = ('code','name', 'address', 
                  'city','state', 'zip',)

    def clean_code(self):
        code = self.cleaned_data.get('code')

        forwarder_code_pattern = ForwarderCodePattern.objects.select_related('forwarder_id').get(
            forwarder_id__id=int(self.data.get('forwarder_name')))
    
        if not re.match(forwarder_code_pattern.pattern_of_code, code):
            raise forms.ValidationError(
                'The given code does not match with selected forwarder')
        return code
