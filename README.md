# 🎙️ Real-Time AI Voice Translator

### *Traduction vocale en temps réel basée sur Google Cloud & IA générative*

Ce projet a été développé dans le cadre du **Hackathon Google Cloud**.
L’objectif : concevoir un **traducteur vocal en temps réel**, capable de reconnaître la parole, de traduire le texte et de synthétiser une voix dans une autre langue, le tout avec **une latence inférieure à 2 secondes**.

Le système combine plusieurs technologies Google Cloud (Speech-to-Text, Translate, Text-to-Speech), de l’audio streaming en Python, ainsi qu'une brique IA générative (Gemini / LLM) pour une traduction enrichie et contextuelle.


## 🎯 Objectifs du projet

### **Objectifs principaux**

* Traduire la voix **en temps réel** dans plusieurs langues.
* Exploiter :

  * **Speech-to-Text** (transcription vocale)
  * **Translation** (traduction textuelle)
  * **Text-to-Speech** (synthèse vocale)
* Utiliser Google **Vertex AI / Gemini** pour contextualiser les traductions.

### **Objectifs secondaires**

* Diffuser les traductions vers des appareils externes (casques, haut-parleurs).
* Fournir un retour éducatif :

  * Corrections de diction
  * Indications grammaticales
* Proposer une interface utilisateur simple (UI Web ou Python).


## 🧠 Innovations

* Utilisation des modèles **Gemini / Vertex AI** pour donner du contexte aux traductions complexes.
* Détection dynamique des silences pour optimiser les performances.
* Architecture de pipeline parallèle pour maintenir une latence très basse.
* Interface utilisateur interactive (via `ui.py`).


## 🏗️ Architecture du système

### Pipeline principal

```
🎤 Capture Audio
       ↓
🗣️ Speech-to-Text (Google Cloud)
       ↓
🌐 Translation API
       ↓
🤖 (optionnel) IA générative Gemini → Traduction enrichie
       ↓
🔊 Text-to-Speech
       ↓
🎧 Restitution audio
```

### Communication interne

* Chaque module communique via une **file d’attente (queue)**.
* Un système de **pipeline parallèle** traite les étapes simultanément.
* Redémarrage automatique en cas de silence prolongé ou d’erreurs réseau.


## 🛠️ Technologies utilisées

### **Google Cloud APIs**

* `speech_v1p1beta1.SpeechClient` — Speech-to-Text
* `translate_v2.TranslateClient` — Traduction
* `texttospeech.TextToSpeechClient` — Synthèse vocale
* `Vertex AI / Gemini` — IA générative (contextualisation)

### **Python**

* `sounddevice` → capture et lecture audio
* `numpy` → traitement des données audio
* `queue` → pipeline parallèle
* `html` → décodage de caractères spéciaux

### **Frontend**

* HTML / CSS / JavaScript (UI)
* ou application Python (`ui.py`)


## 📦 Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
```

### 2. L’activer

Windows :

```bash
.\venv\Scripts\activate
```

macOS / Linux :

```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install google-cloud-speech google-cloud-translate google-cloud-texttospeech sounddevice numpy
```

---

## 🔧 Configuration Google Cloud

1. Activer ces APIs :

   * **Speech-to-Text API**
   * **Cloud Translation API**
   * **Text-to-Speech API**
   * (optionnel) **Vertex AI API**

2. Créer un **compte de service**

3. Télécharger le fichier JSON de clés

4. Exporter la variable d’environnement :

```bash
export GOOGLE_APPLICATION_CREDENTIALS="chemin/vers/cle.json"
```


## ▶️ Exécution du projet

### Lancer l’interface utilisateur :

```bash
python ui.py
```

### Lancer le traducteur vocal directement :

```bash
python translator.py
```


## 📊 Exigences techniques & performances

* **Latence totale** : < 2 secondes (voix → texte → traduction → voix)
* Gestion robuste des flux audio, même en cas d’interruptions
* Support multilingue (choix langue d’entrée / sortie)
* Compatibilité avec plusieurs périphériques audio


## 🔐 Exigences non-fonctionnelles

### **Sécurité**

* Aucun flux audio n’est enregistré sans consentement.
* Traitement réalisé dans un environnement Google Cloud sécurisé.

### **Accessibilité**

* Interface adaptée aux handicaps visuels ou auditifs.

### **Robustesse**

* Résilience aux erreurs réseau et coupures audio.


## 🧪 Plan de tests

### **Tests unitaires**

* Qualité de transcription (phrases courtes & longues)
* Fiabilité de la traduction (expressions complexes)

### **Tests d’intégration**

* Mesure de la latence du pipeline
* Simulations de coupures réseau

### **Tests utilisateurs**

* Fluidité générale
* Clarté et pertinence des traductions


## 🚀 Améliorations futures

* Intégration complète avec **Gemini** pour des traductions encore plus humaines.
* Version mobile (Android / iOS).
* Déploiement sur appareil embarqué (Raspberry Pi + micro).
* Mode transcription collaborative à distance.
* Support pour les dialectes régionaux.


## 👤 Auteur

**Alex Alkhatib**
Projet réalisé dans le cadre du **Google Cloud Hackathon**.


## 📄 Licence
MIT License
Copyright (c) 2025 Alex Alkhatib
