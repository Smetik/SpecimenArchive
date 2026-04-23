from django import forms

from .models import Incident, Specimen


class BaseArchiveModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-checkbox'
            field.widget.attrs['class'] = css_class
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('rows', 4)
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('data-control', name)


class SpecimenForm(BaseArchiveModelForm):
    class Meta:
        model = Specimen
        fields = [
            'code',
            'name',
            'status',
            'short_description',
            'summary',
            'containment_protocol',
            'threat_level',
            'is_active',
        ]


class IncidentForm(BaseArchiveModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['specimen'].queryset = Specimen.objects.order_by('code')

    class Meta:
        model = Incident
        fields = [
            'specimen',
            'title',
            'description',
            'response_protocol',
            'severity',
            'is_resolved',
        ]
