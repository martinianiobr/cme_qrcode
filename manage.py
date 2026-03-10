#!/usr/bin/env python
import os
import sys


def main():
    """Ponto de entrada para comandos Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cme_qrcode.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar Django. Verifique se ele está instalado "
            "e se o ambiente virtual (venv) está ativado."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

