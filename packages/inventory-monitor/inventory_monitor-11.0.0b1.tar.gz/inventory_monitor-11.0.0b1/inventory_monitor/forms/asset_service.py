from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.models import Asset, AssetService, Contract


class AssetServiceForm(NetBoxModelForm):
    fieldsets = (
        FieldSet("contract", "asset", name=_("Linked")),
        FieldSet("service_start", "service_end", name=_("Dates")),
        FieldSet(
            "service_price",
            "service_category",
            "service_category_vendor",
            name=_("Service Params"),
        ),
        FieldSet("tags", name=_("Tag")),
    )

    comments = CommentField(label="Comments")
    service_start = forms.DateField(required=False, label=("Service Start"), widget=DatePicker())
    service_end = forms.DateField(required=False, label=("Service End"), widget=DatePicker())
    service_price = forms.DecimalField(
        required=False,
        label="Service Price",
        initial=0,
        min_value=0,
        decimal_places=2,
    )
    service_category = forms.CharField(
        required=False,
        label="Service Category",
    )
    service_category_vendor = forms.CharField(
        required=False,
        label="Service Category Vendor",
    )
    asset = DynamicModelChoiceField(
        queryset=Asset.objects.all(),
        required=True,
        label="Service Asset",
    )
    contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        required=True,
        label="Service Contract",
    )

    class Meta:
        model = AssetService
        fields = (
            "service_start",
            "service_end",
            "service_price",
            "service_category",
            "service_category_vendor",
            "asset",
            "contract",
            "comments",
            "tags",
        )


class AssetServiceFilterForm(NetBoxModelFilterSetForm):
    model = AssetService

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("asset", "contract", name=_("Linked")),
        FieldSet(
            "service_start",
            "service_start__gte",
            "service_start__lte",
            "service_end",
            "service_end__gte",
            "service_end__lte",
            name=_("Dates"),
        ),
        FieldSet(
            "service_price",
            "service_category",
            "service_category_vendor",
            name=_("Service"),
        ),
    )

    tag = TagFilterField(model)
    service_start = forms.DateField(required=False, label=("Service Start"), widget=DatePicker())
    service_start__gte = forms.DateField(required=False, label=("Service Start: From"), widget=DatePicker())
    service_start__lte = forms.DateField(required=False, label=("Service Start: Till"), widget=DatePicker())
    service_end = forms.DateField(required=False, label=("Service End"), widget=DatePicker())
    service_end__gte = forms.DateField(required=False, label=("Service End: From"), widget=DatePicker())
    service_end__lte = forms.DateField(required=False, label=("Service End: Till"), widget=DatePicker())
    service_price = forms.DecimalField(
        required=False,
        label="Service Price",
        initial=0,
        min_value=0,
        decimal_places=2,
    )
    service_category = forms.CharField(
        required=False,
        label="Service Category",
    )
    service_category_vendor = forms.CharField(
        required=False,
        label="Service Category Vendor",
    )

    asset = DynamicModelMultipleChoiceField(queryset=Asset.objects.all(), required=False, label=_("Asset"))
    contract = DynamicModelMultipleChoiceField(queryset=Contract.objects.all(), required=False, label=_("Contract"))


class AssetServiceBulkEditForm(NetBoxModelBulkEditForm):
    service_start = forms.DateField(required=False, label=("Service Start"), widget=DatePicker())
    service_end = forms.DateField(required=False, label=("Service End"), widget=DatePicker())
    service_price = forms.DecimalField(
        required=False,
        label="Service Price",
        min_value=0,
        decimal_places=2,
    )
    service_category = forms.CharField(
        required=False,
        label="Service Category",
    )
    service_category_vendor = forms.CharField(
        required=False,
        label="Service Category Vendor",
    )
    asset = DynamicModelChoiceField(
        queryset=Asset.objects.all(),
        required=False,
        label="Service Asset",
    )
    contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        required=False,
        label="Service Contract",
    )

    model = AssetService
    fieldsets = (
        FieldSet("service_start", "service_end", name=_("Dates")),
        FieldSet(
            "service_price",
            "service_category",
            "service_category_vendor",
            name=_("Service Params"),
        ),
        FieldSet("asset", "contract", name=_("Linked")),
    )
    nullable_fields = (
        "service_start",
        "service_end",
        "service_price",
        "service_category",
        "service_category_vendor",
    )
