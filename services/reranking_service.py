from sentence_transformers import CrossEncoder
import torch

class RerankerService:
    def __init__(self):
        """
            Uses the 'CrossEncoder' from 'sentence_transformers'.
            'torch.nn.Sigmoid' was used to convert the rerank scores in a range from 0-1.
        """
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2",
                                  activation_fn=torch.nn.Sigmoid()
                                  )
    
    def rerank(self, query, matches):
        """
            Predicts the score for each chunk text against the query. 
            The score is then stored within each chunk.
            Finally all chunks are sorted using the scores in the descreasing order.
            The top 3 chunks are returned.
        """
        for id, match in matches.items():
            matches[id]["rerank_score"] = float(self.model.predict((query, match["text"])))

        return sorted( matches.values(), key=lambda x: x["rerank_score"], reverse=True )[:3]