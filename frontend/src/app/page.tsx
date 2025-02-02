'use client';

import { useState } from "react";
import { Loader2 } from "lucide-react";
import Banner from "./components/Banner";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!url) {
      setError("Please enter a URL");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const response = await fetch('http://127.0.0.1:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();
      
      if (!response.ok || data.error) {
        throw new Error(data.message || 'Analysis failed');
      }

      console.log('Analysis result:', data);
      setResults(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <Banner />
      
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold text-center mb-2">URL Metrics Analyzer</h1>
          <p className="text-gray-400 text-center mb-8">Analyze any website to get detailed metrics and insights</p>
          
          <div className="bg-zinc-900 rounded-lg shadow-xl p-6 mb-8 border border-zinc-800">
            <div className="space-y-4">
              <div className="relative">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter website URL (e.g., https://example.com)"
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500 text-white"
                />
              </div>
              
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full bg-primary hover:bg-primary-hover text-black font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin h-5 w-5" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <span>Analyze Website</span>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-900 text-red-200 px-4 py-3 rounded-lg mb-8">
              {error}
            </div>
          )}

          {results && (
            <div className="bg-zinc-900 rounded-lg shadow-xl overflow-hidden border border-zinc-800">
              <div className="p-6">
                <h2 className="text-xl font-semibold mb-4 text-primary">Analysis Results</h2>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-300 mb-2">Website Type</h3>
                    <p className="text-gray-400">{results.website_type}</p>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium text-gray-300 mb-2">Description</h3>
                    <p className="text-gray-400">{results.description}</p>
                  </div>

                  {results.metrics && results.metrics.length > 0 && (
                    <div>
                      <h3 className="text-lg font-medium text-gray-300 mb-3">Key Metrics</h3>
                      <div className="grid gap-4 md:grid-cols-2">
                        {results.metrics.map((metric: any, index: number) => (
                          <div
                            key={index}
                            className="bg-zinc-800 rounded-lg p-4 hover:bg-zinc-700 transition-colors border border-zinc-700"
                          >
                            <h4 className="font-medium text-primary mb-1">{metric.name}</h4>
                            {metric.tooltip && (
                              <p className="text-sm text-gray-400">{metric.tooltip}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {!results && !loading && !error && (
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-8 text-center">
              <p className="text-gray-400">
                Enter a website URL above and click Analyze to get detailed insights
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
