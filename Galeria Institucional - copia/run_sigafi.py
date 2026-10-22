import threading
import time
import webbrowser

from app import app


def iniciar_flask():
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":

    servidor = threading.Thread(target=iniciar_flask)
    servidor.daemon = True
    servidor.start()

    # Espera a que Flask inicie
    time.sleep(2)

    # Abre el navegador automáticamente
    webbrowser.open("http://127.0.0.1:5000")

    # Mantiene vivo el programa
    servidor.join()