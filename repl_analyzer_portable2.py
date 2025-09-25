#!/usr/bin/env python3
"""
🔍 Analyseur de Projet Replit - Version Portable
================================================================

Script autonome pour analyser n'importe quel projet Replit.
Copiez ce fichier dans votre projet et exécutez-le !

Utilisation:
    python repl_analyzer_portable.py

Auteur: Assistant IA pour emmanuelgoitia
Date: 2024-09-24
"""

import os
import json
import csv
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ReplInfo:
    """Informations sur le repl"""
    id: str
    name: str
    slug: str
    language: str
    is_public: bool
    is_always_on: bool
    is_boosted: bool
    user_id: str
    user_name: str
    url: str

class ReplitProjectAnalyzer:
    """Analyseur de projet Replit autonome"""
    
    def __init__(self):
        """Initialise l'analyseur"""
        self.repl_info: Optional[ReplInfo] = None
        self.project_path = Path.cwd()
        
    def parse_repl_identity(self) -> Optional[Dict[str, Any]]:
        """Parse le token REPL_IDENTITY pour extraire les métadonnées"""
        repl_identity = os.getenv('REPL_IDENTITY')
        if not repl_identity:
            return None
            
        try:
            # REPL_IDENTITY est un token encodé, on essaie de l'analyser
            parts = repl_identity.split('.')
            if len(parts) >= 2:
                # Décoder la partie payload (souvent la deuxième partie)
                payload_part = parts[1]
                # Ajouter padding si nécessaire
                missing_padding = len(payload_part) % 4
                if missing_padding:
                    payload_part += '=' * (4 - missing_padding)
                
                try:
                    decoded_bytes = base64.b64decode(payload_part)
                    decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                    # Chercher des informations JSON dans le contenu décodé
                    if '{' in decoded_str and '}' in decoded_str:
                        start = decoded_str.find('{')
                        end = decoded_str.rfind('}') + 1
                        json_str = decoded_str[start:end]
                        return json.loads(json_str)
                except:
                    pass
                    
        except Exception:
            pass
            
        return None
    
    def load_repl_info(self):
        """Charge les informations du repl depuis les variables d'environnement"""
        # Essayer d'abord de parser REPL_IDENTITY
        identity_data = self.parse_repl_identity()
        
        if identity_data:
            print("✅ Données extraites de REPL_IDENTITY")
            # Utiliser les données de REPL_IDENTITY si disponibles
            self.repl_info = ReplInfo(
                id=identity_data.get('repl_id', os.getenv('REPL_ID', 'unknown')),
                name=identity_data.get('repl_name', identity_data.get('name', os.getenv('REPL_NAME', 'Unknown'))),
                slug=identity_data.get('repl_slug', identity_data.get('slug', os.getenv('REPL_SLUG', 'unknown'))),
                language=identity_data.get('language', 'Unknown'),
                is_public=identity_data.get('is_public', False),
                is_always_on=identity_data.get('is_always_on', False),
                is_boosted=identity_data.get('is_boosted', False),
                user_id=identity_data.get('user_id', 'unknown'),
                user_name=identity_data.get('user_name', os.getenv('REPL_OWNER', 'unknown')),
                url=f"https://replit.com/@{os.getenv('REPL_OWNER', 'unknown')}/{identity_data.get('repl_slug', identity_data.get('slug', os.getenv('REPL_SLUG', 'unknown')))}"
            )
        else:
            print("⚠️  Utilisation des variables d'environnement comme fallback")
            # Fallback vers les variables d'environnement
            self.repl_info = ReplInfo(
                id=os.getenv('REPL_ID', 'unknown'),
                name=os.getenv('REPL_NAME', 'Unknown'),
                slug=os.getenv('REPL_SLUG', 'unknown'),
                language=os.getenv('REPL_LANGUAGE', os.getenv('LANG', 'Unknown')),
                is_public=False,  # Pas d'info disponible
                is_always_on=False,
                is_boosted=False,
                user_id='unknown',
                user_name=os.getenv('REPL_OWNER', 'unknown'),
                url=f"https://replit.com/@{os.getenv('REPL_OWNER', 'unknown')}/{os.getenv('REPL_SLUG', 'unknown')}"
            )
    
    def analyze_file_structure(self) -> Dict[str, Any]:
        """Analyse la structure des fichiers du projet"""
        file_types = {}
        total_files = 0
        total_directories = 0
        size_estimate = 0
        main_files = []
        
        # Extensions importantes à identifier comme fichiers principaux
        main_extensions = {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb'}
        main_filenames = {'main.py', 'index.html', 'app.py', 'server.js', 'main.js', 'README.md', 'requirements.txt', 'package.json'}
        
        try:
            for item in self.project_path.rglob('*'):
                # Ignorer les dossiers cachés et système
                if any(part.startswith('.') for part in item.parts):
                    continue
                if '__pycache__' in str(item) or 'node_modules' in str(item):
                    continue
                
                if item.is_file():
                    total_files += 1
                    
                    # Analyser l'extension
                    suffix = item.suffix.lower()
                    if suffix:
                        file_types[suffix] = file_types.get(suffix, 0) + 1
                    else:
                        file_types['sans_extension'] = file_types.get('sans_extension', 0) + 1
                    
                    # Identifier les fichiers principaux
                    if item.name in main_filenames or suffix in main_extensions:
                        main_files.append(item.name)
                    
                    # Estimer la taille
                    try:
                        size_estimate += item.stat().st_size
                    except:
                        size_estimate += 1024  # Estimation par défaut
                        
                elif item.is_dir():
                    total_directories += 1
                    
        except Exception as e:
            print(f"⚠️  Erreur lors de l'analyse : {e}")
        
        return {
            'total_files': total_files,
            'total_directories': total_directories,
            'file_types': file_types,
            'size_estimate': size_estimate,
            'main_files': sorted(set(main_files))[:10]  # Limiter à 10 fichiers principaux
        }
    
    def get_environment_info(self) -> Dict[str, str]:
        """Récupère les informations d'environnement pertinentes"""
        env_vars = {}
        interesting_vars = [
            'REPL_SLUG', 'REPL_OWNER', 'REPL_ID', 'REPL_NAME', 'REPL_LANGUAGE',
            'REPLIT_DB_URL', 'REPLIT_CLUSTER', 'LANG', 'REPLIT_DEV_DOMAIN'
        ]
        
        for var in interesting_vars:
            value = os.getenv(var)
            if value:
                env_vars[var] = value
        
        return env_vars
    
    def generate_report(self) -> Dict[str, Any]:
        """Génère le rapport complet d'analyse"""
        structure = self.analyze_file_structure()
        environment = self.get_environment_info()
        
        return {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'analysis_type': 'REPL_IDENTITY_PORTABLE',
                'repl_domain': self.repl_info.name if self.repl_info else 'Unknown',
                'analyzer_version': '1.0_portable'
            },
            'repl_info': {
                'id': self.repl_info.id,
                'name': self.repl_info.name,
                'slug': self.repl_info.slug,
                'language': self.repl_info.language,
                'is_public': self.repl_info.is_public,
                'is_always_on': self.repl_info.is_always_on,
                'is_boosted': self.repl_info.is_boosted,
                'user_id': self.repl_info.user_id,
                'user_name': self.repl_info.user_name,
                'url': self.repl_info.url
            } if self.repl_info else {},
            'structure_analysis': structure,
            'environment': environment
        }
    
    def export_to_json(self, filename: str = None) -> str:
        """Exporte le rapport en JSON"""
        report = self.generate_report()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        repl_name = self.repl_info.name if self.repl_info else 'unknown'
        # Nettoyer le nom pour le nom de fichier
        safe_name = "".join(c for c in repl_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = filename or f"repl_analysis_{safe_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def export_to_csv(self, filename: str = None) -> str:
        """Exporte un résumé en CSV"""
        report = self.generate_report()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        repl_name = self.repl_info.name if self.repl_info else 'unknown'
        safe_name = "".join(c for c in repl_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = filename or f"repl_summary_{safe_name}_{timestamp}.csv"
        
        # Créer une version aplatie pour CSV
        csv_data = {
            'repl_id': report['repl_info'].get('id', ''),
            'repl_name': report['repl_info'].get('name', ''),
            'repl_slug': report['repl_info'].get('slug', ''),
            'language': report['repl_info'].get('language', ''),
            'is_public': report['repl_info'].get('is_public', False),
            'user_name': report['repl_info'].get('user_name', ''),
            'url': report['repl_info'].get('url', ''),
            'total_files': report['structure_analysis']['total_files'],
            'total_directories': report['structure_analysis']['total_directories'],
            'size_estimate_bytes': report['structure_analysis']['size_estimate'],
            'size_estimate_kb': round(report['structure_analysis']['size_estimate'] / 1024, 2),
            'main_files': '; '.join(report['structure_analysis']['main_files']),
            'file_types': '; '.join([f"{k}:{v}" for k, v in report['structure_analysis']['file_types'].items()]),
            'analysis_date': report['metadata']['analysis_date']
        }
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data.keys())
            writer.writeheader()
            writer.writerow(csv_data)
        
        return filename
    
    def print_summary(self):
        """Affiche un résumé des informations"""
        if not self.repl_info:
            print("❌ Impossible de charger les informations du repl")
            return
        
        structure = self.analyze_file_structure()
        
        print("============================================================")
        print("📊 ANALYSE DU PROJET REPLIT")
        print("============================================================")
        print(f"📂 Nom : {self.repl_info.name}")
        print(f"🔗 URL : {self.repl_info.url}")
        print(f"💻 Langage : {self.repl_info.language}")
        print(f"👤 Propriétaire : {self.repl_info.user_name}")
        print(f"🌐 Public : {'Oui' if self.repl_info.is_public else 'Non'}")
        print(f"⚡ Always On : {'Oui' if self.repl_info.is_always_on else 'Non'}")
        print(f"🚀 Boosted : {'Oui' if self.repl_info.is_boosted else 'Non'}")
        print()
        print(f"📁 STRUCTURE :")
        print(f"  • {structure['total_files']} fichiers")
        print(f"  • {structure['total_directories']} dossiers")
        print(f"  • Taille estimée : {structure['size_estimate'] / 1024:.1f} KB")
        print()
        
        if structure['file_types']:
            print(f"📄 TYPES DE FICHIERS :")
            for ext, count in sorted(structure['file_types'].items()):
                print(f"  • {ext}: {count} fichier{'s' if count > 1 else ''}")
        
        if structure['main_files']:
            print()
            print(f"🔑 FICHIERS PRINCIPAUX :")
            for file in structure['main_files'][:5]:  # Afficher max 5 fichiers
                print(f"  • {file}")
        
        print("============================================================")

def main():
    """Fonction principale"""
    print("🔍 Analyseur de Projet Replit - Version Portable")
    print("=" * 53)
    print()
    print("📊 Analyse du projet en cours...")
    
    # Créer l'analyseur
    analyzer = ReplitProjectAnalyzer()
    
    # Charger les informations du repl
    analyzer.load_repl_info()
    
    # Afficher le résumé
    analyzer.print_summary()
    
    # Exporter les données
    print()
    print("📤 Export des données...")
    json_file = analyzer.export_to_json()
    csv_file = analyzer.export_to_csv()
    
    print("✅ Analyse terminée !")
    print(f"📁 Fichiers générés :")
    print(f"  • {json_file}")
    print(f"  • {csv_file}")
    print()
    print("💡 Copiez ce script dans d'autres projets pour les analyser !")

if __name__ == "__main__":
    main()