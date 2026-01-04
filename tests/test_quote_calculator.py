# -*- coding: utf-8 -*-
"""
Tests unitaires pour QuoteCalculator
Tests basiques pour valider la logique de calcul
"""

import sys
import os

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from quote_calculator import QuoteCalculator


# ==========================================
# DONNÉES DE TEST
# ==========================================

TARIFS_TEST = {
    "base_price": 500,
    "km_factor_proche": 0.9,
    "km_factor_loin": 0.7,
    "km_seuil": 25,
    "surface_factor_petit": 0.6,
    "surface_factor_grand": 0.5,
    "surface_seuil": 750,
    "plus_factor": 1.4,
    "plus_price_max": 1989,
    "frais_emission_cecb": 80,
    "prix_conseil_incitatif": 0,
    "forfait_normal": 0,
    "forfait_express": 135,
    "forfait_urgent": 270
}

GOOGLE_API_KEY_TEST = ""  # Pas de clé pour les tests
ETA_ADDRESS_TEST = "Route de l'Hôpital 16b, 1180 Rolle, Suisse"


# ==========================================
# TESTS DE CALCUL CECB
# ==========================================

def test_calcul_prix_cecb_standard():
    """Test du calcul de prix CECB standard"""
    print("\n🧪 Test 1: Calcul prix CECB standard")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    # Bâtiment proche (< 25 km), petit (< 750 m²)
    # Distance: 15 km, Surface équivalente: 500 m²
    # Prix = 500 + (15 × 0.9) + (500 × 0.6) = 500 + 13.5 + 300 = 813.5 ≈ 814 CHF
    price = calc.calculate_cecb_price(distance_km=15, surface_eq=500, is_plus=False)

    expected = 814
    assert price == expected, f"❌ Prix incorrect: {price} au lieu de {expected}"
    print(f"✅ Prix CECB calculé correctement: {price} CHF")


def test_calcul_prix_cecb_loin_grand():
    """Test du calcul avec bâtiment loin et grand"""
    print("\n🧪 Test 2: Calcul prix CECB bâtiment loin et grand")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    # Bâtiment loin (>= 25 km), grand (>= 750 m²)
    # Distance: 50 km, Surface équivalente: 1000 m²
    # Prix = 500 + (50 × 0.7) + (1000 × 0.5) = 500 + 35 + 500 = 1035 CHF
    price = calc.calculate_cecb_price(distance_km=50, surface_eq=1000, is_plus=False)

    expected = 1035
    assert price == expected, f"❌ Prix incorrect: {price} au lieu de {expected}"
    print(f"✅ Prix CECB calculé correctement: {price} CHF")


def test_calcul_prix_cecb_plus():
    """Test du calcul CECB Plus"""
    print("\n🧪 Test 3: Calcul prix CECB Plus")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    # Prix CECB Plus = Prix CECB × 1.4 (max 1989 CHF)
    # Base: 15 km, 500 m² = 814 CHF
    # CECB Plus: 814 × 1.4 = 1139.6 ≈ 1140 CHF
    price = calc.calculate_cecb_price(distance_km=15, surface_eq=500, is_plus=True)

    expected = 1140
    assert price == expected, f"❌ Prix incorrect: {price} au lieu de {expected}"
    print(f"✅ Prix CECB Plus calculé correctement: {price} CHF")


def test_calcul_prix_cecb_plus_max():
    """Test du plafond CECB Plus"""
    print("\n🧪 Test 4: Test plafond CECB Plus (max 1989 CHF)")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    # Bâtiment très grand: 50 km, 2000 m²
    # Prix CECB = 500 + (50 × 0.7) + (2000 × 0.5) = 500 + 35 + 1000 = 1535 CHF
    # CECB Plus = 1535 × 1.4 = 2149 CHF → plafonné à 1989 CHF
    price = calc.calculate_cecb_price(distance_km=50, surface_eq=2000, is_plus=True)

    expected = 1989  # Plafond
    assert price == expected, f"❌ Prix incorrect: {price} au lieu de {expected}"
    print(f"✅ Plafond CECB Plus respecté: {price} CHF")


# ==========================================
# TESTS DE CALCUL D'ÉTAGES ET SURFACES
# ==========================================

def test_calcul_etages_equivalents():
    """Test du calcul des étages équivalents"""
    print("\n🧪 Test 5: Calcul étages équivalents")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    # gastw: 3, sous-sol chauffé (1), combles partiellement chauffés (0.5)
    # Total: 3 + 1 + 0.5 = 4.5
    et_eq = calc.calculate_equivalent_floors(
        gastw=3,
        sous_sol="Chauffé",
        combles="Partiellement chauffé 50%"
    )

    expected = 4.5
    assert et_eq == expected, f"❌ Étages incorrects: {et_eq} au lieu de {expected}"
    print(f"✅ Étages équivalents calculés correctement: {et_eq}")


def test_calcul_surface_equivalente():
    """Test du calcul de la surface équivalente"""
    print("\n🧪 Test 6: Calcul surface équivalente")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    # 3 étages × 200 m² = 600 m²
    s_eq = calc.calculate_equivalent_surface(et_eq=3, garea=200)

    expected = 600
    assert s_eq == expected, f"❌ Surface incorrecte: {s_eq} au lieu de {expected}"
    print(f"✅ Surface équivalente calculée correctement: {s_eq} m²")


# ==========================================
# TESTS DE FORFAIT EXÉCUTION
# ==========================================

def test_forfait_execution_normal():
    """Test du forfait exécution normal"""
    print("\n🧪 Test 7: Forfait exécution normal")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    surcharge, label = calc.calculate_deadline_surcharge("Normal")

    assert surcharge == 0, f"❌ Surcharge incorrecte: {surcharge} au lieu de 0"
    assert label == "Normal", f"❌ Label incorrect: {label}"
    print(f"✅ Forfait normal: {surcharge} CHF ({label})")


def test_forfait_execution_express():
    """Test du forfait exécution express"""
    print("\n🧪 Test 8: Forfait exécution express")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    surcharge, label = calc.calculate_deadline_surcharge("Express (+135 CHF)")

    assert surcharge == 135, f"❌ Surcharge incorrecte: {surcharge} au lieu de 135"
    assert label == "Express", f"❌ Label incorrect: {label}"
    print(f"✅ Forfait express: {surcharge} CHF ({label})")


def test_forfait_execution_urgent():
    """Test du forfait exécution urgent"""
    print("\n🧪 Test 9: Forfait exécution urgent")

    calc = QuoteCalculator(TARIFS_TEST, GOOGLE_API_KEY_TEST, ETA_ADDRESS_TEST)

    surcharge, label = calc.calculate_deadline_surcharge("Urgent (+270 CHF)")

    assert surcharge == 270, f"❌ Surcharge incorrecte: {surcharge} au lieu de 270"
    assert label == "Urgent", f"❌ Label incorrect: {label}"
    print(f"✅ Forfait urgent: {surcharge} CHF ({label})")


# ==========================================
# EXÉCUTION DES TESTS
# ==========================================

def run_all_tests():
    """Lance tous les tests"""
    print("=" * 60)
    print("🧪 TESTS UNITAIRES - QuoteCalculator")
    print("=" * 60)

    tests = [
        test_calcul_prix_cecb_standard,
        test_calcul_prix_cecb_loin_grand,
        test_calcul_prix_cecb_plus,
        test_calcul_prix_cecb_plus_max,
        test_calcul_etages_equivalents,
        test_calcul_surface_equivalente,
        test_forfait_execution_normal,
        test_forfait_execution_express,
        test_forfait_execution_urgent
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} ÉCHOUÉ: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERREUR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS: {passed} tests réussis, {failed} tests échoués")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
