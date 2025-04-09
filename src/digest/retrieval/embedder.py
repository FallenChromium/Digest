from torch.nn import functional as F
from sentence_transformers import SentenceTransformer

class Embedder:
    """Sentence embedding model with Matryoshka support for single text inputs."""
    
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1.5") -> None:
        """Initialize the embedding model.
        
        Args:
            model_name: Name of the SentenceTransformer model to load
        """
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
    
    def embed_query(self, text: str, matryoshka_dim: int = 768) -> list[float]:
        """Embed a search query with appropriate prefixing.
        
        Args:
            text: Input text to embed
            matryoshka_dim: Dimension for Matryoshka truncation
        """
        return self._process(text, "search_query: ", matryoshka_dim)
    
    def embed_document(self, text: str, matryoshka_dim: int = 768) -> list[float]:
        """Embed a document with appropriate prefixing.
        
        Args:
            text: Input text to embed
            matryoshka_dim: Dimension for Matryoshka truncation
        """
        return self._process(text, "search_document: ", matryoshka_dim)
    
    def _process(self, text: str, prefix: str, matryoshka_dim: int) -> list[float]:
        """Internal processing pipeline for single text inputs."""
        prefixed_text = f"{prefix}{text}"
        embeddings = self.model.encode([prefixed_text], convert_to_tensor=True)
        embeddings = F.layer_norm(embeddings, normalized_shape=(embeddings.size(-1),))
        embeddings = embeddings[:, :matryoshka_dim]
        embeddings = F.normalize(embeddings, p=2, dim=-1)
        return embeddings.squeeze(0).tolist()


embedder = Embedder()

# if __name__ == "__main__":
#     # Example usage
#     embedder = Embedder()
    
#     query = "What is TSNE?"
#     document = "t-SNE (t-Distributed Stochastic Neighbor Embedding) is a dimensionality reduction technique used for visualizing high-dimensional data."
    
#     query_embed = embedder.embed_query(query)
#     doc_embed = embedder.embed_document(document, matryoshka_dim=256)
    
#     print(f"Query embedding shape: {query_embed.shape}")  # torch.Size([128])
#     print(f"Document embedding shape: {doc_embed.shape}")  # torch.Size([256])
#     print(f"Similarity score: {torch.dot(query_embed, doc_embed[:128]).item():.3f}")