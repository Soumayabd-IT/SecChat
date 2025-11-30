# modules/chatbot_engine.py

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Désactiver la télémétrie ChromaDB
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from huggingface_hub import InferenceClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import logging

# ------------------ Configuration ------------------ #
CHROMA_PATH = "chroma"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_API_KEY = os.getenv("HF_API_KEY")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Template simplifié
prompt_template = """Tu es un expert en cybersécurité. Réponds de manière claire et technique.

Contexte:
{context}

Question: {question}

Réponse:"""

# ------------------ Client Hugging Face ------------------ #
client = None


def initialize_client():
    """Initialise le client avec la nouvelle API"""
    global client

    if not HF_API_KEY:
        logger.error("❌ HF_API_KEY non définie")
        return False

    try:
        # Initialiser le client
        client = InferenceClient(token=HF_API_KEY)

        # Test avec chat_completion (au lieu de text_generation)
        logger.info("🔄 Test de connexion avec Qwen...")
        test_messages = [{"role": "user", "content": "Hello"}]
        test_response = client.chat_completion(
            messages=test_messages,
            model="Qwen/Qwen2.5-72B-Instruct",
            max_tokens=5
        )

        logger.info("✅ Client initialisé avec succès")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur d'initialisation : {str(e)}")
        client = None
        return False


# ------------------ Fonction principale ------------------ #
def answer_question(query_text, k=3):
    """
    Répond à une question en utilisant RAG + LLM

    Args:
        query_text (str): La question de l'utilisateur
        k (int): Nombre de documents à récupérer

    Returns:
        tuple: (réponse, sources)
    """

    if not client:
        logger.error("Client non initialisé")
        if not initialize_client():
            return "❌ Impossible de se connecter à l'API Hugging Face.", []

    try:
        # 1️⃣ Recherche dans ChromaDB
        logger.info("🔍 Recherche dans la base de connaissances...")
        embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embedding_function
        )

        # 2️⃣ Récupération des documents
        results = db.similarity_search_with_relevance_scores(query_text, k=k)

        if not results:
            logger.warning("⚠️ Aucun document trouvé")
            return "Aucun document pertinent trouvé.", []

        logger.info(f"📚 {len(results)} documents trouvés")

        # 3️⃣ Construction du prompt
        context_text = "\n---\n".join([doc.page_content for doc, _ in results])
        prompt = prompt_template.format(context=context_text, question=query_text)

        # 4️⃣ Génération avec chat_completion (format conversationnel)
        logger.info("🤖 Génération de la réponse...")

        # Liste de modèles gratuits disponibles
        models_to_try = [
            "Qwen/Qwen2.5-72B-Instruct",
            "meta-llama/Llama-3.2-3B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "microsoft/Phi-3.5-mini-instruct"
        ]

        response_text = None
        for model_name in models_to_try:
            try:
                logger.info(f"   Essai avec {model_name}...")

                # Format de messages pour chat
                messages = [
                    {"role": "system",
                     "content": "Tu es un expert en cybersécurité. Réponds de manière claire et technique."},
                    {"role": "user", "content": f"Contexte:\n{context_text}\n\nQuestion: {query_text}"}
                ]

                response = client.chat_completion(
                    messages=messages,
                    model=model_name,
                    max_tokens=300,
                    temperature=0.3
                )

                # Extraire le contenu de la réponse
                response_text = response.choices[0].message.content
                logger.info(f"   ✅ Réponse obtenue avec {model_name}")
                break

            except Exception as e:
                logger.warning(f"   ⚠️ {model_name} non disponible: {str(e)[:80]}")
                continue

        if not response_text:
            return "❌ Aucun modèle disponible actuellement. Réessaye dans quelques minutes.", []

        # 5️⃣ Nettoyage
        response_text = response_text.strip()

        # 6️⃣ Sources
        sources = []
        for doc, score in results:
            source = doc.metadata.get("source", "Inconnu")
            sources.append(f"{source} (score: {score:.2f})")

        logger.info("✅ Réponse générée")

        del db
        return response_text, sources

    except Exception as e:
        logger.error(f"❌ Erreur : {str(e)}")
        return f"❌ Erreur : {str(e)}", []


# ------------------ Initialisation ------------------ #
logger.info("🚀 Démarrage du chatbot...")
initialize_client()

# ------------------ Test ------------------ #
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🤖 CHATBOT RAG CYBERSÉCURITÉ - MODÈLES GRATUITS")
    print("=" * 70)

    if not HF_API_KEY:
        print("\n❌ HF_API_KEY non définie !")
        print("\n📝 Crée un fichier .env avec:")
        print("   HF_API_KEY=hf_ton_token_ici")
        print("\nOu récupère un token sur: https://huggingface.co/settings/tokens")
        print("=" * 70)
        exit(1)

    if not client:
        print("\n❌ Client non initialisé.")
        print("Vérifie ta connexion internet et ta clé API.\n")
        exit(1)

    question = "Quels sont les principaux risques d'une injection SQL ?"

    print(f"\n🔍 Question : {question}")
    print("⏳ Génération en cours...\n")

    answer, sources = answer_question(question)

    print("✅ RÉPONSE :")
    print("-" * 70)
    print(answer)
    print("-" * 70)

    if sources:
        print("\n📚 SOURCES :")
        for i, source in enumerate(sources, 1):
            print(f"   {i}. {source}")

    print("\n" + "=" * 70)
    print("✨ Terminé !")
    print("=" * 70 + "\n")