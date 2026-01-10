"""
Knowledge Base Document Loader
Loads and parses turbine maintenance documents
"""

import os
from typing import List, Dict
from datetime import datetime


class KnowledgeLoader:
    """Load and parse knowledge base documents"""
    
    def __init__(self, knowledge_base_path: str):
        """
        Initialize knowledge loader
        
        Args:
            knowledge_base_path: Path to knowledge base folder
        """
        self.knowledge_base_path = knowledge_base_path
        
    def load_all_documents(self) -> List[Dict]:
        """
        Load all documents from knowledge base
        
        Returns:
            List of document dictionaries
        """
        documents = []
        
        if not os.path.exists(self.knowledge_base_path):
            print(f"⚠️  Warning: Knowledge base path not found: {self.knowledge_base_path}")
            return documents
        
        # Get all .txt files
        txt_files = [f for f in os.listdir(self.knowledge_base_path) if f.endswith('.txt')]
        
        if not txt_files:
            print(f"⚠️  Warning: No .txt files found in {self.knowledge_base_path}")
            return documents
        
        print(f"📚 Loading {len(txt_files)} documents from knowledge base...")
        
        for filename in sorted(txt_files):
            file_path = os.path.join(self.knowledge_base_path, filename)
            try:
                doc = self.parse_document(file_path)
                documents.append(doc)
                print(f"   ✅ Loaded: {filename} ({len(doc['content'])} chars)")
            except Exception as e:
                print(f"   ❌ Error loading {filename}: {str(e)}")
        
        print(f"✅ Successfully loaded {len(documents)} documents")
        return documents
    
    def parse_document(self, file_path: str) -> Dict:
        """
        Parse a single document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Document dictionary with metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract filename
        filename = os.path.basename(file_path)
        
        # Extract title (first non-empty line)
        lines = content.split('\n')
        title = ''
        for line in lines:
            if line.strip():
                title = line.strip()
                break
        
        # Get file stats
        stats = os.stat(file_path)
        
        # Parse sections
        sections = self.get_document_sections(content)
        
        return {
            'file_name': filename,
            'file_path': file_path,
            'title': title,
            'content': content,
            'sections': sections,
            'size': stats.st_size,
            'last_modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'line_count': len(lines),
            'char_count': len(content)
        }
    
    def get_document_sections(self, content: str) -> List[Dict]:
        """
        Extract sections from document
        
        Args:
            content: Document text
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            # Detect section headers (all caps, or underlined with ===)
            is_header = False
            
            # Check for all-caps headers
            if line.strip() and line.strip().isupper() and len(line.strip()) > 3:
                is_header = True
            
            # Check for underlined headers (next line is === or ---)
            if line.strip() and set(line.strip()) in [{'='}, {'-'}] and len(line.strip()) > 3:
                # Previous line is the header
                if current_content:
                    # Save previous section
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'content': '\n'.join(current_content[:-1]).strip()  # Exclude the header line
                        })
                    # Start new section
                    current_section = current_content[-1].strip()
                    current_content = []
                continue
            
            if is_header:
                # Save previous section
                if current_section and current_content:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                # Start new section
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        return sections


# Test function
if __name__ == "__main__":
    loader = KnowledgeLoader('data/knowledge_base')
    documents = loader.load_all_documents()
    
    print(f"\n📊 Summary:")
    print(f"Total documents: {len(documents)}")
    
    for doc in documents:
        print(f"\n📄 {doc['file_name']}")
        print(f"   Title: {doc['title']}")
        print(f"   Size: {doc['char_count']:,} characters")
        print(f"   Sections: {len(doc['sections'])}")
        if doc['sections']:
            print(f"   First section: {doc['sections'][0]['title']}")