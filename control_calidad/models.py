from django.db import models


class Proceso(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('interrumpido', 'Interrumpido'),
        ('en_revision', 'En Revisión'),
    ]
    nombre = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proceso"
        verbose_name_plural = "Procesos"


class Hallazgo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('cerrado', 'Cerrado'),
    ]
    SEVERIDAD_CHOICES = [
        ('critico', 'Crítico'),
        ('alto', 'Alto'),
        ('medio', 'Medio'),
        ('bajo', 'Bajo'),
    ]
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    severidad = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES, default='medio')
    fecha_reporte = models.DateField(auto_now_add=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    proceso = models.ForeignKey(Proceso, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Hallazgo"
        verbose_name_plural = "Hallazgos"


class Incidente(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_investigacion', 'En Investigación'),
        ('cerrado', 'Cerrado'),
    ]
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    causa_raiz = models.TextField(blank=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    proceso = models.ForeignKey(Proceso, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def tiempo_respuesta_horas(self):
        if self.fecha_resolucion:
            delta = self.fecha_resolucion - self.fecha_reporte
            return round(delta.total_seconds() / 3600, 1)
        return None

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Incidente"
        verbose_name_plural = "Incidentes"


class Obra(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('finalizado', 'Finalizado'),
        ('retrasado', 'Retrasado'),
    ]
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    responsable = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin_programada = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')

    @property
    def avance_real(self):
        fases = self.fases.all()
        if not fases:
            return 0
        return round(sum(float(f.avance_real) for f in fases) / len(fases), 1)

    @property
    def avance_programado(self):
        fases = self.fases.all()
        if not fases:
            return 0
        return round(sum(float(f.avance_programado) for f in fases) / len(fases), 1)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Obra"
        verbose_name_plural = "Obras"
        ordering = ['-fecha_inicio']


class FaseObra(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('retrasada', 'Retrasada'),
    ]
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name='fases')
    nombre = models.CharField(max_length=200)
    avance_programado = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    avance_real = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    fecha_inicio = models.DateField()
    fecha_fin_programada = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.obra.nombre} — {self.nombre}"

    class Meta:
        verbose_name = "Fase de Obra"
        verbose_name_plural = "Fases de Obra"
        ordering = ['fecha_inicio']


class Indicador(models.Model):
    MEJOR_AL_CHOICES = [
        ('alza', 'Alza'),
        ('baja', 'Baja'),
    ]
    TENDENCIA_CHOICES = [
        ('alza', 'Alza'),
        ('baja', 'Baja'),
        ('estable', 'Estable'),
    ]
    nombre = models.CharField(max_length=300)
    area = models.CharField(max_length=200)
    formula = models.TextField(blank=True)
    responsable = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    meta = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=50, blank=True, default='%')
    mejor_al = models.CharField(max_length=10, choices=MEJOR_AL_CHOICES, default='alza')
    tendencia = models.CharField(max_length=10, choices=TENDENCIA_CHOICES, default='estable')
    incluir_historico = models.BooleanField(default=True)
    tabla_dinamica = models.BooleanField(default=False)
    fecha_registro = models.DateField(auto_now_add=True)

    @property
    def cumple_meta(self):
        if self.mejor_al == 'alza':
            return float(self.valor) >= float(self.meta)
        return float(self.valor) <= float(self.meta)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"
        ordering = ['area', 'nombre']


class IndicadorCumplimiento(models.Model):
    valor = models.DecimalField(max_digits=5, decimal_places=1)
    meta = models.DecimalField(max_digits=5, decimal_places=1)
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.valor}% (meta: {self.meta}%) - {self.fecha}"

    class Meta:
        verbose_name = "Indicador de Cumplimiento"
        verbose_name_plural = "Indicadores de Cumplimiento"
        ordering = ['-fecha']
