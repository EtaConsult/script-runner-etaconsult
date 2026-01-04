"""
Script d'exemple avec arguments
Montre comment accepter des paramètres depuis l'interface
"""

import sys
from datetime import datetime

def main():
    # Vérifie si un argument a été fourni
    if len(sys.argv) < 2:
        print("❌ Erreur : Aucun texte fourni")
        print("Usage: python exemple_avec_args.py <texte>")
        sys.exit(1)
    
    texte = sys.argv[1]
    
    print("="*60)
    print("📝 Script avec Arguments - Démarrage")
    print("="*60)
    
    print(f"\n📥 Texte reçu : '{texte}'")
    print(f"📏 Longueur : {len(texte)} caractères")
    print(f"🔤 Majuscules : {texte.upper()}")
    print(f"🔡 Minuscules : {texte.lower()}")
    print(f"🔄 Inversé : {texte[::-1]}")
    
    print("\n" + "="*60)
    print(f"✨ Analyse terminée à {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()
