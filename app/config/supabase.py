from supabase import create_client, Client
from app.config.env_config import get_settings
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()
settings = get_settings()

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)

engine = create_engine(settings.DATABASE_URL, echo=False)