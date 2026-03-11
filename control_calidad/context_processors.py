from .models import Configuracion


def app_config(request):
    """Inyecta la configuración del sistema en todos los templates."""
    config = Configuracion.objects.first()
    if config is None:
        config = Configuracion()  # objeto sin guardar con valores por defecto
    return {'app_config': config}
