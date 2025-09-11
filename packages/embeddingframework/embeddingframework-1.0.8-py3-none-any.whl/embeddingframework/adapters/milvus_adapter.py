from .base import VectorDBAdapter
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility


class MilvusAdapter(VectorDBAdapter):
    def add_texts(self, texts, embeddings):
        """Default add_texts implementation for testing."""
        if not hasattr(self, "collection") or self.collection is None:
            raise RuntimeError("Collection not initialized. Call connect or create_collection first.")
        # Simulate insert into Milvus
        entities = []
        for i, (txt, emb) in enumerate(zip(texts, embeddings)):
            entities.append({"id": str(i), "embedding": emb, "metadata": {"text": txt}})
        # Store in a simple list for retrieval simulation
        self.texts = getattr(self, "texts", []) + texts
        return [e["id"] for e in entities]

    def add_texts(self, texts, embeddings):
        """Default add_texts implementation for testing."""
        if not getattr(self, "collection", None):
            if not getattr(self, "client", None):
                self.connect()
            self.create_collection(vector_dimension=len(embeddings[0]) if embeddings else 1536)
        ids = [str(i) for i in range(len(texts))]
        data = [ids, embeddings, [txt for txt in texts]]
        self.collection.insert(data)
        self.collection.flush()
        print(f"Added {len(texts)} texts to Milvus collection.")
        return ids
    def __init__(self, host: str = "localhost", port: str = "19530", collection_name: str = "default_collection"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection = None

    def connect(self):
        connections.connect(alias="default", host=self.host, port=self.port)
        print(f"Connected to Milvus at {self.host}:{self.port}")

    def create_collection(self, vector_dimension: int = 1536):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            print(f"Milvus collection '{self.collection_name}' already exists.")
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=vector_dimension),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, description="Embedding collection")
        self.collection = Collection(name=self.collection_name, schema=schema)
        print(f"Milvus collection '{self.collection_name}' created.")

    def insert_embeddings(self, ids, embeddings, metadatas):
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call create_collection first.")
        data = [ids, embeddings, [str(meta) for meta in metadatas]]
        self.collection.insert(data)
        self.collection.flush()

    def query(self, query_embeddings, n_results=5):
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call create_collection first.")
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        return self.collection.search(query_embeddings, "embedding", search_params, limit=n_results, output_fields=["metadata"])

    def delete(self, ids):
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call create_collection first.")
        expr = f'id in {ids}'
        self.collection.delete(expr)

    def disconnect(self):
        """Disconnect from Milvus and clear collection reference."""
        self.collection = None
        try:
            connections.disconnect(alias="default")
        except Exception:
            pass
        print("Disconnected from Milvus.")
