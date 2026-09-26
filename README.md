# COPAG Logistics Streamlit

Application Streamlit en français pour l'analyse des données logistiques COPAG.

## Structure

```text
copag_streamlit/
├── app.py
├── copag_logistics.csv
├── requirements.txt
└── README.md
```

## Authentification

Mot de passe de démonstration :

```text
taroudant.copag
```

> Pour une vraie mise en production, il est recommandé de ne pas laisser le mot de passe directement dans `app.py`. Utiliser plutôt `st.secrets`, une variable d'environnement ou un système d'authentification.

## Installation

```bash
python -m venv .venv
```

Windows :

```bash
.venv\Scripts\activate
```

Installation :

```bash
pip install -r requirements.txt
```

Lancement :

```bash
streamlit run app.py
```
