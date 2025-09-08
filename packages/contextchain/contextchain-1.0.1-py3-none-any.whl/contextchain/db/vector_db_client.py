import chromadb
from pathlib import Path

# This will hold the client instance to ensure it's a singleton
_db_client = None

def get_vector_db_client(db_path: str = "./contextchain_chromadb"):
    """
    Initializes and returns a persistent ChromaDB client.

    If a client at the specified path doesn't exist, it creates one.
    This function is simpler than the MongoDB one because Chroma's
    PersistentClient handles its own local "server" state.

    Args:
        db_path (str): The file system path to store the vector database.

    Returns:
        chromadb.Client: An initialized and connected ChromaDB client instance.
    """
    global _db_client
    if _db_client:
        return _db_client

    try:
        # Ensure the parent directory for the database exists
        db_dir = Path(db_path)
        db_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Attempting to connect to or create ChromaDB at: {db_dir.resolve()}")

        # PersistentClient will create the DB at the path if it doesn't exist
        client = chromadb.PersistentClient(path=str(db_dir))
        
        # The 'heartbeat()' method checks if the client can connect to the server.
        # For a persistent client, this confirms the database is usable.
        client.heartbeat() 

        print("✓ ChromaDB client initialized successfully.")
        _db_client = client
        return _db_client

    except Exception as e:
        print(f"✗ Failed to initialize ChromaDB client at {db_path}: {e}")
        # Re-raise the exception as there's no separate process to start/recover
        raise Exception(f"Fatal: Could not set up the vector database.")