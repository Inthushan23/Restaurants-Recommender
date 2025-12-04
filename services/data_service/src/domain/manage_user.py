import uuid
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone

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



def check_mdp(user_id: str, mdp: int) -> bool:
    response = supabase.table("mdp") \
        .select("") \
        .eq("user_id", user_id) \
        .eq("mdp", mdp) \
        .execute()

    return len(response.data) > 0



def user_exists(user_id: str) -> bool:
    try:
        resp = supabase.table("users").select("user_id").eq("user_id", user_id).limit(1).execute()
        return len(resp.data) > 0
    except Exception as e:
        print("error:", e)
        return False

def business_exists(business_id: str) -> bool:
    try:
        resp = supabase.table("business").select("business_id").eq("business_id", business_id).limit(1).execute()
        return len(resp.data) > 0
    except Exception as e:
        print("error", e)
        return False

def add_or_update_review(user_id: str, business_id: str, like: bool) -> bool:
    # Vérif User
    if not user_exists(user_id):
        print(f"user_id doesn't exist: {user_id}")
        return False

    # Vérif Business
    if not business_exists(business_id):
        print(f"restaurant doesn't exist: {business_id}")
        return False

    stars = 5 if like else 0

    try:
        existing = (
            supabase.table("reviews")
            .select("review_id")
            .eq("user_id", user_id)
            .eq("business_id", business_id)
            .limit(1)
            .execute()
        )
    except Exception as e:
        print("error check review:", e)
        return False

    #Si la review existe : update stars
    if existing.data:
        review_id = existing.data[0]["review_id"]

        try:
            supabase.table("reviews") \
                .update({"stars": stars}) \
                .eq("review_id", review_id) \
                .execute()

            print(f"edit review : {review_id}, stars={stars}")
            return True

        except Exception as e:
            print("error update review:", e)
            return False

    # créer une nouvelle review
    else:
        review_id = str(uuid.uuid4())
        actualdate = datetime.now(timezone.utc).isoformat()

        record = {
            "review_id": review_id,
            "user_id": user_id,
            "business_id": business_id,
            "stars": stars,
            "text": "",
            "date": actualdate
        }

        try:
            supabase.table("reviews").insert(record).execute()
            print("review added :", record)
            return True

        except Exception as e:
            print("error :", e)
            return False