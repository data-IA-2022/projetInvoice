# projetInvoice
Mise à disposition des factures

# Shéma de la BDD utilisée
![schema.png](schema.png)

# Installation
```bash
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
```

# Run local
```bash
 source venv/bin/activate
 UVICORN_PORT=3000 SECRET=EGo uvicorn main:app --host 0.0.0.0 --reload
```
Accès au swagger:
