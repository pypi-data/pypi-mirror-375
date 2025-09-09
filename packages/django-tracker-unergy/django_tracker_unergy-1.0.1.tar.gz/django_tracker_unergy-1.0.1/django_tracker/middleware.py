import threading

_user = threading.local()


class TrackerModelMiddleware:
    """Inicialización del tracker, asigna el usuario actual a una variable de hilo local.
    Esto permite que los modelos accedan al usuario actual sin necesidad de pasarlo explícitamente.
    Proporciona una forma sencilla de rastrear qué usuario realizó cambios en los modelos de Django.

    El usuario se almacena en `_user.value` y puede ser accedido mediante la función `get_current_user()`.
    Esto porque en la db no existe el usuario
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> object:
        _user.value = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        return response


def get_current_user() -> object | None:
    """Obtiene el usuario actual desde el hilo local"""
    return getattr(_user, "value", None)
