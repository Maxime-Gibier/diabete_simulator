# Utiliser une image Python légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port du service
EXPOSE 8000

# Commande pour démarrer le service
CMD ["python", "main.py"]
