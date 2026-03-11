from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Hallazgo, Auditoria, Incidente, Indicador, Competencia, Obra, Configuracion


class StyledMixin:
    """Agrega clase form-control a todos los widgets excepto checkboxes."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                cls = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (cls + ' form-control').strip()


class HallazgoForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Hallazgo
        fields = ['titulo', 'descripcion', 'proceso', 'severidad', 'estado', 'fecha_cierre']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date'}),
        }


class AuditoriaForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Auditoria
        fields = [
            'titulo', 'tipo', 'estado', 'proceso', 'responsable',
            'fecha_programada', 'fecha_realizacion', 'hallazgos_encontrados', 'observaciones',
        ]
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_realizacion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class IncidenteForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Incidente
        fields = ['titulo', 'descripcion', 'proceso', 'estado', 'causa_raiz', 'fecha_resolucion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'causa_raiz': forms.Textarea(attrs={'rows': 3}),
            'fecha_resolucion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class IndicadorForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Indicador
        fields = [
            'nombre', 'area', 'formula', 'responsable',
            'valor', 'meta', 'unidad', 'mejor_al', 'tendencia',
            'incluir_historico', 'tabla_dinamica',
        ]
        widgets = {
            'formula': forms.Textarea(attrs={'rows': 2}),
        }


class CompetenciaForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Competencia
        fields = [
            'nombre', 'descripcion', 'area', 'responsable',
            'nivel_requerido', 'nivel_actual', 'estado',
            'fecha_evaluacion', 'fecha_vencimiento',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'fecha_evaluacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }


class ObraForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['nombre', 'descripcion', 'responsable', 'fecha_inicio', 'fecha_fin_programada', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_programada': forms.DateInput(attrs={'type': 'date'}),
        }


class UsuarioCrearForm(StyledMixin, UserCreationForm):
    is_staff = forms.BooleanField(required=False, label='Rol Administrador')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'password1', 'password2']


class UsuarioEditarForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
        labels = {
            'is_staff':  'Rol Administrador',
            'is_active': 'Cuenta activa',
        }


class ConfiguracionForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['nombre_empresa', 'descripcion', 'email_contacto', 'logo_url']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class GrupoForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        labels = {'name': 'Nombre del grupo'}
