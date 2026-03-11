from django.contrib import admin
from .models import Proceso, Hallazgo, Incidente, Auditoria, Competencia, Indicador, IndicadorCumplimiento, Obra, FaseObra, Configuracion


@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    list_filter = ('estado',)


@admin.register(Hallazgo)
class HallazgoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'estado', 'severidad', 'proceso', 'fecha_reporte')
    list_filter = ('estado', 'severidad', 'proceso')
    date_hierarchy = 'fecha_reporte'


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'estado', 'proceso', 'fecha_reporte', 'fecha_resolucion')
    list_filter = ('estado', 'proceso')
    date_hierarchy = 'fecha_reporte'


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'estado', 'proceso', 'responsable', 'fecha_programada', 'hallazgos_encontrados')
    list_filter = ('tipo', 'estado', 'proceso')
    search_fields = ('titulo', 'responsable')
    date_hierarchy = 'fecha_programada'


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'responsable', 'nivel_requerido', 'nivel_actual', 'estado', 'fecha_evaluacion')
    list_filter = ('area', 'estado')
    search_fields = ('nombre', 'area', 'responsable')
    date_hierarchy = 'fecha_evaluacion'


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'valor', 'meta', 'unidad', 'mejor_al', 'tendencia', 'responsable', 'fecha_registro')
    list_filter = ('area', 'mejor_al', 'tendencia')
    search_fields = ('nombre', 'area', 'responsable')
    date_hierarchy = 'fecha_registro'


@admin.register(IndicadorCumplimiento)
class IndicadorCumplimientoAdmin(admin.ModelAdmin):
    list_display = ('valor', 'meta', 'fecha', 'descripcion')
    date_hierarchy = 'fecha'


class FaseObraInline(admin.TabularInline):
    model = FaseObra
    extra = 1


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'responsable', 'estado', 'fecha_inicio', 'fecha_fin_programada')
    list_filter = ('estado',)
    date_hierarchy = 'fecha_inicio'
    inlines = [FaseObraInline]


@admin.register(FaseObra)
class FaseObraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'obra', 'avance_real', 'avance_programado', 'estado', 'fecha_fin_programada')
    list_filter = ('estado', 'obra')


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'email_contacto')
