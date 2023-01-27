from django import forms
from .models import Struk

class StrukForm(forms.ModelForm):
    class Meta:
        model = Struk
        fields = ('plat_nomor', 'tipekendaraan')

        widgets = {
            'plat_nomor': forms.TextInput(attrs={'class':'form-control border'}),
            'tipekendaraan': forms.Select(attrs={'class':'form-control border', }),
        }   

class SearchForm(forms.Form):
    search_input = forms.CharField()

class TiketForm(forms.ModelForm):
    plat_nomor = forms.CharField