import uuid
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(r"services\data_service\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(user_id: str, name: str):
    # Vérifier si l'utilisateur existe déjà
    existing = supabase.table("users") \
        .select("") \
        .eq("user_id", user_id) \
        .execute()

    if existing.data:
        return {
            "success": False,
            "error": f"L'utilisateur '{user_id}' existe déjà."
        }

    # Si non, création avec le nom
    response = supabase.table("users").insert({
        "user_id": user_id,
        "name": name
    }).execute()

    return {
        "success": True,
        "data": response.data
    }
def check_mdp(user_id: str, mdp: int) -> bool:
    response = supabase.table("mdp") \
        .select("") \
        .eq("user_id", user_id) \
        .eq("mdp", mdp) \
        .execute()

    return len(response.data) > 0


def create_mdp(user_id: str, mdp: int):
    # Vérifier si l'utilisateur a déjà un mdp dans la table
    existing = supabase.table("mdp") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    if existing.data:
        return {
            "success": False,
            "error": f"L'utilisateur '{user_id}' possède déjà un mdp."
        }

    # Générer automatiquement un mdp_id unique
    mdp_id = str(uuid.uuid4())

    # Insérer le nouveau MDP
    response = supabase.table("mdp").insert({
        "mdp_id": mdp_id,
        "user_id": user_id,
        "mdp": mdp
    }).execute()

    return {
        "success": True,
        "data": response.data
    } 