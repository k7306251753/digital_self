import chromadb
import uuid

class Memory:
    def __init__(self, collection_name="digital_self"):
        try:
            self.client = chromadb.PersistentClient(path="./memory_db")
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            self.collection = None

    def add_memory(self, text, metadata=None):
        if self.collection is None:
            raise Exception("Memory DB not initialized")
            
        if metadata is None:
            metadata = {}
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )

    def retrieve_context(self, query, n_results=3):
        if self.collection is None:
            return []
            
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if results['documents']:
            return results['documents'][0]
        return []
