from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Configs(BaseSettings):
    BOT_TOKEN: str
    DB_URI: str = "sqlite:///db.db"


configs = Configs()
