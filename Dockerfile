# Base de l'image: linux + python 3.8
FROM python:3.8-slim-buster
# Création de répertoire /code dans l'image (pas en local)
WORKDIR /code
# Copie requirements local -> image
COPY requirements.txt requirements.txt
# Installation des librairies dans l'image
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# Copie de tous les fichiers (sauf ceux défini dans .dockerignore) -> image
COPY . /code
# Mon service sera disponible sur le port 8000
EXPOSE 80
# Définition du code python qui va s'executer dans l'instance qui sera crée
CMD ["uvicorn", "main:app", "--port", "80", "--host", "0.0.0.0"]
