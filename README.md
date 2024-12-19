# Financial Document QA System

## Getting Started

### Prerequisites
- Python 3.11 
- pip (Python package installer)
- OpenAI API key

### Installation

1. **Set up virtual environment**
   ```
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```
   # Add your OpenAI API key to .env
   "OPENAI_API_KEY=your-api-key-here" >> .env
   ```

5. **Start the backend server**
   ```
   
   python run.py
   Embeddings should be generated in data/vector_store if you run for the second time it will check for embeddings in the vector_store and skip the embedding generation.

   ```

6. **Launch the frontend (in a new terminal)**
   ```
   # Navigate to frontend directory
   cd frontend

   # Install frontend dependencies
   npm install

   # Start the development server
   npm run dev
   ```

7. **Access the application**
   - Backend API: `http://localhost:8000`
   - Frontend interface: `http://localhost:3000`

## Architecture Overview

This system implements a sophisticated Retrieval-Augmented Generation (RAG) pipeline specifically designed for financial document question-answering.

### Model Choices

- **Main LLM**: GPT-4 Turbo (`gpt-4-turbo-preview`)
  - Configured with low temperature (0.1) for deterministic and precise financial responses
  - Maximum token limit: 2000
  - Request timeout: 60 seconds

- **Embeddings**: OpenAI's `text-embedding-3-small`
  - Balanced choice between cost and performance
  - Optimized for financial context

- **Vector Storage**: FAISS
  - Efficient similarity search capabilities
  - Lightweight memory footprint
  - Local storage implementation

### RAG System Architecture

#### Enhanced Retriever with Hybrid Search
- Combines semantic search with keyword-based matching
- Financial entity extraction for improved context matching
- Score-based reranking system
- Conversation-based result grouping for context maintenance

#### Optimized Chunking Strategy
- Chunk size: 500 tokens
- Overlap: 100 tokens
- Recursive character splitting
- Preserves financial data table structure

## Current Limitations and Future Improvements

### Implementation Limitations
- Implement a production vector database such as Pinecone or Supabase
- Limited 3-turn conversation history
- Basic financial entity extraction
- Simple memory management (ConversationBufferMemory)
- add other data sources to the database via an upload
- Save conversation history to database
- Imporve the handling of metrics
- Deploy to production

### Planned Improvements

#### Infrastructure
- Migration to production-ready vector database (e.g., Pinecone)
- Proper versioning for embeddings and models
- Enhanced financial entity recognition
- Robust error handling and retry mechanisms
- Comprehensive monitoring and logging
- Authentication and rate limiting
- Caching layer implementation
- Testing infrastructure
- CI/CD pipeline
- Backup and recovery mechanisms

#### Metrics Enhancement
- User satisfaction tracking
- Extended context tracking
- Component-wise latency analysis
- Answer confidence scoring
- Real-time metric visualization
- Resource utilization monitoring

## Development Rationale

The system was designed with a focus on rapid implementation while maintaining high-quality financial QA capabilities. The architecture choices reflect a balance between immediate functionality and future scalability, with clear paths for production-ready improvements.

The use of FAISS and local storage solutions were chosen for quick development and testing, with the understanding that these components would need to be replaced with more robust solutions in a production environment.

## System Metrics

### Current Performance Metrics

| Metric | Result | Why This Metric | Potential Improvements |
|--------|---------|----------------|----------------------|
| Embedding Time | 30:02 minutes | Measures initial setup efficiency | • Optimize chunk size<br>• Parallel processing<br>• More efficient text preprocessing |
| Response Latency | 9-11 seconds | Critical for user experience | • Switch to production vector DB<br>• Optimize context window size<br>• Cache frequent queries |
| Accuracy | 0.8 | Measures correctness of responses | • Fine-tune retrieval strategy<br>• Improve prompt engineering<br>• Enhance context selection |
| Cosine Similarity | 0.8 | Shows relevance of retrieved context | • Better document chunking<br>• Improve embedding strategy<br>• Enhanced reranking |
| F1 Score | 0.75 | Balanced measure of precision and recall | • Optimize retrieval threshold<br>• Better context filtering<br>• Improve query preprocessing |
| Average Token Usage | ~1500 | Tracks cost and efficiency | • Optimize prompt length<br>• Better context pruning<br>• Improve response conciseness |

### Recommended Additional Metrics

1. **User Experience Metrics**
   - Time to first response
   - User satisfaction rating
   - Query success rate
   - Session completion rate

2. **Quality Metrics**
   - Hallucination rate
   - Factual accuracy
   - Numerical precision
   - Source citation accuracy

3. **System Health Metrics**
   - Memory usage
   - CPU utilization
   - API error rate
   - Database query time

4. **Business Metrics**
   - Cost per query
   - Daily active users
   - User retention rate
   - Average session duration



