from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddingsGenerator:
    """
    A class to generate embeddings using SentenceTransformer model.
    Possible Model Names:
    - 'sentence-transformers/paraphrase-MiniLM-L6-v2'
    - 'sentence-transformers/all-MiniLM-L6-v2'
    - 'sentence-transformers/all-mpnet-base-v2'
    - 'sentence-transformers/multi-qa-mpnet-base-dot-v1'

    Example:
        generator = SentenceTransformerEmbeddingsGenerator('sentence-transformers/paraphrase-MiniLM-L6-v2')
        embeddings = generator.generate_embeddings(['text1', 'text2'])
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, sentences):
        return self.model.encode(sentences)
    