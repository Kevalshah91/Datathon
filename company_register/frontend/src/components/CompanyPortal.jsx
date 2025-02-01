import { useState, useEffect } from 'react';
import { Building2, Mail, Globe, FileText, Loader2, CheckCircle } from 'lucide-react';

const CompanyPortal = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    companyName: '',
    domain: '',
    description: ''
  });

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setError('');
      const response = await fetch('http://localhost:3000/api/companies');
      if (!response.ok) {
        throw new Error('Failed to fetch companies');
      }
      const { data } = await response.json();
      setCompanies(data);
    } catch (error) {
      setError('Failed to load companies. Please try again later.');
      console.error('Error fetching companies:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:3000/api/companies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'Failed to register company');
      }
      
      setFormData({
        email: '',
        companyName: '',
        domain: '',
        description: ''
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      fetchCompanies();
    } catch (error) {
      setError(error.message || 'Failed to register company. Please try again.');
      console.error('Error registering company:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {error && (
          <div className="bg-red-500 text-white p-4 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Registration Form */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">Register Your Company</h2>
            <p className="text-gray-400">Join our platform and showcase your business to the world</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Building2 className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="companyName"
                  value={formData.companyName}
                  onChange={handleChange}
                  placeholder="Company Name"
                  className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  required
                />
              </div>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Email Address"
                  className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  required
                />
              </div>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Globe className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="domain"
                  value={formData.domain}
                  onChange={handleChange}
                  placeholder="Domain (e.g., company.com)"
                  className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </div>

              <div className="relative">
                <div className="absolute top-3 left-3 pointer-events-none">
                  <FileText className="h-5 w-5 text-gray-400" />
                </div>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Company Description"
                  className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all min-h-[120px] resize-y"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                  Registering...
                </>
              ) : success ? (
                <>
                  <CheckCircle className="-ml-1 mr-2 h-5 w-5" />
                  Registration Successful!
                </>
              ) : (
                'Register Company'
              )}
            </button>
          </form>
        </div>

        {/* Registered Companies */}
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">Registered Companies</h2>
            <p className="text-gray-400">Browse through our network of registered companies</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {companies.map((company) => (
              <div key={company._id} className="bg-gray-700 rounded-lg p-6 border border-gray-600 hover:border-gray-500 transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">{company.companyName}</h3>
                    <p className="text-gray-400 text-sm">{company.domain}</p>
                  </div>
                  <Building2 className="h-6 w-6 text-blue-400" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center text-gray-300">
                    <Mail className="h-4 w-4 mr-2" />
                    <span className="text-sm">{company.email}</span>
                  </div>
                  <p className="text-gray-400 text-sm line-clamp-3">
                    {company.description || 'No description provided'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyPortal;