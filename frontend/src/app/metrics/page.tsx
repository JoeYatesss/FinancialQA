import { Card } from '@/components/ui/card'

// Add type definitions for our metrics
interface Metrics {
  // Answer metrics
  answer_accuracy: number;
  exact_match_rate: number;
  cosine_similarity: number;
  rouge1: number;
  rouge2: number;
  rougeL: number;
  
  // Retrieval metrics
  retrieval_precision: number;
  retrieval_recall: number;
  f1_score: number;
  ndcg: number;
  mrr: number;
  
  // System metrics
  response_latency: number;
  context_retention: number;
  total_questions: number;
  successful_retrievals: number;
  total_conversations?: number;
  total_tokens?: number;
}

// Create a separate client component for the chart
import dynamic from 'next/dynamic'

const PerformanceChart = dynamic(
  () => import('../../components/PerformanceChart'),
  { ssr: false }
)

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to safely format numbers
const formatNumber = (value: number | undefined | null, decimals: number = 2): string => {
  if (value === undefined || value === null) return '0.00';
  return value.toFixed(decimals);
};

// Helper function to format percentages
const formatPercentage = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return '0%';
  return `${(value * 100).toFixed(1)}%`;
};

export default async function MetricsPage() {
  let metrics: Metrics | null = null;
  let error: string | null = null;

  try {
    const response = await fetch(`${API_URL}/api/metrics`, {
      next: { revalidate: 300 },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch metrics');
    }

    const data = await response.json();
    metrics = data.metrics;  // Use the metrics directly from the response
    
    if (!metrics) {
      metrics = {
        answer_accuracy: 0,
        exact_match_rate: 0,
        cosine_similarity: 0,
        rouge1: 0,
        rouge2: 0,
        rougeL: 0,
        retrieval_precision: 0,
        retrieval_recall: 0,
        f1_score: 0,
        ndcg: 0,
        mrr: 0,
        response_latency: 0,
        context_retention: 0,
        total_questions: 0,
        successful_retrievals: 0,
        total_conversations: 0,
        total_tokens: 0
      };
    }
  } catch (e) {
    error = e instanceof Error ? e.message : 'An error occurred while fetching metrics';
    metrics = {
      answer_accuracy: 0,
      exact_match_rate: 0,
      cosine_similarity: 0,
      rouge1: 0,
      rouge2: 0,
      rougeL: 0,
      retrieval_precision: 0,
      retrieval_recall: 0,
      f1_score: 0,
      ndcg: 0,
      mrr: 0,
      response_latency: 0,
      context_retention: 0,
      total_questions: 0,
      successful_retrievals: 0,
      total_conversations: 0,
      total_tokens: 0
    };
  }

  // Calculate retrieval success rate
  const retrievalSuccessRate = metrics.total_questions > 0 
    ? metrics.successful_retrievals / metrics.total_questions 
    : 0;

  return (
    <div className="p-8">
      {/* <h1 className="text-3xl font-bold mb-8">System Performance Metrics</h1> */}
      
      {/* Overview Stats */}
      {/* <Card className="p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4">System Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Questions</p>
            <p className="text-2xl font-bold">{metrics.total_questions}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Conversations</p>
            <p className="text-2xl font-bold">{metrics.total_conversations}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Tokens</p>
            <p className="text-2xl font-bold">{metrics?.total_tokens?.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Retrieval Success Rate</p>
            <p className="text-2xl font-bold">{formatPercentage(retrievalSuccessRate)}</p>
          </div>
        </div>
      </Card> */}
      
      {/* Answer Quality Metrics */}
      <h2 className="text-2xl font-bold mb-4">Answer Quality Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">Exact Match Rate</h3>
          <div className="text-4xl font-bold text-blue-600">
            {formatPercentage(metrics.exact_match_rate)}
          </div>
          <p className="text-gray-600 mt-2">
            Percentage of answers matching ground truth exactly
          </p>
          <div className="mt-4 h-2 bg-gray-200 rounded-full">
            <div 
              className="h-2 bg-blue-600 rounded-full" 
              style={{ width: `${metrics.exact_match_rate * 100}%` }}
            />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">Cosine Similarity</h3>
          <div className="text-4xl font-bold text-green-600">
            {formatPercentage(metrics.cosine_similarity)}
          </div>
          <p className="text-gray-600 mt-2">
            Semantic similarity with ground truth answers
          </p>
          <div className="mt-4 h-2 bg-gray-200 rounded-full">
            <div 
              className="h-2 bg-green-600 rounded-full" 
              style={{ width: `${metrics.cosine_similarity * 100}%` }}
            />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">ROUGE Scores</h3>
          <div className="space-y-2">
            <div>
              <span className="text-sm text-gray-600">ROUGE-1:</span>
              <span className="text-lg font-bold text-purple-600 ml-2">{formatPercentage(metrics.rouge1)}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">ROUGE-2:</span>
              <span className="text-lg font-bold text-purple-600 ml-2">{formatPercentage(metrics.rouge2)}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">ROUGE-L:</span>
              <span className="text-lg font-bold text-purple-600 ml-2">{formatPercentage(metrics.rougeL)}</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Retrieval Metrics */}
      <h2 className="text-2xl font-bold mb-4">Retrieval Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">Precision & Recall</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-600">Precision</span>
                <span className="text-sm font-bold">{formatPercentage(metrics.retrieval_precision)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full">
                <div 
                  className="h-2 bg-blue-600 rounded-full" 
                  style={{ width: `${metrics.retrieval_precision * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-600">Recall</span>
                <span className="text-sm font-bold">{formatPercentage(metrics.retrieval_recall)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full">
                <div 
                  className="h-2 bg-green-600 rounded-full" 
                  style={{ width: `${metrics.retrieval_recall * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-600">F1 Score</span>
                <span className="text-sm font-bold">{formatPercentage(metrics.f1_score)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full">
                <div 
                  className="h-2 bg-yellow-600 rounded-full" 
                  style={{ width: `${metrics.f1_score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">NDCG</h3>
          <div className="text-4xl font-bold text-indigo-600">
            {formatPercentage(metrics.ndcg)}
          </div>
          <p className="text-gray-600 mt-2">
            Normalized Discounted Cumulative Gain
          </p>
          <div className="mt-4 h-2 bg-gray-200 rounded-full">
            <div 
              className="h-2 bg-indigo-600 rounded-full" 
              style={{ width: `${metrics.ndcg * 100}%` }}
            />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">MRR</h3>
          <div className="text-4xl font-bold text-pink-600">
            {formatPercentage(metrics.mrr)}
          </div>
          <p className="text-gray-600 mt-2">
            Mean Reciprocal Rank
          </p>
          <div className="mt-4 h-2 bg-gray-200 rounded-full">
            <div 
              className="h-2 bg-pink-600 rounded-full" 
              style={{ width: `${metrics.mrr * 100}%` }}
            />
          </div>
        </Card>
      </div>

      {/* System Performance */}
      <h2 className="text-2xl font-bold mb-4">System Performance</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">Response Latency</h3>
          <div className="text-4xl font-bold text-yellow-600">
            {formatNumber(metrics.response_latency, 1)}s
          </div>
          <p className="text-gray-600 mt-2">
            Average time taken to generate a response
          </p>
          <div className="mt-4 text-sm text-gray-500">
            Target: &lt; 3s
          </div>
          <div className="mt-2 h-2 bg-gray-200 rounded-full">
            <div 
              className={`h-2 rounded-full ${
                metrics.response_latency > 3 ? 'bg-red-600' : 'bg-yellow-600'
              }`}
              style={{ width: `${Math.min(metrics.response_latency / 5 * 100, 100)}%` }}
            />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-2">Context Retention</h3>
          <div className="text-4xl font-bold text-purple-600">
            {formatPercentage(metrics.context_retention)}
          </div>
          <p className="text-gray-600 mt-2">
            Semantic similarity with conversation history
          </p>
          <div className="mt-4 h-2 bg-gray-200 rounded-full">
            <div 
              className="h-2 bg-purple-600 rounded-full" 
              style={{ width: `${metrics.context_retention * 100}%` }}
            />
          </div>
        </Card>
      </div>

      {/* System Health */}
      {/* <Card className="p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4">System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full ${metrics.f1_score > 0.7 ? 'bg-green-500' : 'bg-yellow-500'} mr-2`} />
            <span className="text-gray-700">Retrieval Quality</span>
          </div>
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full ${metrics.response_latency < 3 ? 'bg-green-500' : 'bg-yellow-500'} mr-2`} />
            <span className="text-gray-700">Response Time</span>
          </div>
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full ${metrics.exact_match_rate > 0.5 ? 'bg-green-500' : 'bg-yellow-500'} mr-2`} />
            <span className="text-gray-700">Answer Quality</span>
          </div>
        </div>
      </Card> */}
    </div>
  );
} 