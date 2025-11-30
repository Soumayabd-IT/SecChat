# test_project.py

import pytest
from project import validate_input, detect_cyber_topic, format_response


def test_validate_input():
    """Test de la fonction validate_input avec différents cas"""

    # Cas valides
    assert validate_input("Hello") == True
    assert validate_input("What is malware?") == True
    assert validate_input("Cybersecurity question") == True
    assert validate_input("a") == True
    assert validate_input("123") == True
    assert validate_input("Special chars: !@#$%") == True

    # Cas invalides
    assert validate_input("") == False
    assert validate_input("   ") == False
    assert validate_input("  \n  ") == False
    assert validate_input("\t\t") == False
    assert validate_input(None) == False


def test_detect_cyber_topic():
    """Test de la fonction detect_cyber_topic avec différents mots-clés"""

    # Messages contenant des mots-clés cybersécurité (devrait retourner True)
    assert detect_cyber_topic("What is cybersecurity?") == True
    assert detect_cyber_topic("Tell me about CYBER attacks") == True
    assert detect_cyber_topic("How does malware work?") == True
    assert detect_cyber_topic("Explain phishing attacks") == True
    assert detect_cyber_topic("What is a virus?") == True
    assert detect_cyber_topic("Tell me about hacking") == True
    assert detect_cyber_topic("SECURITY best practices") == True
    assert detect_cyber_topic("ransomware protection") == True
    assert detect_cyber_topic("firewall configuration") == True
    assert detect_cyber_topic("encryption methods") == True

    # Messages sans rapport avec la cybersécurité (devrait retourner False)
    assert detect_cyber_topic("Hello, how are you?") == False
    assert detect_cyber_topic("What's the weather today?") == False
    assert detect_cyber_topic("Tell me a joke") == False
    assert detect_cyber_topic("Recipe for chocolate cake") == False
    assert detect_cyber_topic("Python programming basics") == False

    # Cas limites
    assert detect_cyber_topic("") == False
    assert detect_cyber_topic("   ") == False


def test_format_response():
    """Test de la fonction format_response avec différents types de réponses"""

    # Réponses valides
    assert format_response("This is a test") == "This is a test"
    assert format_response("Malware is malicious software") == "Malware is malicious software"

    # Réponses avec espaces superflus
    assert format_response("  test  ") == "test"
    assert format_response("   response with spaces   ") == "response with spaces"
    assert format_response("\n\ntest\n\n") == "test"
    assert format_response("\t\ttest\t\t") == "test"

    # Réponses vides ou None - CORRIGÉ ICI
    assert format_response("") == "I couldn't generate a response. Please try again."
    assert format_response("   ") == "I couldn't generate a response. Please try again."
    assert format_response(None) == "I couldn't generate a response. Please try again."

    # Réponses avec caractères spéciaux
    assert format_response("Test: 123!") == "Test: 123!"
    assert format_response("Response with émojis 🔒") == "Response with émojis 🔒"


def test_integration():
    """Test d'intégration basique pour vérifier que les fonctions fonctionnent ensemble"""

    # Scénario 1: Question valide sur la cybersécurité
    user_input = "What is malware?"
    assert validate_input(user_input) == True
    assert detect_cyber_topic(user_input) == True

    # Scénario 2: Question invalide
    user_input = ""
    assert validate_input(user_input) == False

    # Scénario 3: Question valide mais hors sujet
    user_input = "What's the weather?"
    assert validate_input(user_input) == True
    assert detect_cyber_topic(user_input) == False

    # Scénario 4: Formatage d'une réponse
    response = "  Malware is malicious software  "
    formatted = format_response(response)
    assert formatted == "Malware is malicious software"
    assert validate_input(formatted) == True


def test_edge_cases():
    """Test des cas extrêmes et limites"""

    # Très longue chaîne
    long_string = "cyber" * 1000
    assert validate_input(long_string) == True
    assert detect_cyber_topic(long_string) == True

    # Caractères Unicode
    assert validate_input("Cybersécurité français") == True
    assert detect_cyber_topic("Sécurité informatique") == True

    # Mélange majuscules/minuscules
    assert detect_cyber_topic("CyBeRsEcUrItY") == True
    assert detect_cyber_topic("MaLwArE") == True

    # Multiples espaces
    assert format_response("test    with    spaces") == "test    with    spaces"


def test_type_handling():
    """Test de la gestion des types de données incorrects"""

    # validate_input avec différents types
    assert validate_input(None) == False
    assert validate_input(123) == False
    assert validate_input([]) == False

    # format_response avec None - CORRIGÉ ICI
    assert format_response(None) == "I couldn't generate a response. Please try again."


if __name__ == "__main__":
    # Permet d'exécuter les tests avec: python test_project.py
    pytest.main([__file__, "-v"])