import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from ..models.database import store_embeddings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Initialize the sentence transformer model
        # Using BGE-small-en as specified in requirements
        # For Docker deployment, models are pre-cached during build
        import os
        
        # Set model cache directory for offline usage
        model_cache_dir = os.getenv('SENTENCE_TRANSFORMERS_HOME', '/app/models')
        
        try:
            # Try to load from local cache first (for Docker deployment)
            self.model = SentenceTransformer('BAAI/bge-small-en-v1.5', cache_folder=model_cache_dir)
            logger.info(f"Embedding service initialized with BGE-small-en-v1.5 from cache: {model_cache_dir}")
        except Exception as e:
            logger.warning(f"Failed to load from cache, downloading model: {e}")
            # Fallback to downloading if cache fails
            self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
            logger.info("Embedding service initialized with BGE-small-en-v1.5 (downloaded)")
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        try:
            embedding = self.model.encode([text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"Error creating embedding for text: {str(e)}")
            raise
    
    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts efficiently"""
        try:
            embeddings = self.model.encode(texts)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise
    
    async def create_embeddings(self, chunks: List[Dict[str, Any]], filename: str, pdf_path: str) -> str:
        """
        Create embeddings for PDF chunks and store in database
        """
        try:
            logger.info(f"Creating embeddings for {len(chunks)} chunks from {filename}")
            
            # Extract text from chunks
            texts = [chunk['chunk_text'] for chunk in chunks]
            
            # Create embeddings in batch for efficiency
            embeddings = self.create_embeddings_batch(texts)
            
            # Prepare data for database storage
            chunks_data = []
            for i, chunk in enumerate(chunks):
                chunks_data.append({
                    'file_name': filename,
                    'chunk_text': chunk['chunk_text'],
                    'embedding': embeddings[i]
                })
            
            # Store in database
            config_id = await store_embeddings(chunks_data)
            
            logger.info(f"Successfully created and stored embeddings with config_id: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def find_most_similar(self, query_text: str, candidate_texts: List[str], top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Find most similar texts using semantic similarity
        """
        try:
            # Create embedding for query
            query_embedding = self.create_embedding(query_text)
            
            # Create embeddings for candidates
            candidate_embeddings = self.create_embeddings_batch(candidate_texts)
            
            # Calculate cosine similarities
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = np.dot(query_embedding, candidate_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(candidate_embedding)
                )
                similarities.append({
                    'text': candidate_texts[i],
                    'similarity': float(similarity),
                    'index': i
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar texts: {str(e)}")
            raise
