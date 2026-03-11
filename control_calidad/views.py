import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import HttpResponse

from .models import Hallazgo, Incidente, Proceso, Indicador, IndicadorCumplimiento, Obra, Auditoria, Competencia, Configuracion
from .forms import HallazgoForm, AuditoriaForm, IncidenteForm, IndicadorForm, CompetenciaForm, ObraForm, UsuarioCrearForm, UsuarioEditarForm, GrupoForm, ConfiguracionForm


# ── helpers ──────────────────────────────────────────────────────────────────

def _csv_response(filename):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    resp.write('\ufeff')   # BOM para Excel
    return resp


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


# ── dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    indicador = IndicadorCumplimiento.objects.first()
    cumplimiento_global = indicador.valor if indicador else 0
    cumplimiento_meta = indicador.meta if indicador else 95

    total_incidentes = Incidente.objects.exclude(estado='cerrado').count()
    total_procesos = Proceso.objects.filter(estado='activo').count()
    factor_incidentes = round(total_incidentes / total_procesos, 1) if total_procesos else 0
    factor_meta = 2.0

    incidentes_cerrados = Incidente.objects.filter(estado='cerrado', fecha_resolucion__isnull=False)
    tiempos = [i.tiempo_respuesta_horas for i in incidentes_cerrados if i.tiempo_respuesta_horas is not None]
    tiempo_respuesta = round(sum(tiempos) / len(tiempos), 1) if tiempos else 0

    hallazgos_criticos = Hallazgo.objects.filter(severidad='critico').count()
    hallazgos_pendientes = Hallazgo.objects.filter(estado='pendiente').count()
    procesos_interrumpidos = Proceso.objects.filter(estado='interrumpido')
    incidentes_sin_causa_raiz = Incidente.objects.filter(
        causa_raiz='', estado__in=['abierto', 'en_investigacion']
    ).count()

    cumplimiento_bar = round(float(cumplimiento_global), 1)
    factor_bar       = round(min(float(factor_incidentes) / 5.0 * 100, 100), 1)
    tiempo_bar       = round(min(float(tiempo_respuesta) / 10.0 * 100, 100), 1)
    hallazgos_bar    = round(min(float(hallazgos_criticos) / 20.0 * 100, 100), 1)

    # Tabs data
    indicadores_tabla = Indicador.objects.filter(tabla_dinamica=True).order_by('-fecha_registro')[:10]
    _hist_qs = Indicador.objects.filter(incluir_historico=True).order_by('-fecha_registro')[:8]
    indicadores_historico = []
    for _ind in _hist_qs:
        _pct = 0
        if _ind.meta:
            _pct = min(int(round(float(_ind.valor) / float(_ind.meta) * 100)), 100)
        indicadores_historico.append({'ind': _ind, 'pct': _pct, 'ok': _ind.cumple_meta})
    obras_dash = list(Obra.objects.prefetch_related('fases').order_by('-id')[:5])

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
        'indicadores_tabla': indicadores_tabla,
        'indicadores_historico': indicadores_historico,
        'obras_dash': obras_dash,
    }
    return render(request, 'dashboard.html', context)


# ── avance de obra ─────────────────────────────────────────────────────────────

@login_required
def avance_obra(request):
    form = ObraForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Obra registrada exitosamente.')
            return redirect('avance_obra')
        show_modal = True

    obras = Obra.objects.prefetch_related('fases').all()
    avances = [obra.avance_real for obra in obras]
    context = {
        'obras': obras,
        'total_obras': obras.count(),
        'obras_activas': obras.filter(estado='activo').count(),
        'obras_finalizadas': obras.filter(estado='finalizado').count(),
        'obras_retrasadas': obras.filter(estado='retrasado').count(),
        'avance_promedio': round(sum(avances) / len(avances), 1) if avances else 0,
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'avance_obra.html', context)


@login_required
def exportar_avance_obra(request):
    resp = _csv_response('avance_obra.csv')
    w = csv.writer(resp)
    w.writerow(['Obra', 'Responsable', 'Estado', 'Avance Real (%)', 'Avance Programado (%)', 'F. Inicio', 'F. Fin Programada'])
    for o in Obra.objects.all():
        w.writerow([o.nombre, o.responsable, o.get_estado_display(),
                    o.avance_real, o.avance_programado, o.fecha_inicio, o.fecha_fin_programada])
    return resp


# ── indicadores ───────────────────────────────────────────────────────────────

@login_required
def indicadores(request):
    form = IndicadorForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Indicador creado exitosamente.')
            return redirect('indicadores')
        show_modal = True

    todos = Indicador.objects.all()
    cumpliendo = sum(1 for i in todos if i.cumple_meta)
    context = {
        'indicadores': todos,
        'total': todos.count(),
        'cumpliendo': cumpliendo,
        'por_debajo': todos.count() - cumpliendo,
        'en_alza': todos.filter(tendencia='alza').count(),
        'en_baja': todos.filter(tendencia='baja').count(),
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'indicadores.html', context)


@login_required
def exportar_indicadores(request):
    resp = _csv_response('indicadores.csv')
    w = csv.writer(resp)
    w.writerow(['Nombre', 'Área', 'Responsable', 'Valor', 'Meta', 'Unidad', 'Mejor al', 'Tendencia', 'Cumple Meta'])
    for ind in Indicador.objects.all():
        w.writerow([ind.nombre, ind.area, ind.responsable,
                    ind.valor, ind.meta, ind.unidad,
                    ind.get_mejor_al_display(), ind.get_tendencia_display(),
                    'Sí' if ind.cumple_meta else 'No'])
    return resp


# ── hallazgos ─────────────────────────────────────────────────────────────────

@login_required
def hallazgos(request):
    form = HallazgoForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Hallazgo registrado exitosamente.')
            return redirect('hallazgos')
        show_modal = True

    qs = Hallazgo.objects.select_related('proceso').order_by('-fecha_reporte')
    severidad_f = request.GET.get('severidad', '')
    estado_f    = request.GET.get('estado', '')
    proceso_f   = request.GET.get('proceso', '')
    if severidad_f: qs = qs.filter(severidad=severidad_f)
    if estado_f:    qs = qs.filter(estado=estado_f)
    if proceso_f:   qs = qs.filter(proceso_id=proceso_f)

    todos = Hallazgo.objects.all()
    context = {
        'hallazgos': qs,
        'total':     todos.count(),
        'pendientes': todos.filter(estado='pendiente').count(),
        'en_proceso': todos.filter(estado='en_proceso').count(),
        'cerrados':   todos.filter(estado='cerrado').count(),
        'criticos':   todos.filter(severidad='critico').count(),
        'procesos':   Proceso.objects.filter(estado='activo'),
        'severidad_f': severidad_f,
        'estado_f':    estado_f,
        'proceso_f':   proceso_f,
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'hallazgos.html', context)


@login_required
def exportar_hallazgos(request):
    resp = _csv_response('hallazgos.csv')
    w = csv.writer(resp)
    w.writerow(['Título', 'Proceso', 'Severidad', 'Estado', 'Fecha Reporte', 'Fecha Cierre', 'Descripción'])
    for h in Hallazgo.objects.select_related('proceso').all():
        w.writerow([h.titulo, h.proceso.nombre if h.proceso else '',
                    h.get_severidad_display(), h.get_estado_display(),
                    h.fecha_reporte, h.fecha_cierre or '', h.descripcion])
    return resp


# ── auditorías ────────────────────────────────────────────────────────────────

@login_required
def auditorias(request):
    form = AuditoriaForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Auditoría registrada exitosamente.')
            return redirect('auditorias')
        show_modal = True

    qs = Auditoria.objects.select_related('proceso').order_by('-fecha_programada')
    tipo_f   = request.GET.get('tipo', '')
    estado_f = request.GET.get('estado', '')
    if tipo_f:   qs = qs.filter(tipo=tipo_f)
    if estado_f: qs = qs.filter(estado=estado_f)

    todos = Auditoria.objects.all()
    context = {
        'auditorias': qs,
        'total': todos.count(),
        'programadas': todos.filter(estado='programada').count(),
        'en_curso':    todos.filter(estado='en_curso').count(),
        'finalizadas': todos.filter(estado='finalizada').count(),
        'total_hallazgos': sum(a.hallazgos_encontrados for a in todos),
        'tipo_f':   tipo_f,
        'estado_f': estado_f,
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'auditorias.html', context)


@login_required
def exportar_auditorias(request):
    resp = _csv_response('auditorias.csv')
    w = csv.writer(resp)
    w.writerow(['Título', 'Tipo', 'Proceso', 'Responsable', 'Estado',
                'F. Programada', 'F. Realización', 'Hallazgos', 'Observaciones'])
    for a in Auditoria.objects.select_related('proceso').all():
        w.writerow([a.titulo, a.get_tipo_display(),
                    a.proceso.nombre if a.proceso else '',
                    a.responsable, a.get_estado_display(),
                    a.fecha_programada, a.fecha_realizacion or '',
                    a.hallazgos_encontrados, a.observaciones])
    return resp


# ── incidentes ────────────────────────────────────────────────────────────────

@login_required
def incidentes(request):
    form = IncidenteForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidente registrado exitosamente.')
            return redirect('incidentes')
        show_modal = True

    qs = Incidente.objects.select_related('proceso').order_by('-fecha_reporte')
    estado_f  = request.GET.get('estado', '')
    proceso_f = request.GET.get('proceso', '')
    if estado_f:  qs = qs.filter(estado=estado_f)
    if proceso_f: qs = qs.filter(proceso_id=proceso_f)

    todos = Incidente.objects.all()
    resueltos = todos.filter(estado='cerrado', fecha_resolucion__isnull=False)
    tiempos = [i.tiempo_respuesta_horas for i in resueltos if i.tiempo_respuesta_horas is not None]
    context = {
        'incidentes': qs,
        'total':           todos.count(),
        'abiertos':        todos.filter(estado='abierto').count(),
        'en_investigacion': todos.filter(estado='en_investigacion').count(),
        'cerrados':        todos.filter(estado='cerrado').count(),
        'sin_causa':       todos.filter(causa_raiz='', estado__in=['abierto', 'en_investigacion']).count(),
        'tiempo_promedio': round(sum(tiempos) / len(tiempos), 1) if tiempos else 0,
        'procesos':  Proceso.objects.filter(estado='activo'),
        'estado_f':  estado_f,
        'proceso_f': proceso_f,
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'incidentes.html', context)


@login_required
def exportar_incidentes(request):
    resp = _csv_response('incidentes.csv')
    w = csv.writer(resp)
    w.writerow(['Título', 'Proceso', 'Estado', 'Causa Raíz',
                'Fecha Reporte', 'Fecha Resolución', 'Tiempo Respuesta (h)'])
    for inc in Incidente.objects.select_related('proceso').all():
        w.writerow([inc.titulo, inc.proceso.nombre if inc.proceso else '',
                    inc.get_estado_display(), inc.causa_raiz or 'Pendiente',
                    inc.fecha_reporte.strftime('%Y-%m-%d %H:%M'),
                    inc.fecha_resolucion.strftime('%Y-%m-%d %H:%M') if inc.fecha_resolucion else '',
                    inc.tiempo_respuesta_horas or ''])
    return resp


# ── competencias ──────────────────────────────────────────────────────────────

@login_required
def competencias(request):
    form = CompetenciaForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Competencia registrada exitosamente.')
            return redirect('competencias')
        show_modal = True

    qs = Competencia.objects.order_by('area', 'nombre')
    area_f   = request.GET.get('area', '')
    estado_f = request.GET.get('estado', '')
    if area_f:   qs = qs.filter(area__icontains=area_f)
    if estado_f: qs = qs.filter(estado=estado_f)

    todos = Competencia.objects.all()
    cumpliendo = sum(1 for c in todos if c.cumple)
    context = {
        'competencias': qs,
        'total':      todos.count(),
        'cumpliendo': cumpliendo,
        'con_brecha': todos.count() - cumpliendo,
        'vencidas':   todos.filter(estado='vencida').count(),
        'por_vencer': todos.filter(estado='por_vencer').count(),
        'areas':      todos.values_list('area', flat=True).distinct(),
        'area_f':   area_f,
        'estado_f': estado_f,
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'competencias.html', context)


@login_required
def exportar_competencias(request):
    resp = _csv_response('competencias.csv')
    w = csv.writer(resp)
    w.writerow(['Nombre', 'Área', 'Responsable', 'Nivel Requerido', 'Nivel Actual',
                'Brecha', 'Estado', 'F. Evaluación', 'Vencimiento'])
    for c in Competencia.objects.all():
        w.writerow([c.nombre, c.area, c.responsable,
                    c.nivel_requerido, c.nivel_actual, c.brecha,
                    c.get_estado_display(), c.fecha_evaluacion, c.fecha_vencimiento or ''])
    return resp


# ── usuarios (solo admin) ─────────────────────────────────────────────────────

@staff_required
def usuarios(request):
    form = UsuarioCrearForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('usuarios')
        show_modal = True

    context = {
        'usuarios': User.objects.all().order_by('username'),
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'usuarios.html', context)


@staff_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UsuarioEditarForm(request.POST or None, instance=usuario)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuarios')
    return render(request, 'usuario_editar.html', {'form': form, 'usuario': usuario})


@staff_required
def usuario_eliminar(request, pk):
    if request.method == 'POST':
        usuario = get_object_or_404(User, pk=pk)
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
        else:
            usuario.delete()
            messages.success(request, 'Usuario eliminado.')
    return redirect('usuarios')


# ── permisos / grupos (solo admin) ───────────────────────────────────────────

@staff_required
def permisos(request):
    form = GrupoForm(request.POST or None)
    show_modal = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo creado exitosamente.')
            return redirect('permisos')
        show_modal = True

    grupos = Group.objects.prefetch_related('user_set').all()
    context = {
        'grupos': grupos,
        'form': form,
        'show_modal': show_modal,
    }
    return render(request, 'permisos.html', context)


@staff_required
def grupo_eliminar(request, pk):
    if request.method == 'POST':
        grupo = get_object_or_404(Group, pk=pk)
        grupo.delete()
        messages.success(request, 'Grupo eliminado.')
    return redirect('permisos')


# ── configuración (solo admin) ────────────────────────────────────────────────

@staff_required
def configuracion(request):
    config = Configuracion.get_instancia()
    form = ConfiguracionForm(request.POST or None, instance=config)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada.')
            return redirect('configuracion')
    return render(request, 'configuracion.html', {'form': form, 'config': config})
