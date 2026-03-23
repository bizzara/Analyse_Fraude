# 🚀 Projet Final – Détection de Fraude Financière

## 📁 Fichiers du projet

| Fichier | Description |
|---|---|
| `analyse_fraude.ipynb` | Notebook complet (Pandas, Matplotlib, Seaborn, Plotly) |
| `app.py` | Application Streamlit interactive |
| `Dataset.csv` | Jeu de données (2000 transactions) |
| `requirements.txt` | Dépendances Python |

---

## ⚙️ Installation & Lancement en local

```bash
# 1. Cloner / télécharger le projet
# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le dashboard
streamlit run app.py
```

L'application s'ouvre automatiquement sur http://localhost:8501

---

## ☁️ Déploiement sur Streamlit Cloud

1. Créer un compte sur [share.streamlit.io](https://share.streamlit.io)
2. Connecter votre dépôt GitHub contenant les fichiers du projet
3. Sélectionner `app.py` comme fichier principal
4. Cliquer sur **Deploy** → l'URL publique est générée automatiquement

> ⚠️ Assurez-vous que `Dataset.csv` est présent dans le même dépôt que `app.py`

---

## 📊 Contenu du Notebook

1. **Exploration & Préparation** – chargement, inspection, nettoyage, feature engineering
2. **Analyse statique** – Matplotlib & Seaborn (distributions, boxplots, heatmap, camemberts)
3. **Analyse interactive** – Plotly Express (scatter, sunburst, timeline, barres empilées)

---

## 🔍 Principales conclusions

- **2 000 transactions** sur novembre 2018, dont **6 fraudes (0,3%)**
- Catégorie dominante : **airtime** ; montants les plus élevés : **financial_services**
- Canal principal : **ChannelId_3**
- Pic d'activité : **0h–6h du matin**
- Forte corrélation **Amount ↔ Value** ; les montants négatifs = remboursements
