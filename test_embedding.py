from app.rag.embeddings import EnhancedEmbeddingEngine
import os
from dotenv import load_dotenv

def test_embeddings():
    # Load environment variables
    load_dotenv()
    print("Environment variables loaded")
    
    # Initialize the embedding engine
    print("Initializing embedding engine...")
    engine = EnhancedEmbeddingEngine()
    
    # Test data
    test_data = [
        {
            "text": "This is a test message to verify embeddings are working correctly.",
            "metadata": {"source": "test"}
        }
    ]
    
    try:
        # Get a single embedding first to test
        print("\nTesting direct embedding...")
        test_embedding = engine.embeddings.embed_query("Test embedding")
        print(f"✅ Direct embedding successful! Vector dimension: {len(test_embedding)}")
        
        # Process the test document
        print("\nTesting document processing...")
        engine.process_documents(test_data, save_path="data/test_vector_store")
        print("✅ Document processing successful!")
        return True
    except Exception as e:
        print(f"❌ Embedding test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_embeddings() 