from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelBulkEditForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.models import Contract, Contractor, ContractTypeChoices


class ContractForm(NetBoxModelForm):
    comments = CommentField(label="Comments")
    contractor = DynamicModelChoiceField(queryset=Contractor.objects.all(), required=True)
    parent = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        query_params={"parent_id": "null"},
        required=False,
        label=("Parent Contract"),
    )
    signed = forms.DateField(required=False, label=("Signed"), widget=DatePicker())
    accepted = forms.DateField(required=False, label=("Accepted"), widget=DatePicker())
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())

    class Meta:
        model = Contract
        fields = (
            "name",
            "name_internal",
            "contractor",
            "type",
            "price",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            "parent",
            "comments",
            "tags",
        )


class ContractFilterForm(NetBoxModelFilterSetForm):
    model = Contract

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("name", "name_internal", "contract_type", "type", name=_("Common")),
        FieldSet("contractor_id", "parent_id", name=_("Linked")),
        FieldSet(
            "signed",
            "signed__gte",
            "signed__lte",
            "accepted",
            "accepted__gte",
            "accepted__lte",
            "invoicing_start",
            "invoicing_start__gte",
            "invoicing_start__lte",
            "invoicing_end",
            "invoicing_end__gte",
            "invoicing_end__lte",
            name=_("Dates"),
        ),
    )
    tag = TagFilterField(model)
    name = forms.CharField(required=False)
    name_internal = forms.CharField(required=False)
    contract_type = forms.ChoiceField(
        label="Contract Type",
        choices=(
            ("All", "All"),
            ("Contract", "Contract"),
            ("Subcontract", "Subcontract"),
        ),
        required=False,
        initial="All",
    )
    contractor_id = DynamicModelMultipleChoiceField(
        queryset=Contractor.objects.all(), required=False, label=_("Contractor")
    )

    parent_id = DynamicModelMultipleChoiceField(
        queryset=Contract.objects.filter(parent_id=None),
        required=False,
        label=_("Parent Contract"),
    )
    type = forms.MultipleChoiceField(choices=ContractTypeChoices, required=False)
    price = forms.DecimalField(required=False)
    accepted__gte = forms.DateField(required=False, label=("Accepted From"), widget=DatePicker())
    accepted__lte = forms.DateField(required=False, label=("Accepted Till"), widget=DatePicker())
    accepted = forms.DateField(required=False, label=("Accepted"), widget=DatePicker())
    signed__gte = forms.DateField(required=False, label=("Signed From"), widget=DatePicker())
    signed__lte = forms.DateField(required=False, label=("Signed Till"), widget=DatePicker())
    signed = forms.DateField(required=False, label=("Signed"), widget=DatePicker())
    invoicing_start__gte = forms.DateField(required=False, label=("Invoicing Start: From"), widget=DatePicker())
    invoicing_start__lte = forms.DateField(required=False, label=("Invoicing Start: Till"), widget=DatePicker())
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())

    invoicing_end__gte = forms.DateField(required=False, label=("Invoicing End: From"), widget=DatePicker())
    invoicing_end__lte = forms.DateField(required=False, label=("Invoicing End: Till"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())


class ContractBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(max_length=100, required=False)
    name_internal = forms.CharField(max_length=100, required=False)
    contractor = DynamicModelChoiceField(queryset=Contractor.objects.all(), required=False)
    type = forms.ChoiceField(choices=ContractTypeChoices, required=False)
    price = forms.DecimalField(required=False)
    signed = forms.DateField(required=False, widget=DatePicker())
    accepted = forms.DateField(required=False, widget=DatePicker())
    invoicing_start = forms.DateField(required=False, widget=DatePicker())
    invoicing_end = forms.DateField(required=False, widget=DatePicker())

    model = Contract
    nullable_fields = ("name_internal", "price", "signed", "accepted", "invoicing_start", "invoicing_end")
