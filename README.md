Dishcovery: Restaurant Recommender

The project's branch is the GNN branch.

Dishcovery – Intelligent Restaurant Recommendation App
Description

Dishcovery is an intelligent restaurant-recommendation application developed as part of an AI/ML project.
It learns user preferences, understands natural-language queries, and recommends the most relevant restaurants using a combination of two specialized Graph Neural Networks (GNNs) and conversational AI.

More precisely:

A Link Prediction GNN estimates how likely a user is to enjoy a restaurant they haven’t visited yet.

A Label Prediction GNN classifies interactions as like or dislike to refine user taste modeling.

Together, they power a personalized and adaptive recommendation engine.

Table of Contents

Initialization

Project Structure

Prerequisites

Installation

Usage

System Architecture

Data

Contributors

1. Initialization
1.1 Project Structure

The project is composed of three main components:

PROJECT/
├── frontend/
│   └── app.py
├── services/
│   ├── data_service/
│   └── recommender_service/
├── models/
│   ├── link_pred.pth         # Link Prediction GNN
│   └── label_pred.pth        # Label Prediction GNN
├── data/
│   └── (processed restaurant datasets)
├── requirements.txt
└── README.md

1.2 Prerequisites

Python 3.9+

Required libraries in requirements.txt

Optional GPU support for faster inference

Internet access for certain API operations

1.3 Installation
python -m venv venv
pip install -r requirements.txt

2. Usage
Start the Data Service (port 8001)
uvicorn services.data_service.main:app --reload --port 8001

Start the Recommender Service (port 8000)
uvicorn services.recommender_service.main:app --reload --port 8000

Start the Streamlit App
streamlit run frontend/app.py


Open:

http://localhost:8501

3. System Architecture

Dishcovery integrates multiple AI components working together:

1. Graph-Based User Preference Modeling

The system uses two complementary Graph Neural Networks:

🔹 Link Prediction GNN

Predicts how likely a user is to enjoy a given restaurant.
This model captures structural patterns such as:

user similarity

restaurant similarity

interaction intensity

It powers the core recommendation engine.

🔹 Label Prediction GNN (Like/Dislike)

Predicts the type of interaction (positive or negative).
This helps the system refine personalization based on explicit user feedback.

2. NLP-Powered Smart Search

Users can simply describe the type of dining experience they want:

“A romantic Italian place”
“A cheap sushi restaurant near downtown”

Dishcovery interprets the query, retrieves relevant restaurants, and ranks them using the two GNN models.

4. Data

The dataset contains:

Restaurant metadata

Location and categories

Ratings and reviews

User–restaurant interactions (likes/dislikes)

Graph-ready representations for GNN training

Additional processed data supports:

Cold-start handling

Semantic filtering

Graph construction

5. Contributors

Augustin Samier

Inthushan Suthakaran

Aurélien Verdier

Victor Lei
Benkamin Auer
