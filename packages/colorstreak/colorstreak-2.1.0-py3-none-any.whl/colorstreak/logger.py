class Logger:
    """
    Clase para manejar logs con colores, con métodos accesibles directamente como Logger.info(), Logger.warning(), etc.
    """
    COLORS = {
        "debug": "\033[92m",     # Green
        "info": "\033[94m",      # Blue
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "library": "\033[95m" # Magenta
    }
    RESET = "\033[0m"  # Reset color

    @staticmethod
    def _print(message, level):
        """
        Método interno para imprimir mensajes con colores.
        """
        color = Logger.COLORS.get(level, Logger.RESET)
        print(f"{color}[{level.upper()}] {message}{Logger.RESET}")

    @staticmethod
    def debug(message):
        Logger._print(message, "debug")

    @staticmethod
    def info(message):
        Logger._print(message, "info")

    @staticmethod
    def warning(message):
        Logger._print(message, "warning")

    @staticmethod
    def error(message):
        Logger._print(message, "error")

    @staticmethod
    def library(message):
        Logger._print(message, "library")
