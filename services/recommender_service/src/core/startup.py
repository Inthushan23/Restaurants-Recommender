from fastapi import FastAPI

# models
from .config import LINK_PRED_MODEL, EDGE_PRED_MODEL
from ..domain.gnn.gnn_edge_predictor import GNNEdgeLabelPredictor
from ..domain.gnn.gnn_link_predictor import GNNLinkPredictor 



def load_models(app: FastAPI):
    link_pred = GNNLinkPredictor(in_channels= app.state.graph.x.size(1), hidden_channels=512, out_channels=256).load(LINK_PRED_MODEL)
    link_pred.eval()

    edge_pred = GNNEdgeLabelPredictor(in_channels=app.state.graph_with_labels.num_node_features, hidden_channels=128, out_channels=64).load(EDGE_PRED_MODEL)
    edge_pred.eval()

    app.state.link_pred = link_pred
    app.state.edge_pred = edge_pred


