"""
Document Retriever
Finds most relevant chunks for a given query
"""

from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TFIDFRetriever:
    """TF-IDF based document retriever"""
    
    def __init__(self):
        """Initialize retriever"""
        self.vectorizer = None
        self.chunk_vectors = None
        self.chunks = []
        self._index_built = False  
        
    def build_index(self, chunks: List[Dict]):
        """
        Build TF-IDF index from chunks
        
        Args:
            chunks: List of chunk dictionaries
        """
        print(f"\n🔍 Building TF-IDF index for {len(chunks)} chunks...")

        if self._index_built:  # ADD THIS CHECK
            print("   ℹ️  Index already built, skipping...")
            return
        
        print(f"\n🔍 Building TF-IDF index for {len(chunks)} chunks...")
        
        self.chunks = chunks
        
        # Extract text from chunks
        chunk_texts = [chunk['content'] for chunk in chunks]
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=2,
            max_df=0.7
        )
        
        # Fit and transform
        self.chunk_vectors = self.vectorizer.fit_transform(chunk_texts)
        
        print(f"✅ Index built: {self.chunk_vectors.shape[0]} chunks, {self.chunk_vectors.shape[1]} features")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve most relevant chunks for query
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of chunks with relevance scores
        """
        if not self.vectorizer or not self.chunks:
            print("⚠️  Warning: Index not built. Call build_index() first.")
            return []
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.chunk_vectors)[0]
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.01:  # Minimum relevance threshold
                chunk = self.chunks[idx].copy()
                chunk['relevance_score'] = float(similarities[idx])
                results.append(chunk)
        
        return results
    
    def search(self, query: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict]:
        """
        Search with filtering
        
        Args:
            query: Search query
            top_k: Number of results
            min_score: Minimum relevance score
            
        Returns:
            Filtered results
        """
        results = self.retrieve(query, top_k=top_k)
        
        # Filter by minimum score
        filtered = [r for r in results if r['relevance_score'] >= min_score]
        
        return filtered


# Test function
if __name__ == "__main__":
    from knowledge_loader import KnowledgeLoader
    from document_chunker import DocumentChunker
    
    # Load and chunk documents
    loader = KnowledgeLoader('data/knowledge_base')
    documents = loader.load_all_documents()
    
    chunker = DocumentChunker(chunk_size=800, overlap=200)
    chunks = chunker.chunk_documents(documents)
    
    # Build index
    retriever = TFIDFRetriever()
    retriever.build_index(chunks)
    
    # Test queries
    test_queries = [
        "What causes high vibration?",
        "bearing failure symptoms",
        "normal operating temperature",
        "oil change procedure",
        "gearbox maintenance cost"
    ]
    
    print(f"\n🔍 Testing retrieval:")
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = retriever.retrieve(query, top_k=2)
        
        for i, result in enumerate(results):
            print(f"\n   Result {i+1} (score: {result['relevance_score']:.3f}):")
            print(f"   Source: {result['source_file']} / {result['source_section']}")
            print(f"   Preview: {result['content'][:150]}...")