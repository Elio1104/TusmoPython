import sys
import os
from pathlib import Path

# Ajout du dossier serverV2 au path pour les imports src.*
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from src.server import app
from src.core.conf import SERV_IP, SERV_PORT

if __name__ == "__main__":
    print(f"[SERVER] Démarrage sur http://{SERV_IP}:{SERV_PORT}")
    uvicorn.run(app, host=SERV_IP, port=SERV_PORT)
