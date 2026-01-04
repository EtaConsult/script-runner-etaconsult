"""
Script d'exemple simple
Ce script montre comment créer un script qui fonctionne avec Script Runner
"""

import time
from datetime import datetime

def main():
    print("="*60)
    print("🎯 Script Exemple Simple - Démarrage")
    print("="*60)
    
    # Simulation d'un traitement
    print("\n📊 Analyse en cours...")
    time.sleep(1)
    
    print("✅ Étape 1 : Chargement des données")
    time.sleep(0.5)
    
    print("✅ Étape 2 : Traitement")
    time.sleep(0.5)
    
    print("✅ Étape 3 : Génération du résultat")
    time.sleep(0.5)
    
    print("\n" + "="*60)
    print(f"✨ Terminé avec succès à {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()
