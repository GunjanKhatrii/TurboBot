"""
Document Chunker
Splits large documents into smaller, searchable chunks
"""

from typing import List, Dict
import re


class DocumentChunker:
    """Split documents into optimal chunks for retrieval"""
    
    def __init__(self, chunk_size: int = 2500, overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk all documents
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of chunk dictionaries
        """
        all_chunks = []
        chunk_id = 0
        
        print(f"\n🔪 Chunking documents (size={self.chunk_size}, overlap={self.overlap})...")
        
        for doc in documents:
            doc_chunks = self.chunk_document(doc, start_chunk_id=chunk_id)
            all_chunks.extend(doc_chunks)
            chunk_id += len(doc_chunks)
            print(f"   ✅ {doc['file_name']}: {len(doc_chunks)} chunks")
        
        print(f"✅ Created {len(all_chunks)} total chunks")
        return all_chunks
    
    def chunk_document(self, document: Dict, start_chunk_id: int = 0) -> List[Dict]:
        """
        Chunk a single document
        
        Args:
            document: Document dictionary
            start_chunk_id: Starting ID for chunks
            
        Returns:
            List of chunks
        """
        chunks = []
        content = document['content']
        
        # Split by sections first
        if document['sections']:
            for section in document['sections']:
                section_chunks = self.chunk_text(
                    text=section['content'],
                    source_file=document['file_name'],
                    source_section=section['title'],
                    start_id=start_chunk_id + len(chunks)
                )
                chunks.extend(section_chunks)
        else:
            # No sections, chunk entire document
            chunks = self.chunk_text(
                text=content,
                source_file=document['file_name'],
                source_section='',
                start_id=start_chunk_id
            )
        
        return chunks
    
    def chunk_text(self, text: str, source_file: str, source_section: str, start_id: int) -> List[Dict]:
        """
        Split text into chunks
        
        Args:
            text: Text to chunk
            source_file: Source filename
            source_section: Section title
            start_id: Starting chunk ID
            
        Returns:
            List of chunks
        """
        if not text.strip():
            return []
        
        chunks = []
        
        # Split into paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(self.create_chunk(
                    content=current_chunk,
                    chunk_id=f"chunk_{start_id + chunk_index:04d}",
                    source_file=source_file,
                    source_section=source_section,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_text = self.get_overlap_text(current_chunk)
                current_chunk = overlap_text + "\n\n" + para if overlap_text else para
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Save final chunk
        if current_chunk.strip():
            chunks.append(self.create_chunk(
                content=current_chunk,
                chunk_id=f"chunk_{start_id + chunk_index:04d}",
                source_file=source_file,
                source_section=source_section,
                chunk_index=chunk_index
            ))
        
        return chunks
    
    def get_overlap_text(self, text: str) -> str:
        """
        Get last N characters for overlap
        
        Args:
            text: Text to get overlap from
            
        Returns:
            Overlap text
        """
        if len(text) <= self.overlap:
            return text
        
        # Get last 'overlap' characters
        overlap_text = text[-self.overlap:]
        
        # Try to start at sentence boundary
        sentence_start = max(
            overlap_text.find('. '),
            overlap_text.find('.\n'),
            overlap_text.find('\n')
        )
        
        if sentence_start > 0:
            overlap_text = overlap_text[sentence_start + 1:].strip()
        
        return overlap_text
    
    def create_chunk(self, content: str, chunk_id: str, source_file: str, 
                    source_section: str, chunk_index: int) -> Dict:
        """
        Create chunk dictionary
        
        Args:
            content: Chunk content
            chunk_id: Unique chunk ID
            source_file: Source filename
            source_section: Section title
            chunk_index: Index in document
            
        Returns:
            Chunk dictionary
        """
        return {
            'chunk_id': chunk_id,
            'content': content.strip(),
            'source_file': source_file,
            'source_section': source_section,
            'chunk_index': chunk_index,
            'char_count': len(content),
            'token_count': self.estimate_tokens(content)
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4


# Test function
if __name__ == "__main__":
    from knowledge_loader import KnowledgeLoader
    
    loader = KnowledgeLoader('data/knowledge_base')
    documents = loader.load_all_documents()
    
    chunker = DocumentChunker(chunk_size=800, overlap=200)
    chunks = chunker.chunk_documents(documents)
    
    print(f"\n📊 Chunking Summary:")
    print(f"Total chunks: {len(chunks)}")
    print(f"Average chunk size: {sum(c['char_count'] for c in chunks) // len(chunks)} chars")
    
    print(f"\n📄 Sample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['source_file']} / {chunk['source_section']}")
        print(f"Size: {chunk['char_count']} chars, ~{chunk['token_count']} tokens")
        print(f"Content preview: {chunk['content'][:200]}...")