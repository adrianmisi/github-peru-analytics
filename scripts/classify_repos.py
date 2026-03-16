import os
import csv
import json
import time
import asyncio
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.classification.industry_classifier import IndustryClassifier

load_dotenv()

async def classify_repo_async(classifier: IndustryClassifier, repo: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Clasifica un repositorio de forma asíncrona controlando el paralelismo con un semáforo."""
    async with semaphore:
        key = f"{repo['owner']}/{repo['name']}"
        try:
            description = repo.get("description", "")
            readme = repo.get("readme_content", "")[:2000]
            
            loop = asyncio.get_event_loop()
            prediction = await loop.run_in_executor(
                None, 
                classifier.classify_repository, 
                repo['name'], 
                description, 
                readme
            )
            
            print(f"✅ {key} -> {prediction.get('category')}")
            
        except Exception as e:
            print(f"❌ Error en {key}: {e}")
            prediction = {
                "category": "Desconocido",
                "confidence": 0,
                "reasoning": f"Error asíncrono: {e}"
            }
            await asyncio.sleep(2)
            
        return {
            "owner": repo["owner"],
            "name": repo["name"],
            "industry": prediction.get("category", "Desconocido"),
            "confidence": prediction.get("confidence", 0),
            "reasoning": prediction.get("reasoning", "")
        }

async def process_batch(classifier: IndustryClassifier, batch: List[Dict], max_concurrent: int) -> List[Dict]:
    """Procesa un lote de repositorios concurrentemente."""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [classify_repo_async(classifier, repo, semaphore) for repo in batch]
    return await asyncio.gather(*tasks)

def _save_to_csv(filepath: Path, data_list: List[Dict]):
    """Guarda una lista de diccionarios en disco de forma segura."""
    if not data_list:
        return
    keys = ["owner", "name", "industry", "confidence", "reasoning"]
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data_list)

async def main_async():
    print("🤖 Iniciando clasificación de industrias con GPT-4...")
    
    base_dir = Path(__file__).parent.parent
    processed_dir = base_dir / "data" / "processed"
    
    repos_file = processed_dir / "repositories.csv"
    classifications_file = processed_dir / "classifications.csv"
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: Falta OPENAI_API_KEY.")
        return
        
    classifier = IndustryClassifier()
    
    repos_to_process = []
    if not repos_file.exists():
        print(f"❌ No se encontró el archivo {repos_file}")
        return

    with open(repos_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            repos_to_process.append(row)
            
    existing_classifications = {}
    if classifications_file.exists():
        with open(classifications_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['owner']}/{row['name']}"
                existing_classifications[key] = row
                
    results = list(existing_classifications.values())
    
    pending_repos = [r for r in repos_to_process if f"{r['owner']}/{r['name']}" not in existing_classifications]
    
    print(f"📦 Total repositorios: {len(repos_to_process)}")
    print(f"🔄 Ya procesados: {len(existing_classifications)}")
    print(f"⏳ Pendientes por procesar: {len(pending_repos)}")
    
    if not pending_repos:
        print("✅ Nada nuevo que procesar.")
        return

    BATCH_SIZE = 50 
    MAX_CONCURRENT_REQUESTS = 10 
    
    for i in range(0, len(pending_repos), BATCH_SIZE):
        batch = pending_repos[i:i+BATCH_SIZE]
        print(f"\n🚀 Procesando lote {i//BATCH_SIZE + 1} ({len(batch)} items)...")
        
        batch_results = await process_batch(classifier, batch, MAX_CONCURRENT_REQUESTS)
        results.extend(batch_results)
        
        _save_to_csv(classifications_file, results)
        print(f"💾 Progreso guardado: {len(results)}/{len(repos_to_process)} completados.")
        
        if i + BATCH_SIZE < len(pending_repos):
            print("⏳ Pausa de 3 segundos...")
            await asyncio.sleep(3)

    print(f"\n✅ Clasificación completada.")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()

