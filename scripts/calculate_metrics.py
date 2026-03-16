import json
import csv
from datetime import datetime
from pathlib import Path
import os
from collections import Counter, defaultdict

import sys
sys.path.append(str(Path(__file__).parent.parent))

def load_csv_data(filepath):
    if not filepath.exists():
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_csv_data(filepath, fieldnames, data):
    os.makedirs(filepath.parent, exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def save_json_data(filepath, data):
    os.makedirs(filepath.parent, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_user_metrics(users, repos, classifications):
    """Calcula las métricas solicitadas a nivel de usuario."""
    repos_by_owner = defaultdict(list)
    for repo in repos:
        repos_by_owner[repo['owner']].append(repo)
        
    classifications_by_repo = {}
    for cl in classifications:
        key = f"{cl['owner']}/{cl['name']}"
        classifications_by_repo[key] = cl

    user_metrics = []
    
    for user in users:
        owner = user['login']
        user_repos = repos_by_owner.get(owner, [])
        
        activity_score = user.get('public_repos', 0)
        
        total_repo_stars = sum(int(r.get('stargazers_count', 0)) for r in user_repos)
        followers = int(user.get('followers', 0))
        influence_score = total_repo_stars + followers
        
        languages_used = set()
        for repo in user_repos:
            try:
                # El campo era languages_bytes en extract_data.py nuevo, pero verificamos
                langs_str = repo.get('languages_bytes') or repo.get('languages', '{}')
                langs = json.loads(langs_str)
                if langs:
                    languages_used.update(langs.keys())
            except json.JSONDecodeError:
                pass
        technical_score = len(languages_used)
        
        total_forks = sum(int(r.get('forks_count', 0)) for r in user_repos)
        engagement_score = total_forks
        
        industries_in_repos = []
        for repo in user_repos:
            key = f"{owner}/{repo['name']}"
            if key in classifications_by_repo:
                ind = classifications_by_repo[key].get('industry')
                if ind and ind != "Desconocido":
                    industries_in_repos.append(ind)
                    
        dominant_industry = "Desconocido"
        if industries_in_repos:
            dominant_industry = Counter(industries_in_repos).most_common(1)[0][0]

        # Lógica de Clustering para "Talent Analytics"
        # Categorías: Elite, Expert, Active, Rising, Contributor
        activity_int = int(activity_score)
        if influence_score > 500:
            cluster = "Elite Developer"
        elif influence_score > 100 or activity_int > 50:
            cluster = "Expert Developer"
        elif technical_score > 5:
            cluster = "Polyglot / Active"
        elif engagement_score > 10:
            cluster = "High Engagement"
        else:
            cluster = "Rising Talent"


        user_metrics.append({
            "login": owner,
            "name": user.get('name', ''),
            "company": user.get('company', ''),
            "location": user.get('location', ''),
            "activity_repos": activity_score,
            "influence_score": influence_score,
            "technical_languages": technical_score,
            "engagement_forks": engagement_score,
            "primary_industry": dominant_industry,
            "developer_cluster": cluster
        })

        
    return user_metrics

def calculate_ecosystem_metrics(users, repos, classifications):
    """Calcula métricas agregadas del ecosistema de Perú."""
    total_users = len(users)
    total_repos = len(repos)
    
    all_languages = Counter()
    for repo in repos:
        try:
            langs_str = repo.get('languages_bytes') or repo.get('languages', '{}')
            langs = json.loads(langs_str)
            for lang, bytes_count in langs.items():
                all_languages[lang] += bytes_count
        except json.JSONDecodeError:
            pass
            
    top_languages = dict(all_languages.most_common(10))
    
    industry_counter = Counter()
    for cl in classifications:
        industry_counter[cl.get('industry', 'Desconocido')] += 1
        
    top_industries = dict(industry_counter.most_common(10))
    
    locations = Counter()
    for user in users:
        loc = str(user.get('location', '')).lower()
        if 'lima' in loc:
            locations['Lima'] += 1
        elif 'arequipa' in loc:
            locations['Arequipa'] += 1
        elif 'cusco' in loc or 'cuzco' in loc:
            locations['Cusco'] += 1
        else:
            locations['Other Peru'] += 1
            
    avg_followers_per_user = sum(int(u.get('followers', 0)) for u in users) / max(total_users, 1)
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "totals": {
            "users": total_users,
            "repositories": total_repos,
            "classifications": len(classifications)
        },
        "averages": {
            "followers_per_user": round(avg_followers_per_user, 2),
            "repos_per_user": round(total_repos / max(total_users, 1), 2)
        },
        "top_languages_by_bytes": top_languages,
        "top_industries_by_repo_count": top_industries,
        "geo_distribution": dict(locations)
    }
    
    return metrics

def main():
    print("📈 Iniciando procesamiento de métricas...")
    
    base_dir = Path(__file__).parent.parent
    processed_dir = base_dir / "data" / "processed"
    metrics_dir = base_dir / "data" / "metrics"
    
    users = load_csv_data(processed_dir / "users.csv")
    repos = load_csv_data(processed_dir / "repositories.csv")
    classifications = load_csv_data(processed_dir / "classifications.csv")
    
    print(f"✅ Cargados {len(users)} usuarios, {len(repos)} repos, {len(classifications)} clasificaciones.")
    
    user_metrics = calculate_user_metrics(users, repos, classifications)
    if user_metrics:
        fields = list(user_metrics[0].keys())
        save_csv_data(metrics_dir / "user_metrics.csv", fields, user_metrics)
        print(f"💾 Guardadas métricas de usuarios en metrics/user_metrics.csv")
        
    eco_metrics = calculate_ecosystem_metrics(users, repos, classifications)
    save_json_data(metrics_dir / "ecosystem_metrics.json", eco_metrics)
    print(f"💾 Guardadas métricas del ecosistema en metrics/ecosystem_metrics.json")
    
    print("✨ Procesamiento de métricas finalizado.")

if __name__ == "__main__":
    main()

