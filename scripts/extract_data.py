import os
import json
import csv
import time
from pathlib import Path
from dotenv import load_dotenv

# Asegurar que el path sea el del proyecto para poder importar desde src
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.extraction.github_client import GitHubClient

load_dotenv()

def main():
    print("🚀 Iniciando extracción de datos de GitHub Perú...")
    
    client = GitHubClient()
    
    # Directorios de salida
    base_dir = Path(__file__).parent.parent
    processed_dir = base_dir / "data" / "processed"
    raw_dir = base_dir / "data" / "raw"
    
    # Asegurar que existan
    processed_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Listas para almacenar datos
    users_data = []
    repos_data = []
    
    # Buscamos usuarios en Perú
    target_repos = 1100
    collected_repos_count = 0
    
    query = "location:Peru"
    page = 1
    
    try:
        while collected_repos_count < target_repos:
            print(f"\nBuscando usuarios (página {page})...")
            search_result = client.search_users(query=query, sort="repositories", order="desc", per_page=50, page=page)
            
            items = search_result.get("items", [])
            if not items:
                print("⚠️ No se encontraron más usuarios.")
                break
                
            for user_item in items:
                username = user_item["login"]
                print(f"👤 Procesando usuario: {username}")
                
                # Obtener detalles completos del usuario
                user_detail = client.get_user(username)
                
                # Obtener actividad técnica adicional (Rubric compliance)
                activity_counts = client.get_user_activity_counts(username)
                user_detail.update(activity_counts)
                
                users_data.append(user_detail)
                
                # Obtener repositorios del usuario
                repos = client.get_user_repos(username, type="owner", sort="updated", per_page=100)
                
                for repo in repos:
                    if repo.get("fork", False):
                        continue
                        
                    repo_name = repo["name"]
                    print(f"  📦 Extrayendo repo: {repo_name} ({repo.get('language', 'N/A')})")
                    
                    # Extraer el README (requerido para la clasificación)
                    readme_data = client.get_repo_readme(username, repo_name)
                    readme_content = ""
                    if readme_data and "content" in readme_data:
                        import base64
                        try:
                            readme_content = base64.b64decode(readme_data["content"]).decode('utf-8')
                        except Exception:
                            readme_content = ""
                            
                    readme_content = readme_content[:5000] if readme_content else ""
                    
                    # Extraer lenguajes explícitos
                    languages = client.get_repo_languages(username, repo_name)
                    
                    # Almacenamos toda la metadata relevante
                    repo_info = {
                        "owner": username,
                        "name": repo_name,
                        "description": repo.get("description", ""),
                        "url": repo.get("html_url", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language", ""),
                        "languages_bytes": json.dumps(languages) if languages else "{}",
                        "created_at": repo.get("created_at", ""),
                        "updated_at": repo.get("updated_at", ""),
                        "readme_content": readme_content
                    }
                    
                    repos_data.append(repo_info)
                    collected_repos_count += 1
                    
                    if collected_repos_count >= target_repos:
                        print(f"\n✅ Alcanzado el objetivo de {target_repos} repositorios extraídos!")
                        break
                        
                if collected_repos_count >= target_repos:
                    break
                    
            page += 1
            time.sleep(2)
            
    except Exception as e:
        print(f"\n❌ Error durante la extracción: {e}")
        print("Guardando datos parciales recolectados hasta ahora...")
        
    finally:
        # Guardado de datos a CSV
        print(f"\n💾 Guardando {len(users_data)} usuarios y {len(repos_data)} repositorios...")
        
        if users_data:
            users_file = processed_dir / "users.csv"
            keys = ["login", "id", "name", "company", "location", "public_repos", "followers", "following", "created_at"]
            with open(users_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(users_data)
                
        if repos_data:
            repos_file = processed_dir / "repositories.csv"
            keys = repos_data[0].keys()
            with open(repos_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(repos_data)
                
        print("✅ Extracción finalizada.")

if __name__ == "__main__":
    main()

