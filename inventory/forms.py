from django import forms
from .models import RepairLog, Pump, Valve, Filter, MixTank, CommandCenter, Misc

class PumpForm(forms.ModelForm):
    class Meta:
        model = Pump
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location', 'status',
            'speed', 'inlet', 'outlet', 'moc', 'power'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class ValveForm(forms.ModelForm):
    class Meta:
        model = Valve
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location', 'status',
            'moc', 'size', 'valve_type'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class FilterForm(forms.ModelForm):
    class Meta:
        model = Filter
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location', 'status',
            'inlet', 'outlet', 'moc', 'filter_type'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class MixTankForm(forms.ModelForm):
    class Meta:
        model = MixTank
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location', 'status',
            'inlet', 'outlet', 'moc', 'power'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class CommandCenterForm(forms.ModelForm):
    class Meta:
        model = CommandCenter
        fields = ['item_id', 'description', 'location', 'status',]
        widgets = {
            'category': forms.HiddenInput(),
        }

class MiscForm(forms.ModelForm):
    class Meta:
        model = Misc
        fields = [
            'item_id', 'description', 'vendor', 'rating', 'location', 'status',
            'speed', 'inlet', 'outlet', 'moc', 'power', 'quantity'
        ]
        widgets = {
            'category': forms.HiddenInput(),
        }

class RepairLogForm(forms.ModelForm):
    class Meta:
        model = RepairLog
        fields = [
            'repair_company', 'contact_name', 'contact_number', 'contact_email', 'start_date',
            'expected_return_date', 'description', 'cost',
            'document1', 'document2', 'document3', 'document4', 'document5'
        ]

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_return_date': forms.DateInput(attrs={'type': 'date'}),
        }

        labels = {
            'description': 'Repair Description',
            'cost': 'Estimated/Final Cost',
        }