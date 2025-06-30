# Plan is for this file to be the one that activates the API - helps with
# modularity and allows for use of other created Python files/modules on retrieved data.

import uvicorn, json, os

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from app.api import app

if __name__ == '__main__':
    uvicorn.run(("app.api:app"), host="0.0.0.0", port=8000, reload=True)