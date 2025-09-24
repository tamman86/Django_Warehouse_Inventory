from django import forms
from .models import Pump, Valve, Filter, MixTank, CommandCenter, Misc

class PumpForm(forms.ModelForm):
    class Meta:
        model = Pump
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location',
            'speed', 'inlet', 'outlet', 'moc', 'power'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class ValveForm(forms.ModelForm):
    class Meta:
        model = Valve
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location',
            'moc', 'size', 'valve_type'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class FilterForm(forms.ModelForm):
    class Meta:
        model = Filter
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location',
            'inlet', 'outlet', 'moc', 'filter_type'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class MixTankForm(forms.ModelForm):
    class Meta:
        model = MixTank
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location',
            'inlet', 'outlet', 'moc', 'power'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class CommandCenterForm(forms.ModelForm):
    class Meta:
        model = CommandCenter
        fields = ['item_id', 'description', 'location']
        widgets = {
            'category': forms.HiddenInput(),
        }

class MiscForm(forms.ModelForm):
    class Meta:
        model = Misc
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location',
            'speed', 'inlet', 'outlet', 'moc', 'power', 'quantity'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }