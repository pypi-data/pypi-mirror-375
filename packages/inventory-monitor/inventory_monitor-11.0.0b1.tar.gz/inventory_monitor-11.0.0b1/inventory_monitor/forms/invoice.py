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

from inventory_monitor.models import Contract, Invoice


class InvoiceForm(NetBoxModelForm):
    comments = CommentField(label="Comments")
    contract = DynamicModelChoiceField(queryset=Contract.objects.all(), required=True)
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())

    class Meta:
        model = Invoice
        fields = (
            "name",
            "name_internal",
            "project",
            "contract",
            "price",
            "invoicing_start",
            "invoicing_end",
            "comments",
            "tags",
        )


class InvoiceFilterForm(NetBoxModelFilterSetForm):
    model = Invoice

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("name", "name_internal", "project", name=_("Common")),
        FieldSet("contract_id", name=_("Linked")),
        FieldSet(
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
    project = forms.CharField(required=False)
    contract_id = DynamicModelMultipleChoiceField(queryset=Contract.objects.all(), required=False, label=_("Contract"))
    price = forms.DecimalField(required=False)
    invoicing_start__gte = forms.DateField(required=False, label=("Invoicing Start: From"), widget=DatePicker())
    invoicing_start__lte = forms.DateField(required=False, label=("Invoicing Start: Till"), widget=DatePicker())
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())

    invoicing_end__gte = forms.DateField(required=False, label=("Invoicing End: From"), widget=DatePicker())
    invoicing_end__lte = forms.DateField(required=False, label=("Invoicing End: Till"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())


class InvoiceBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(max_length=100, required=False)
    name_internal = forms.CharField(max_length=100, required=False)
    project = forms.CharField(max_length=100, required=False)
    contract = DynamicModelChoiceField(queryset=Contract.objects.all(), required=False)
    price = forms.DecimalField(required=False)
    invoicing_start = forms.DateField(required=False, widget=DatePicker())
    invoicing_end = forms.DateField(required=False, widget=DatePicker())

    model = Invoice
    nullable_fields = ("name_internal", "project", "price", "invoicing_start", "invoicing_end")
