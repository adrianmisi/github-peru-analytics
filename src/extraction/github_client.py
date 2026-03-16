import os
import time
import requests
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class RateLimitException(Exception):
    """Excepción lanzada cuando se alcanza el límite de tasa de la API de GitHub."""
    def __init__(self, message, reset_time=None):
        super().__init__(message)
        self.reset_time = reset_time

class GitHubClient:
    """Cliente para interactuar con la API de GitHub con manejo automático de limites de tasa."""
    
    def __init__(self, token=None):
        """
        Inicializa el cliente de GitHub.
        
        Args:
            token (str, opcional): Token de acceso personal de GitHub. Si no se provee,
                                  intenta obtenerlo de la variable de entorno GITHUB_TOKEN.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("Se requiere un GITHUB_TOKEN. Defínelo al instanciar o en el archivo .env")
            
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = "https://api.github.com"
        # Usamos una sola sesión para reutilizar conexiones HTTP subyacentes
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _handle_rate_limit(self, response):
        """Verifica los headers de rate limit y lanza una excepción si se alcanzó."""
        if response.status_code in [403, 429]:
            # Verificar si es por rate limit
            if "X-RateLimit-Remaining" in response.headers and response.headers["X-RateLimit-Remaining"] == "0":
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                raise RateLimitException("Límite de tasa de la API de GitHub alcanzado.", reset_time=reset_time)
            
            # Chequear también secondary limits (abusos) a veces retornan 403 con mensaje específico
            try:
                data = response.json()
                if "message" in data and ("rate limit" in data["message"].lower() or "secondary rate limit" in data["message"].lower()):
                    # Secondary rate limits o a veces no retornan headers de remaining=0
                    retry_after = int(response.headers.get("Retry-After", 60))
                    reset_time = int(time.time()) + retry_after
                    raise RateLimitException("Límite de tasa secundario de GitHub alcanzado.", reset_time=reset_time)
            except ValueError:
                pass
                
        response.raise_for_status()

    # Decorador de retry: 
    # - Sólo reintenta si es de tipo requests.exceptions.RequestException, PERO
    # - El manejo principal se debe pausar cuando golpeamos explicitamente RateLimitException
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    )
    def make_request(self, endpoint, params=None):
        """
        Realiza una petición GET a un endpoint específico tratando automáticamente el rate limit.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        while True:
            try:
                response = self.session.get(url, params=params)
                self._handle_rate_limit(response)
                return response.json()
                
            except RateLimitException as e:
                # Si fallamos por rate limit, esperamos el tiempo necesario
                current_time = int(time.time())
                wait_time = max(1, e.reset_time - current_time + 1)
                
                print(f"⚠️ [Rate Limit alcanzado] Esperando {wait_time} segundos para el reinicio (hasta {time.strftime('%H:%M:%S', time.localtime(e.reset_time))})...")
                
                # En un caso extremo, si el tiempo es demasiado (ej > 1h), podríamos detener el script
                if wait_time > 3600:
                    print(f"❌ Espera demasiado larga ({wait_time}s). Abortando.")
                    raise e
                    
                time.sleep(wait_time)
                # Al terminar el sleep el while True internamente vuelve a intentar url.get()

    def search_users(self, query, sort="followers", order="desc", per_page=100, page=1):
        """
        Busca usuarios en GitHub según un query específico.
        """
        endpoint = "search/users"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        return self.make_request(endpoint, params=params)
        
    def get_user(self, username):
        """Obtiene toda la información (perfil completo) de un usuario específico."""
        return self.make_request(f"users/{username}")
        
    def get_user_repos(self, username, type="owner", sort="updated", per_page=100, page=1):
        """Obtiene los repositorios públicos de un usuario específico."""
        params = {
            "type": type,
            "sort": sort,
            "per_page": per_page,
            "page": page
        }
        return self.make_request(f"users/{username}/repos", params=params)
        
    def get_repo_readme(self, owner, repo):
        """
        Obtiene el README principal de un repositorio.
        Retorna tanto contenido (base64 decodificado o diccionario con details dependiendo endpoint).
        """
        # Usamos el endpoint que retorna info del README y el 'download_url' o 'content' en base64
        try:
            return self.make_request(f"repos/{owner}/{repo}/readme")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None  # No hay README
            raise e
            
    def get_repo_languages(self, owner, repo):
        """Obtiene el desglose de bytes por lenguaje en el repo."""
        return self.make_request(f"repos/{owner}/{repo}/languages")
