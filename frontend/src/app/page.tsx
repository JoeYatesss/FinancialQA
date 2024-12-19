'use client'

import { useState, useEffect } from 'react'
import { askQuestion } from '@/lib/api'
import { Card } from '@/components/ui/card'

interface ChatMetrics {
  answer_accuracy: number;
  exact_match_rate: number;
  cosine_similarity: number;
  rouge1: number;
  rouge2: number;
  rougeL: number;
  retrieval_precision: number;
  retrieval_recall: number;
  f1_score: number;
  ndcg: number;
  mrr: number;
  response_latency: number;
  context_retention: number;
  total_questions: number;
  successful_retrievals: number;
  total_conversations: number;
  total_tokens: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metrics?: ChatMetrics;
  timestamp: string;
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string>(() => 
    `session_${Date.now()}`
  )

  useEffect(() => {
    const savedMessages = localStorage.getItem(`chat_history_${conversationId}`)
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages))
    }
  }, [conversationId])

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_history_${conversationId}`, JSON.stringify(messages))
    }
  }, [messages, conversationId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await askQuestion({
        question: input,
        conversation_id: conversationId,
        context: {
          history: messages.map(m => ({
            role: m.role,
            content: m.content
          }))
        }
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        metrics: response.metrics as unknown as ChatMetrics,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen p-4">
      {/* Chat Messages */}
      <div className="flex-1 overflow-auto mb-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className="flex flex-col max-w-[80%]">
                <div
                  className={`rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-[#d8ff00] text-black'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
                {message.metrics && (
                  <div className="flex flex-wrap gap-2 mt-1 text-xs text-secondary">
                    <span>Accuracy: {(message.metrics.answer_accuracy * 100).toFixed(1)}%</span>
                    <span>•</span>
                    <span>Latency: {message.metrics.response_latency.toFixed(2)}s</span>
                    <span>•</span>
                    <span>Context: {(message.metrics.context_retention * 100).toFixed(1)}%</span>
                    <span>•</span>
                    <span>Precision: {(message.metrics.retrieval_precision * 100).toFixed(1)}%</span>
                    <span>•</span>
                    <span>Recall: {(message.metrics.retrieval_recall * 100).toFixed(1)}%</span>
                  </div>
                )}
                <div className="text-xs text-secondary mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[#d8ff00] rounded-lg p-4">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-black rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-black rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-black rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto w-full">
        <div className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border-2 border-secondary rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary bg-white text-black placeholder-gray-500"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 border-2 border-[#d8ff00] text-[#d8ff00] rounded-lg hover:bg-[#d8ff00] hover:text-black disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}
