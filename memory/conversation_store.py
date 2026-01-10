"""
Conversation Storage
Stores and retrieves conversation history
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ConversationStore:
    """Stores conversation history persistently"""
    
    def __init__(self, storage_path: str = 'data/conversations'):
        """
        Initialize conversation store
        
        Args:
            storage_path: Path to store conversation files
        """
        self.storage_path = storage_path
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
        print(f"💾 Conversation store: {storage_path}")
    
    def create_session(self) -> str:
        """
        Create a new conversation session
        
        Returns:
            session_id: Unique identifier for this session
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "metadata": {
                "total_messages": 0,
                "turbine_queries": 0
            }
        }
        
        self._save_session(session_id, session_data)
        
        print(f"✅ Created session: {session_id}")
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, 
                   metadata: Optional[Dict] = None):
        """
        Add a message to the conversation
        
        Args:
            session_id: Session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (turbine data, etc.)
        """
        session = self._load_session(session_id)
        
        if not session:
            print(f"⚠️  Session {session_id} not found, creating new one")
            session = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "metadata": {"total_messages": 0, "turbine_queries": 0}
            }
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        session["messages"].append(message)
        session["metadata"]["total_messages"] = len(session["messages"])
        
        if role == "user":
            session["metadata"]["turbine_queries"] += 1
        
        self._save_session(session_id, session)
    
    def get_conversation(self, session_id: str, last_n: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history
        
        Args:
            session_id: Session identifier
            last_n: Return only last N messages (None = all)
        
        Returns:
            List of messages
        """
        session = self._load_session(session_id)
        
        if not session:
            return []
        
        messages = session.get("messages", [])
        
        if last_n:
            return messages[-last_n:]
        
        return messages
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get list of all conversation sessions
        
        Returns:
            List of session summaries
        """
        sessions = []
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                session_id = filename.replace('.json', '')
                session = self._load_session(session_id)
                
                if session:
                    summary = {
                        "session_id": session_id,
                        "created_at": session.get("created_at"),
                        "total_messages": session.get("metadata", {}).get("total_messages", 0),
                        "turbine_queries": session.get("metadata", {}).get("turbine_queries", 0),
                        "last_message": session["messages"][-1]["content"][:100] if session.get("messages") else ""
                    }
                    sessions.append(summary)
        
        # Sort by creation date (newest first)
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        
        return sessions
    
    def search_conversations(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search through conversation history
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of matching messages with context
        """
        query_lower = query.lower()
        results = []
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                session_id = filename.replace('.json', '')
                session = self._load_session(session_id)
                
                if not session:
                    continue
                
                for i, message in enumerate(session.get("messages", [])):
                    if query_lower in message["content"].lower():
                        # Include context (previous and next message)
                        context_start = max(0, i - 1)
                        context_end = min(len(session["messages"]), i + 2)
                        
                        results.append({
                            "session_id": session_id,
                            "message": message,
                            "context": session["messages"][context_start:context_end],
                            "timestamp": message["timestamp"]
                        })
                        
                        if len(results) >= max_results:
                            return results
        
        return results
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session
        
        Args:
            session_id: Session to delete
        
        Returns:
            True if deleted, False if not found
        """
        filepath = os.path.join(self.storage_path, f"{session_id}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️  Deleted session: {session_id}")
            return True
        
        return False
    
    def _load_session(self, session_id: str) -> Optional[Dict]:
        """Load session from disk"""
        filepath = os.path.join(self.storage_path, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading session {session_id}: {e}")
            return None
    
    def _save_session(self, session_id: str, session_data: Dict):
        """Save session to disk"""
        filepath = os.path.join(self.storage_path, f"{session_id}.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving session {session_id}: {e}")