import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ClienteHTTP:
    """
    Cliente para realizar llamadas HTTP reutilizables basado en requests.Session.
    Permite descargar archivos y está diseñado para ser fácilmente ampliable.
    """

    def __init__(self, headers=None, timeout=10, verify_ssl=True):
        self.log = logging.getLogger()
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get(self, url, params=None, headers=None):
        params = params or {}
        request_headers = self.session.headers.copy()
        request_headers.update(headers or {})
        try:
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log.error(f"Error HTTP en GET a {url}: {e}")
            raise

    def post(self, url, *, data=None, files=None, headers=None):
        data = data or {}
        request_headers = self.session.headers.copy()
        request_headers.update(headers or {})
        try:
            response = self.session.post(
                url,
                data=data,
                files=files,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log.error(f"Error HTTP en POST a {url}: {e}")
            raise

    def post_con_reintentos(self, url, *, data=None, files=None, headers=None, reintentos=3, delay=3):
        """
        Realiza un POST con reintentos automáticos en caso de fallo temporal.
        reintentos: número máximo de intentos (default: 3).
        delay: backoff_factor -> tiempo de espera entre reintentos (ej: 3 → 3s, 6s, 12s).
        """
        data = data or {}
        request_headers = self.session.headers.copy()
        request_headers.update(headers or {})

        session_tmp = requests.Session()
        session_tmp.headers.update(request_headers)

        retry_strategy = Retry(total=reintentos, backoff_factor=delay, status_forcelist=[408, 429, 500, 502, 503, 504, 507], allowed_methods=["POST"])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session_tmp.mount("http://", adapter)
        session_tmp.mount("https://", adapter)

        try:
            response = session_tmp.post(url, data=data, files=files, headers=request_headers, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log.error(f"Error HTTP en POST con reintentos a {url}: {e}")
            raise
        finally:
            session_tmp.close()


    def descargar_archivo(self, url, destino):
        """
        Descarga un archivo desde la URL dada y lo guarda en la ruta 'destino'.
        """
        try:
            response = self.session.get(
                url,
                stream=True,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            with open(destino, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.log.info(f"Archivo descargado correctamente desde {url} a {destino}")
            return True

        except requests.RequestException as e:
            self.log.error(f"Error HTTP al descargar {url}: {e}")
            raise

        except Exception as e:
            self.log.error(f"Error general al descargar {url}: {e}")
            raise

    def cerrar(self):
        """
        Cierra la sesión HTTP y libera recursos.
        """
        if self.session:
            self.session.close()
        self.log.info("Sesión HTTP cerrada correctamente.")
