from django.shortcuts import render
from .models import Hallazgo, Incidente, Proceso, Indicador, IndicadorCumplimiento, Obra


def dashboard(request):
    # Indicador de cumplimiento global (último registrado)
    indicador = IndicadorCumplimiento.objects.first()
    cumplimiento_global = indicador.valor if indicador else 0
    cumplimiento_meta = indicador.meta if indicador else 95

    # Factor de incidentes: incidentes activos / procesos activos
    total_incidentes = Incidente.objects.exclude(estado='cerrado').count()
    total_procesos = Proceso.objects.filter(estado='activo').count()
    factor_incidentes = round(total_incidentes / total_procesos, 1) if total_procesos else 0
    factor_meta = 2.0

    # Tiempo de respuesta promedio (incidentes cerrados con fecha de resolución)
    incidentes_cerrados = Incidente.objects.filter(
        estado='cerrado', fecha_resolucion__isnull=False
    )
    tiempos = [i.tiempo_respuesta_horas for i in incidentes_cerrados if i.tiempo_respuesta_horas is not None]
    tiempo_respuesta = round(sum(tiempos) / len(tiempos), 1) if tiempos else 0

    # Hallazgos críticos
    hallazgos_criticos = Hallazgo.objects.filter(severidad='critico').count()

    # Alertas del sistema
    hallazgos_pendientes = Hallazgo.objects.filter(estado='pendiente').count()
    procesos_interrumpidos = Proceso.objects.filter(estado='interrumpido')
    incidentes_sin_causa_raiz = Incidente.objects.filter(
        causa_raiz='', estado__in=['abierto', 'en_investigacion']
    ).count()

    # Anchos de barra de progreso normalizados a 0-100
    cumplimiento_bar = round(float(cumplimiento_global), 1)
    factor_bar       = round(min(float(factor_incidentes) / 5.0 * 100, 100), 1)
    tiempo_bar       = round(min(float(tiempo_respuesta) / 10.0 * 100, 100), 1)
    hallazgos_bar    = round(min(float(hallazgos_criticos) / 20.0 * 100, 100), 1)

    context = {
        'cumplimiento_global': cumplimiento_global,
        'cumplimiento_meta': cumplimiento_meta,
        'cumplimiento_bar': cumplimiento_bar,
        'factor_incidentes': factor_incidentes,
        'factor_meta': factor_meta,
        'factor_bar': factor_bar,
        'tiempo_respuesta': tiempo_respuesta,
        'tiempo_bar': tiempo_bar,
        'hallazgos_criticos': hallazgos_criticos,
        'hallazgos_bar': hallazgos_bar,
        'hallazgos_pendientes': hallazgos_pendientes,
        'procesos_interrumpidos': procesos_interrumpidos,
        'incidentes_sin_causa_raiz': incidentes_sin_causa_raiz,
    }
    return render(request, 'dashboard.html', context)


def avance_obra(request):
    obras = Obra.objects.prefetch_related('fases').all()

    total_obras = obras.count()
    obras_activas = obras.filter(estado='activo').count()
    obras_finalizadas = obras.filter(estado='finalizado').count()
    obras_retrasadas = obras.filter(estado='retrasado').count()

    avances = [obra.avance_real for obra in obras]
    avance_promedio = round(sum(avances) / len(avances), 1) if avances else 0

    context = {
        'obras': obras,
        'total_obras': total_obras,
        'obras_activas': obras_activas,
        'obras_finalizadas': obras_finalizadas,
        'obras_retrasadas': obras_retrasadas,
        'avance_promedio': avance_promedio,
    }
    return render(request, 'avance_obra.html', context)


def indicadores(request):
    todos = Indicador.objects.all()
    total = todos.count()

    cumpliendo = sum(1 for i in todos if i.cumple_meta)
    por_debajo = total - cumpliendo

    en_alza = todos.filter(tendencia='alza').count()
    en_baja = todos.filter(tendencia='baja').count()

    context = {
        'indicadores': todos,
        'total': total,
        'cumpliendo': cumpliendo,
        'por_debajo': por_debajo,
        'en_alza': en_alza,
        'en_baja': en_baja,
    }
    return render(request, 'indicadores.html', context)
