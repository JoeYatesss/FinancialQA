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

### Metrics System

Our metrics system is designed to comprehensively evaluate both the retrieval and generation aspects of the RAG pipeline, ensuring high-quality financial information delivery.

#### Retrieval Metrics
- **Precision and Recall Tracking**
  - Precision measures the proportion of retrieved documents that are relevant
  - Recall measures the proportion of relevant documents that were successfully retrieved
  - Critical for financial QA where both accuracy and completeness are essential
  - Helps identify if the system is missing crucial financial information or retrieving irrelevant data

- **Score-based Relevance Assessment**
  - Combines semantic similarity scores with financial entity matching
  - Higher weights assigned to exact matches of financial numbers and percentages (0.5)
  - Lower weights for general financial term matches (0.3)
  - Ensures financial data accuracy in retrieved context

- **Context Retention Measurements**
  - Tracks how well context is maintained across conversation turns
  - Evaluates the system's ability to maintain coherent financial discussions
  - Particularly important for multi-turn queries about financial reports or trends

#### Answer Quality Metrics
- **ROUGE Scores Against Retrieved Context**
  - ROUGE-1: Measures unigram overlap between generated answer and context
  - ROUGE-2: Measures bigram overlap for phrase accuracy
  - ROUGE-L: Measures longest common subsequence for fluency
  - Ensures answers are grounded in the retrieved financial documents

- **Semantic Similarity with Ground Truth**
  - Uses embedding-based similarity scoring
  - Evaluates answer correctness beyond exact word matching
  - Particularly useful for financial explanations where multiple valid phrasings exist
  - Helps identify conceptual accuracy in financial explanations

- **Conversation Context Retention**
  - Measures semantic similarity between consecutive answers
  - Evaluates consistency in financial advice and explanations
  - Tracks topic drift in multi-turn financial discussions
  - Important for maintaining coherent financial narratives

#### Performance Metrics (Planned)
- **Latency Tracking**
  - Component-wise timing (retrieval, processing, generation)
  - Critical for real-time financial applications
  - Helps identify bottlenecks in the pipeline

- **User Satisfaction Metrics**
  - Answer helpfulness ratings
  - Query reformulation rates
  - Session completion rates
  - Essential for measuring real-world utility in financial decision-making

- **Resource Utilization**
  - Token usage monitoring
  - Embedding operation counts
  - Storage efficiency
  - Important for cost optimization in production environments

### Metric Selection Rationale

Our metric selection was driven by several key considerations in financial QA:

1. **Accuracy Priority**: Financial information must be precise and accurate, hence the focus on exact matching and semantic similarity metrics.

2. **Context Importance**: Financial discussions often require maintaining context across multiple turns, reflected in our context retention metrics.

3. **User-Centric Evaluation**: Planned user satisfaction metrics ensure the system provides actually useful financial insights.

4. **Performance Monitoring**: Latency and resource metrics ensure the system remains cost-effective and responsive in production.

These metrics work together to ensure:
- Retrieved context is relevant and complete
- Generated answers are accurate and well-grounded
- Conversations remain coherent and contextual
- System performance meets production requirements

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

The use of FAISS and local storage solutions was chosen for quick development and testing, with the understanding that these components would need to be replaced with more robust solutions in a production environment.

### Troubleshooting

Common issues and solutions:

1. **OpenAI API Key Issues**
   - Ensure your API key is correctly set in the `.env` file
   - Check API key permissions and usage limits

2. **Embedding Generation Errors**
   - Verify input data format
   - Check available disk space for vector store
   - Ensure OpenAI API is accessible

3. **Frontend Connection Issues**
   - Verify backend is running and accessible
   - Check CORS settings in backend configuration
   - Ensure correct ports are available


Embedding time: 
   start: 12:42
   end: 1:12
   total: 30:02
