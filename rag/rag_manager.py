"""
RAG Manager
Orchestrates the entire RAG system
"""

from typing import List, Dict, Optional
import os
from .knowledge_loader import KnowledgeLoader
from .document_chunker import DocumentChunker
from .retriever import TFIDFRetriever


class RAGManager:
    """Main RAG system orchestrator"""
    
    def __init__(self, knowledge_base_path: str = 'data/knowledge_base'):
        """
        Initialize RAG Manager
        
        Args:
            knowledge_base_path: Path to knowledge base folder
        """
        self.knowledge_base_path = knowledge_base_path
        self.loader = KnowledgeLoader(knowledge_base_path)
        self.chunker = DocumentChunker(chunk_size=2500, overlap=50)
        self.retriever = TFIDFRetriever()
        
        self.documents = []
        self.chunks = []
        self.initialized = False
    
    def initialize(self):
        """
        Initialize RAG system - call this once at startup
        """
        print("\n" + "="*60)
        print("🚀 Initializing RAG System for TurboBot")
        print("="*60)
        
        try:
            # Step 1: Load documents
            self.documents = self.loader.load_all_documents()
            
            if not self.documents:
                print("⚠️  Warning: No documents loaded. RAG will not be available.")
                return False
            
            # Step 2: Chunk documents
            self.chunks = self.chunker.chunk_documents(self.documents)
            
            if not self.chunks:
                print("⚠️  Warning: No chunks created. RAG will not be available.")
                return False
            
            # Step 3: Build retrieval index
            self.retriever.build_index(self.chunks)
            
            # Success!
            self.initialized = True
            
            # Print summary
            print("\n" + "="*60)
            print("✅ RAG System Initialized Successfully!")
            print("="*60)
            print(f"📚 Documents loaded: {len(self.documents)}")
            print(f"🔪 Chunks created: {len(self.chunks)}")
            print(f"💾 Total knowledge: {sum(d['char_count'] for d in self.documents):,} characters")
            print(f"🎯 System ready for intelligent retrieval!")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error initializing RAG system: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def retrieve_context(self, query: str, top_k: int = 3, min_score: float = 0.05) -> str:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            min_score: Minimum relevance score
            
        Returns:
            Formatted context string for LLM
        """
        if not self.initialized:
            return ""
        
        try:
            # Retrieve relevant chunks
            results = self.retriever.search(query, top_k=top_k, min_score=min_score)
            
            if not results:
                return ""
            
            # Format for LLM
            formatted_context = self.format_for_llm(results)
            
            return formatted_context
            
        except Exception as e:
            print(f"⚠️  Error retrieving context: {str(e)}")
            return ""
    
    def format_for_llm(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks for LLM consumption
        
        Args:
            chunks: List of retrieved chunks with scores
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = ["RELEVANT KNOWLEDGE FROM MAINTENANCE MANUALS:\n"]
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"\n[Source {i}: {chunk['source_file']}]")
            
            if chunk['source_section']:
                context_parts.append(f"[Section: {chunk['source_section']}]")
            
            context_parts.append(f"[Relevance: {chunk['relevance_score']:.2f}]\n")
            context_parts.append(chunk['content'])
            context_parts.append("\n" + "-"*60)
        
        context_parts.append("\nIMPORTANT: Use the above knowledge to provide accurate, specific answers. Cite sources when using this information.")
        
        return "\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """
        Get RAG system statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'initialized': self.initialized,
            'knowledge_base_path': self.knowledge_base_path,
            'documents_loaded': len(self.documents),
            'total_chunks': len(self.chunks),
            'total_characters': sum(d['char_count'] for d in self.documents) if self.documents else 0,
            'document_files': [d['file_name'] for d in self.documents]
        }
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search knowledge base (for debugging/testing)
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of results with metadata
        """
        if not self.initialized:
            return []
        
        results = self.retriever.search(query, top_k=top_k)
        
        # Simplify output
        simplified = []
        for r in results:
            simplified.append({
                'source_file': r['source_file'],
                'source_section': r['source_section'],
                'relevance_score': round(r['relevance_score'], 3),
                'content_preview': r['content'][:200] + '...' if len(r['content']) > 200 else r['content']
            })
        
        return simplified
    
    def reload_knowledge_base(self):
        """
        Reload knowledge base (useful if documents are updated)
        """
        print("\n🔄 Reloading knowledge base...")
        return self.initialize()


# Test function
if __name__ == "__main__":
    # Initialize RAG
    rag = RAGManager('data/knowledge_base')
    success = rag.initialize()
    
    if not success:
        print("❌ Failed to initialize RAG")
        exit(1)
    
    # Print stats
    stats = rag.get_stats()
    print(f"\n📊 RAG Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test queries
    test_queries = [
        "What causes bearing failure?",
        "How to detect high vibration?",
        "Normal operating temperature for gearbox",
        "When should I change the oil?",
        "Cost of bearing replacement"
    ]
    
    print(f"\n🔍 Testing RAG Retrieval:\n")
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        context = rag.retrieve_context(query, top_k=2)
        
        if context:
            print(context)
        else:
            print("No relevant context found.")
    
    # Test search function
    print(f"\n\n🔍 Testing Search Function:")
    results = rag.search_knowledge("vibration analysis", top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {result['source_file']}")
        print(f"Section: {result['source_section']}")
        print(f"Score: {result['relevance_score']}")
        print(f"Preview: {result['content_preview']}")