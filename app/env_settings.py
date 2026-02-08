import os

from dotenv import load_dotenv


class EnvSettings:
    """
        The Environment
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("Path to Workspace:", self.base_dir)

        self.environment=os.getenv('ENVIRONMENT', 'development')
        env_path=os.path.join(self.base_dir, f".env.{self.environment}")
        print(f"Loading env from: {env_path}")
        load_dotenv(dotenv_path=env_path, override=True)
    
        self.BACKEND_PATH=os.getenv('BACKEND_PATH')
        self.FRONTEND_PATH=os.getenv('FRONTEND_PATH')
        self.AUDIO_DIR_PATH=os.getenv('AUDIO_DIR_PATH')
        self.AUDIO_CHUNK_SIZE_MB=os.getenv('AUDIO_CHUNK_SIZE_MB')
        self.AUDIO_CHUNK_LIMIT_SECONDS=os.getenv('AUDIO_CHUNK_LIMIT_SECONDS')
        
        self.SECRET_KEY=os.getenv('SECRET_KEY')
        self.ALGORITHM=os.getenv('ALGORITHM') or "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
        self.REFRESH_TOKEN_EXPIRE_MINUTES=os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')        
        
        self.MONGODB_URL = os.getenv('MONGODB_URL')
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
        
        
        

env=EnvSettings()
