"""
Memory Manager
Manages conversation memory and context for AI
"""

from typing import List, Dict, Optional
from .conversation_store import ConversationStore


class MemoryManager:
    """Manages conversation memory for TurboBot"""
    
    def __init__(self, storage_path: str = 'data/conversations'):
        """
        Initialize memory manager
        
        Args:
            storage_path: Path to store conversations
        """
        self.store = ConversationStore(storage_path)
        self.current_session = None
        
        print("🧠 Memory Manager initialized")
    
    def start_session(self) -> str:
        """
        Start a new conversation session
        
        Returns:
            session_id
        """
        self.current_session = self.store.create_session()
        return self.current_session
    
    def set_session(self, session_id: str):
        """Set active session"""
        self.current_session = session_id
        print(f"📌 Active session: {session_id}")
    
    def add_interaction(self, user_message: str, assistant_response: str,
                       turbine_data: Optional[Dict] = None):
        """
        Add a complete user-assistant interaction
        
        Args:
            user_message: User's question
            assistant_response: TurboBot's response
            turbine_data: Optional turbine data context
        """
        if not self.current_session:
            self.start_session()
        
        # Add user message
        self.store.add_message(
            self.current_session,
            role="user",
            content=user_message,
            metadata={"turbine_data": turbine_data} if turbine_data else None
        )
        
        # Add assistant response
        self.store.add_message(
            self.current_session,
            role="assistant",
            content=assistant_response
        )
    
    def get_context_for_ai(self, max_messages: int = 10) -> List[Dict]:
        """
        Get recent conversation context for AI
        
        Args:
            max_messages: Maximum number of recent messages
        
        Returns:
            List of messages in format for AI
        """
        if not self.current_session:
            return []
        
        messages = self.store.get_conversation(self.current_session, last_n=max_messages)
        
        # Format for AI (role + content only)
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted
    
    def get_full_history(self) -> List[Dict]:
        """
        Get complete conversation history for current session
        
        Returns:
            All messages in current session
        """
        if not self.current_session:
            return []
        
        return self.store.get_conversation(self.current_session)
    
    def search_memory(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search through past conversations
        
        Args:
            query: What to search for
            max_results: Maximum results to return
        
        Returns:
            Matching conversations with context
        """
        return self.store.search_conversations(query, max_results)
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current session
        
        Returns:
            Session statistics
        """
        if not self.current_session:
            return {"active": False}
        
        messages = self.get_full_history()
        
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        return {
            "active": True,
            "session_id": self.current_session,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "last_interaction": messages[-1]["timestamp"] if messages else None
        }
    
    def list_all_sessions(self) -> List[Dict]:
        """
        List all past conversation sessions
        
        Returns:
            List of session summaries
        """
        return self.store.get_all_sessions()
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a previous session
        
        Args:
            session_id: Session to load
        
        Returns:
            True if loaded successfully
        """
        messages = self.store.get_conversation(session_id)
        
        if messages:
            self.current_session = session_id
            print(f"✅ Loaded session: {session_id} ({len(messages)} messages)")
            return True
        
        print(f"⚠️  Session {session_id} not found")
        return False
    
    def clear_session(self):
        """Clear current session (start fresh)"""
        self.current_session = None
        print("🔄 Session cleared")


# Test the memory system
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING MEMORY SYSTEM")
    print("="*70)
    
    # Create memory manager
    memory = MemoryManager()
    
    # Start session
    session_id = memory.start_session()
    print(f"\n✅ Session started: {session_id}")
    
    # Simulate conversation
    print("\n📝 Adding test conversation...")
    memory.add_interaction(
        user_message="What causes high vibration?",
        assistant_response="High vibration can be caused by bearing wear, imbalance, or misalignment.",
        turbine_data={"temperature": 65, "vibration": 4.2}
    )
    
    memory.add_interaction(
        user_message="What should I do about it?",
        assistant_response="Schedule inspection within 48 hours and monitor continuously."
    )
    
    # Get context
    print("\n📖 Getting conversation context...")
    context = memory.get_context_for_ai(max_messages=6)
    for msg in context:
        print(f"   {msg['role']}: {msg['content'][:50]}...")
    
    # Get summary
    print("\n📊 Session summary:")
    summary = memory.get_session_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # List sessions
    print("\n📋 All sessions:")
    sessions = memory.list_all_sessions()
    for session in sessions[:5]:
        print(f"   {session['session_id']}: {session['total_messages']} messages")
    
    print("\n" + "="*70)
    print("✅ Memory system test complete!")
    print("="*70 + "\n")