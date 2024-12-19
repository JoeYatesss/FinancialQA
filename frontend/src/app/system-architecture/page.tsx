import { Card } from '@/components/ui/card'

export default function SystemArchitecturePage() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4 text-white">
          System Architecture
        </h1>
        <p className="text-lg text-gray-300 max-w-3xl">
          A technical deep dive into our Financial QA system's architecture, model choices, and implementation details.
        </p>
      </div>

      <div className="space-y-8">
        {/* Model Choices */}
        <Card className="p-8 border-l-4 border-[#d8ff00]">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Model Architecture</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-[#d8ff00] rounded-full mr-2"></span>
                Large Language Model
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Leveraging GPT-4 Turbo with precise configuration (temperature: 0.1) for consistent and accurate financial responses.
                Optimized with a 2000-token context window and 60-second timeout for efficient query processing in financial contexts.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-[#d8ff00] rounded-full mr-2"></span>
                Embedding System
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Implemented using OpenAI's text-embedding-3-small model, offering an optimal balance between
                performance and cost efficiency. Specifically tuned for financial domain understanding and
                semantic search capabilities.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-[#d8ff00] rounded-full mr-2"></span>
                Vector Storage Solution
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                FAISS implementation providing high-performance similarity search with minimal memory overhead.
                Designed for rapid prototyping while maintaining production-grade search capabilities.
              </p>
            </div>
          </div>
        </Card>

        {/* Current Limitations */}
        <Card className="p-8 border-l-4 border-red-400">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Current Limitations</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                Storage Constraints
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Local FAISS implementation limits scalability and persistence. No distributed storage
                capability, making it challenging to handle large-scale document collections or
                maintain system state across deployments.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                Context Management
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Basic ConversationBufferMemory with 3-turn limit restricts long-term context retention.
                No hierarchical summarization or dynamic context window adjustment, leading to potential
                information loss in extended conversations.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                Entity Recognition
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Pattern-based financial entity extraction lacks sophisticated NER capabilities.
                Limited ability to handle complex financial instruments, nested entities, or
                context-dependent financial terminology.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                Production Readiness
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Absence of robust error handling, monitoring, and logging infrastructure.
                No authentication system, rate limiting, or proper API versioning.
                Limited caching mechanisms impact response times and resource utilization.
              </p>
            </div>
          </div>
        </Card>

        {/* RAG System Architecture */}
        <Card className="p-8 border-l-4 border-[#d8ff00]">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Retrieval Architecture</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-[#d8ff00] rounded-full mr-2"></span>
                Hybrid Search Engine
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Advanced retrieval system combining semantic search with financial entity matching.
                Features include intelligent score-based reranking and contextual result grouping,
                optimized for financial document retrieval.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-[#d8ff00] rounded-full mr-2"></span>
                Document Processing
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Sophisticated chunking strategy utilizing 500-token segments with 100-token overlaps.
                Implements recursive splitting while maintaining structural integrity of financial data
                and tabular information.
              </p>
            </div>
          </div>
        </Card>

        {/* Technical Limitations */}
        <Card className="p-8 border-l-4 border-red-400">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Current Technical Scope</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-red-400 rounded-full mr-2"></span>
                Infrastructure Constraints
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Current implementation utilizes local FAISS storage and basic ConversationBufferMemory
                with a 3-turn conversation limit. Financial entity extraction system operates with
                foundational pattern matching capabilities.
              </p>
            </div>
          </div>
        </Card>

        {/* Roadmap */}
        <Card className="p-8 border-l-4 border-blue-400">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Technical Roadmap</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                Infrastructure Evolution
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Planned migration to enterprise-grade vector database (Pinecone), implementation of
                versioned embeddings, and enhanced financial entity recognition. Infrastructure improvements
                include robust error handling, comprehensive monitoring, and advanced caching mechanisms.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                Analytics & Monitoring
              </h3>
              <p className="text-gray-600 leading-relaxed pl-4 border-l border-gray-200">
                Development of comprehensive analytics suite including user satisfaction metrics,
                extended context tracking, and granular performance monitoring. Implementation of
                real-time visualization tools and resource utilization analytics.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
} 