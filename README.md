# projetInvoice
Mise à disposition des factures

# Shéma de la BDD utilisée
![schema.png](schema.png)

# Installation (linux)
```bash
 python3 -m venv venv
 source venv/bin/activate
 # Windows : 
 # . venv/Scripts/activate
 pip install -r requirements.txt
```

# Remplissage de la BDD (à partir de Faker)
```bash
source ../venv/bin/activate
python3 fillDB.py > invoice.sql
rm invoice.sqlite
time sqlite3 invoice.sqlite < invoice.sql
ll invoice.sqlite
```


# Run local
```bash
 source venv/bin/activate
 UVICORN_PORT=8000 SECRET=EGo uvicorn main:app --host 0.0.0.0 --reload
```
Accès au swagger: http://localhost:8000/docs

# Création image docker

```bash
 docker build -t projetinvoice .
 docker rm -f projetinvoice
 docker run -d --name projetinvoice -p 8000:8000 projetinvoice
```
