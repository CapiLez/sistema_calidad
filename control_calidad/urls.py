from django.urls import path
from . import views

urlpatterns = [
    # Módulos principales
    path('', views.dashboard, name='dashboard'),
    path('avance-obra/', views.avance_obra, name='avance_obra'),
    path('indicadores/', views.indicadores, name='indicadores'),
    path('hallazgos/', views.hallazgos, name='hallazgos'),
    path('auditorias/', views.auditorias, name='auditorias'),
    path('incidentes/', views.incidentes, name='incidentes'),
    path('competencias/', views.competencias, name='competencias'),

    # Módulos de administración (solo staff)
    path('usuarios/',                   views.usuarios,         name='usuarios'),
    path('usuarios/<int:pk>/editar/',   views.usuario_editar,   name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name='usuario_eliminar'),
    path('permisos/',                   views.permisos,         name='permisos'),
    path('permisos/<int:pk>/eliminar/', views.grupo_eliminar,   name='grupo_eliminar'),
    path('configuracion/',              views.configuracion,    name='configuracion'),

    # Exportaciones CSV
    path('avance-obra/exportar/', views.exportar_avance_obra, name='exportar_avance_obra'),
    path('indicadores/exportar/', views.exportar_indicadores, name='exportar_indicadores'),
    path('hallazgos/exportar/', views.exportar_hallazgos, name='exportar_hallazgos'),
    path('auditorias/exportar/', views.exportar_auditorias, name='exportar_auditorias'),
    path('incidentes/exportar/', views.exportar_incidentes, name='exportar_incidentes'),
    path('competencias/exportar/', views.exportar_competencias, name='exportar_competencias'),
]
