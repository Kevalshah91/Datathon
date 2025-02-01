import { useState } from 'react';
import { UploadCloud, BarChart2, AlertCircle } from 'lucide-react';

const MarketingAnalysis = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const jsonData = JSON.parse(jsonInput);
      const response = await fetch('http://localhost:5100/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
      });
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error);
      }
      
      // Parse the analysis string into sections
      const sections = data.analysis.split('\n\n').reduce((acc, section) => {
        if (section.startsWith('===')) {
          acc.title = section.replace(/===/g, '').trim();
        } else if (section.startsWith('Market Context:')) {
          acc.marketContext = section.replace('Market Context:', '').trim();
        } else if (section.startsWith('Primary Focus Areas:')) {
          acc.focusAreas = section
            .replace('Primary Focus Areas:', '')
            .trim()
            .split('\n')
            .filter(item => item.startsWith('-'))
            .map(item => item.replace('-', '').trim());
        } else if (section.startsWith('Behavioral Insights:')) {
          acc.insights = section
            .replace('Behavioral Insights:', '')
            .trim()
            .split('\n')
            .filter(item => item.startsWith('-'))
            .map(item => item.replace('-', '').trim());
        }
        return acc;
      }, {});
      
      setAnalysis(sections);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Marketing Analysis Dashboard</h1>
          <p className="text-gray-600">Upload your JSON data to analyze marketing performance</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              JSON Input
            </label>
            <textarea
              className="w-full h-40 px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:border-blue-500"
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              placeholder="Paste your JSON data here..."
            />
          </div>
          <button
            onClick={analyzeData}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <BarChart2 className="animate-spin" size={20} />
                Analyzing...
              </>
            ) : (
              <>
                <UploadCloud size={20} />
                Analyze Data
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8 rounded">
            <div className="flex items-center">
              <AlertCircle className="text-red-400" size={24} />
              <p className="ml-3 text-red-700">{error}</p>
            </div>
          </div>
        )}

        {analysis && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{analysis.title}</h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Market Context</h3>
                <p className="text-gray-600">{analysis.marketContext}</p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Primary Focus Areas</h3>
                <ul className="space-y-2">
                  {analysis.focusAreas.map((area, index) => (
                    <li key={index} className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-blue-100 text-blue-600 mr-2">
                        {index + 1}
                      </span>
                      <span className="text-gray-600">{area}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Behavioral Insights</h3>
                <ul className="space-y-2">
                  {analysis.insights.map((insight, index) => (
                    <li key={index} className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-green-100 text-green-600 mr-2">
                        {index + 1}
                      </span>
                      <span className="text-gray-600">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketingAnalysis;