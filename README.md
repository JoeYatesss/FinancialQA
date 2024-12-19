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

This system implements a Retrieval-Augmented Generation (RAG) pipeline specifically designed for financial document question-answering. The architecture was carefully designed to balance accuracy, performance, and maintainability while handling financial information.

### Design Philosophy

- **Accuracy First**: Financial data requires extremely high precision. The system prioritizes accurate information retrieval and response generation over speed.
  
- **Context Preservation**: Financial documents often contain interconnected information (e.g., metrics tied to specific time periods or conditions). The architecture maintains these relationships through:
  - Strategic document chunking that keeps related information together
  - Context-aware retrieval that considers document structure
  - Conversation memory to maintain topic continuity

### Why RAG?

1. **Source Truth**: Traditional LLMs can sometimes generate plausible-sounding but incorrect information (hallucinations). RAG solves this by:
   - Retrieving specific passages from your verified financial documents
   - Using these passages as evidence to generate responses
   - Ensuring every answer can be traced back to source documents
   - Maintaining data lineage for regulatory compliance

2. **Cost Efficiency**: Reduces token usage by providing focused context
3. **Up-to-date Information**: Easy to update by simply refreshing the document database
4. **Reduced Hallucination**: LLM responses are constrained by retrieved context

### System Components

Each component was chosen with specific reasoning:

1. **Vector Database (FAISS)**
   - Local implementation for rapid development
   - Excellent performance for our current scale
   - Easy migration path to production databases

2. **Embedding Model (text-embedding-3-small)**
   - Strong performance on financial text
   - Cost-effective for development
   - Good balance of speed and accuracy

3. **LLM (GPT-4 Turbo)**
   - Superior understanding of financial concepts
   - Excellent at maintaining context
   - Strong numerical reasoning capabilities

### Data Flow

1. Query → Embedding → Retrieval → Context Assembly → Response Generation

This linear flow prioritizes:
- Maintainability: Each step is isolated and testable
- Transparency: Clear data transformation path
- Extensibility: Easy to add new components or modify existing ones

## Other Options

1. **Graph Database Approach**
   - Represents financial documents as interconnected nodes and relationships
   - Better captures complex financial relationships and dependencies
   - Enables hierarchical and network analysis
   - Supports temporal relationships between financial events
   - Visual represntation of the data (would have been a cool addition, showing the retieval of the data)
   - Challenges: Higher complexity, longer developement time

2. **Semantic Search with Traditional NLP**
   - Uses techniques like TF-IDF, BM25, or LSA
   - Lower computational requirements
   - No dependency on external AI services
   - Challenges: Less understanding of context, literal matching only

3. **Fine-tuned Language Models**
   - Train specialized models on financial documents
   - Better domain-specific understanding
   - No need for real-time retrieval
   - Challenges: Regular retraining needed, high computational cost

Each approach has its trade-offs in terms of:
- Accuracy vs. Speed
- Complexity vs. Maintainability
- Cost vs. Capability
- Development Time vs. Performance

## Current Limitations and Future Improvements

### Implementation Limitations
- Implement a production vector database such as Pinecone or Supabase
- Limited 3-turn conversation history
- Basic financial entity extraction
- Simple memory management (ConversationBufferMemory)
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
- Addition of other data sources to the database via an upload/APIs
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



