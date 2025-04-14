from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from datetime import datetime, timedelta
import json

class RAGManager:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Initialize FAISS index
        self.dimension = 384  # Dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        # Store conversation chunks and metadata
        self.conversation_chunks = []
        self.metadata = []

    def create_chunks(self, conversation_history, chunk_size=3):
        """Split conversation history into chunks of messages."""
        chunks = []
        for i in range(0, len(conversation_history), chunk_size):
            chunk = conversation_history[i:i + chunk_size]
            # Combine messages in the chunk
            chunk_text = " ".join([msg["content"] for msg in chunk])
            chunks.append({
                "text": chunk_text,
                "timestamp": chunk[-1]["timestamp"],
                "messages": chunk
            })
        return chunks

    def add_conversation(self, conversation_history):
        """Add new conversation chunks to the RAG system."""
        chunks = self.create_chunks(conversation_history)
        
        for chunk in chunks:
            # Generate embedding for the chunk
            embedding = self.model.encode(chunk["text"])
            # Add to FAISS index
            self.index.add(np.array([embedding]).astype('float32'))
            # Store metadata
            self.conversation_chunks.append(chunk)
            self.metadata.append({
                "timestamp": chunk["timestamp"],
                "chunk_index": len(self.conversation_chunks) - 1
            })

    def search_relevant_context(self, query, k=3, time_window_days=7):
        """Search for relevant conversation chunks based on the query."""
        # Generate embedding for the query
        query_embedding = self.model.encode(query)
        
        # Search in FAISS index
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), 
            k
        )
        
        # Get relevant chunks
        relevant_chunks = []
        current_time = datetime.utcnow()
        
        for idx in indices[0]:
            if idx < len(self.conversation_chunks):
                chunk = self.conversation_chunks[idx]
                # Check if chunk is within time window
                if (current_time - chunk["timestamp"]).days <= time_window_days:
                    relevant_chunks.append(chunk)
        
        return relevant_chunks

    def get_context_for_prompt(self, current_message, conversation_history):
        """Get relevant context for the current message."""
        # Add new conversation to the RAG system
        self.add_conversation(conversation_history)
        
        # Search for relevant context
        relevant_chunks = self.search_relevant_context(current_message)
        
        # Format context for the prompt
        context = ""
        for chunk in relevant_chunks:
            context += f"Previous conversation (from {chunk['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}):\n"
            for msg in chunk["messages"]:
                context += f"{msg['role']}: {msg['content']}\n"
            context += "\n"
        
        return context 