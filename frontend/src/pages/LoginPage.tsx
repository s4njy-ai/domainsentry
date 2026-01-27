

export const LoginPage = () => (
  <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
    <div className="p-8 bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl max-w-md w-full mx-4">
      <h1 className="text-3xl font-bold text-white mb-8 text-center">DomainSentry</h1>
      <div className="space-y-4">
        <p className="text-gray-300 text-center">Demo mode - no login required.</p>
        <a href="/" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-xl font-medium block text-center transition-all duration-200">
          Enter Dashboard
        </a>
      </div>
    </div>
  </div>
);