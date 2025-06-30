import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

from pprint import pprint
from pathlib import Path

envPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

class BackendSettings(BaseSettings):
    type: str = Field(..., alias='FASTAPI_FIREBASE_TYPE')
    project_id: str = Field(..., alias='FASTAPI_FIREBASE_PROJECT_ID')
    private_key_id: str = Field(..., alias='FASTAPI_FIREBASE_API_KEY_ID')
    private_key: str = Field(..., alias='FASTAPI_FIREBASE_PRIVATE_API_KEY')
    client_email: str = Field(..., alias='FASTAPI_FIREBASE_CLIENT_EMAIL')
    client_id: str = Field(..., alias='FASTAPI_FIREBASE_CLIENT_ID')
    auth_uri: str = Field(..., alias='FASTAPI_FIREBASE_AUTH_URI')
    token_uri: str = Field(..., alias='FASTAPI_FIREBASE_TOKEN_URI')
    auth_provider_x509_cert_url: str = Field(..., alias='FASTAPI_FIREBASE_AUTH_PROVIDER_CERT')
    client_x509_cert_url: str = Field(..., alias='FASTAPI_FIREBASE_CLIENT_PROVIDER_CERT')
    universe_domain: str = Field(..., alias='FASTAPI_FIREBASE_UNIVERSE_DOMAIN')

    model_config = SettingsConfigDict(env_file=envPath, populate_by_name=True, extra='ignore')

@lru_cache
def getSettings():
    return BackendSettings()

settings = getSettings()

