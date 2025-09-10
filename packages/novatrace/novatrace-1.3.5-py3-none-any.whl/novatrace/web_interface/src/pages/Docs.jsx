import React, { useState, useEffect } from 'react';
import { ExternalLink, Book, FileText, Code2, Sparkles } from 'lucide-react';

const Docs = () => {
    const [webUrl, setWebUrl] = useState('');

    useEffect(() => {
        // Usar la URL actual del navegador (puerto web)
        const currentUrl = window.location.origin;
        setWebUrl(currentUrl);
    }, []);

    const openSwaggerDocs = () => {
        window.open(`${webUrl}/api/docs`, '_blank');
    };

    const openReDocDocs = () => {
        window.open(`${webUrl}/api/redoc`, '_blank');
    };

    const openOpenAPISpec = () => {
        window.open(`${webUrl}/api/openapi.json`, '_blank');
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-6 text-white">
                <div className="flex items-center space-x-3 mb-4">
                    <Book size={32} />
                    <div>
                        <h1 className="text-3xl font-bold">NovaTrace API Documentation</h1>
                    </div>
                </div>
                <p className="text-blue-100 text-lg">
                    Complete API reference for NovaTrace - AI Agent and LLM Tracing Platform
                </p>
                <div className="mt-4 flex items-center space-x-4 text-sm">
                    <span>Web URL: <code className="bg-blue-500 px-2 py-1 rounded">{webUrl}</code></span>
                    <span>Documentation: <code className="bg-blue-500 px-2 py-1 rounded">{webUrl}/api/docs</code></span>
                </div>
            </div>

            {/* Interactive Documentation Options */}
            <div className="grid md:grid-cols-3 gap-6">
                {/* Swagger UI */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2 bg-green-100 rounded-lg">
                            <Sparkles className="text-green-600" size={24} />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900">Swagger UI</h3>
                            <p className="text-sm text-gray-500">Interactive API Explorer</p>
                        </div>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Test API endpoints directly in your browser. Perfect for development and testing.
                    </p>
                    <ul className="text-sm text-gray-600 mb-4 space-y-1">
                        <li>• Interactive request forms</li>
                        <li>• Real-time response preview</li>
                        <li>• Authentication testing</li>
                        <li>• Request/response examples</li>
                    </ul>
                    <button
                        onClick={openSwaggerDocs}
                        className="w-full flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                        <span>Open Swagger UI</span>
                        <ExternalLink size={16} />
                    </button>
                </div>

                {/* ReDoc */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2 bg-purple-100 rounded-lg">
                            <FileText className="text-purple-600" size={24} />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900">ReDoc</h3>
                            <p className="text-sm text-gray-500">Clean Documentation</p>
                        </div>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Beautiful, clean documentation with a focus on readability and navigation.
                    </p>
                    <ul className="text-sm text-gray-600 mb-4 space-y-1">
                        <li>• Clean, modern interface</li>
                        <li>• Searchable documentation</li>
                        <li>• Mobile-friendly design</li>
                        <li>• Schema visualization</li>
                    </ul>
                    <button
                        onClick={openReDocDocs}
                        className="w-full flex items-center justify-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                    >
                        <span>Open ReDoc</span>
                        <ExternalLink size={16} />
                    </button>
                </div>

                {/* OpenAPI Spec */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2 bg-orange-100 rounded-lg">
                            <Code2 className="text-orange-600" size={24} />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900">OpenAPI Spec</h3>
                            <p className="text-sm text-gray-500">Raw JSON Schema</p>
                        </div>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Download the raw OpenAPI 3.0 specification for code generation and tooling.
                    </p>
                    <ul className="text-sm text-gray-600 mb-4 space-y-1">
                        <li>• Machine-readable format</li>
                        <li>• Code generation ready</li>
                        <li>• Tool integration</li>
                        <li>• Complete schema definition</li>
                    </ul>
                    <button
                        onClick={openOpenAPISpec}
                        className="w-full flex items-center justify-center space-x-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                    >
                        <span>View JSON Spec</span>
                        <ExternalLink size={16} />
                    </button>
                </div>
            </div>

            {/* Authentication Guide */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-amber-800 mb-4 flex items-center">
                    🔐 Authentication Guide
                </h3>
                <div className="space-y-4 text-amber-700">
                    <div className="bg-white border border-amber-200 rounded-lg p-4">
                        <h4 className="font-medium text-amber-800 mb-2">1. Login to get a token:</h4>
                        <div className="bg-gray-900 rounded p-3 text-sm overflow-x-auto">
                            <code className="text-yellow-300">POST</code> <code className="text-green-300">{webUrl}/api/auth/login</code>
                        </div>
                    </div>
                    <div className="bg-white border border-amber-200 rounded-lg p-4">
                        <h4 className="font-medium text-amber-800 mb-2">2. Use the token in requests:</h4>
                        <div className="bg-gray-900 rounded p-3 text-sm">
                            <code className="text-blue-300">Authorization:</code> <code className="text-green-300">Bearer &lt;your-token&gt;</code>
                        </div>
                    </div>
                    <div className="bg-white border border-amber-200 rounded-lg p-4">
                        <h4 className="font-medium text-amber-800">3. Token expires in 24 hours</h4>
                        <p className="text-sm text-amber-600 mt-1">Refresh by logging in again when needed.</p>
                    </div>
                </div>
            </div>

            {/* Quick Start Examples */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">🚀 Quick Start Examples</h3>
                
                <div className="space-y-6">
                    {/* cURL Example */}
                    <div>
                        <h4 className="text-lg font-semibold mb-3 flex items-center">
                            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                            cURL Example
                        </h4>
                        <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
                            <div className="bg-gray-800 px-4 py-2 border-b border-gray-700">
                                <span className="text-gray-300 text-sm font-mono">Terminal</span>
                            </div>
                            <div className="p-4 overflow-x-auto">
                                <pre className="text-sm leading-relaxed">
<span className="text-gray-400"># 1. Login</span>{'\n'}
<span className="text-blue-400">curl</span> <span className="text-yellow-300">-X POST</span> <span className="text-green-300">"{webUrl}/api/auth/login"</span> <span className="text-yellow-300">\</span>{'\n'}
  <span className="text-yellow-300">-H</span> <span className="text-green-300">"Content-Type: application/json"</span> <span className="text-yellow-300">\</span>{'\n'}
  <span className="text-yellow-300">-d</span> <span className="text-green-300">'&#123;"username": "admin", "password": "your_password"&#125;'</span>{'\n'}
{'\n'}
<span className="text-gray-400"># 2. Get projects (replace TOKEN with actual token)</span>{'\n'}
<span className="text-blue-400">curl</span> <span className="text-yellow-300">-X GET</span> <span className="text-green-300">"{webUrl}/api/projects"</span> <span className="text-yellow-300">\</span>{'\n'}
  <span className="text-yellow-300">-H</span> <span className="text-green-300">"Authorization: Bearer TOKEN"</span>
                                </pre>
                            </div>
                        </div>
                    </div>

                    {/* JavaScript Example */}
                    <div>
                        <h4 className="text-lg font-semibold mb-3 flex items-center">
                            <span className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                            JavaScript Example
                        </h4>
                        <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
                            <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
                                <span className="text-gray-300 text-sm font-mono">script.js</span>
                                <span className="text-xs bg-yellow-600 text-yellow-100 px-2 py-1 rounded">JavaScript</span>
                            </div>
                            <div className="p-4 overflow-x-auto">
                                <pre className="text-sm leading-relaxed">
<span className="text-gray-400">// 1. Login</span>{'\n'}
<span className="text-purple-400">const</span> <span className="text-blue-300">loginResponse</span> <span className="text-white">=</span> <span className="text-purple-400">await</span> <span className="text-yellow-300">fetch</span><span className="text-white">(</span><span className="text-green-300">'{webUrl}/api/auth/login'</span><span className="text-white">, &#123;</span>{'\n'}
  <span className="text-red-300">method</span><span className="text-white">:</span> <span className="text-green-300">'POST'</span><span className="text-white">,</span>{'\n'}
  <span className="text-red-300">headers</span><span className="text-white">:</span> <span className="text-white">&#123;</span> <span className="text-green-300">'Content-Type'</span><span className="text-white">:</span> <span className="text-green-300">'application/json'</span> <span className="text-white">&#125;</span><span className="text-white">,</span>{'\n'}
  <span className="text-red-300">body</span><span className="text-white">:</span> <span className="text-blue-300">JSON</span><span className="text-white">.</span><span className="text-yellow-300">stringify</span><span className="text-white">(&#123;</span> <span className="text-red-300">username</span><span className="text-white">:</span> <span className="text-green-300">'admin'</span><span className="text-white">,</span> <span className="text-red-300">password</span><span className="text-white">:</span> <span className="text-green-300">'your_password'</span> <span className="text-white">&#125;)</span>{'\n'}
<span className="text-white">&#125;);</span>{'\n'}
<span className="text-purple-400">const</span> <span className="text-white">&#123;</span> <span className="text-blue-300">access_token</span> <span className="text-white">&#125;</span> <span className="text-white">=</span> <span className="text-purple-400">await</span> <span className="text-blue-300">loginResponse</span><span className="text-white">.</span><span className="text-yellow-300">json</span><span className="text-white">();</span>{'\n'}
{'\n'}
<span className="text-gray-400">// 2. Get projects</span>{'\n'}
<span className="text-purple-400">const</span> <span className="text-blue-300">projectsResponse</span> <span className="text-white">=</span> <span className="text-purple-400">await</span> <span className="text-yellow-300">fetch</span><span className="text-white">(</span><span className="text-green-300">'{webUrl}/api/projects'</span><span className="text-white">, &#123;</span>{'\n'}
  <span className="text-red-300">headers</span><span className="text-white">:</span> <span className="text-white">&#123;</span> <span className="text-green-300">'Authorization'</span><span className="text-white">:</span> <span className="text-green-300">`Bearer $&#123;access_token&#125;`</span> <span className="text-white">&#125;</span>{'\n'}
<span className="text-white">&#125;);</span>{'\n'}
<span className="text-purple-400">const</span> <span className="text-blue-300">projects</span> <span className="text-white">=</span> <span className="text-purple-400">await</span> <span className="text-blue-300">projectsResponse</span><span className="text-white">.</span><span className="text-yellow-300">json</span><span className="text-white">();</span>
                                </pre>
                            </div>
                        </div>
                    </div>

                    {/* Python Example */}
                    <div>
                        <h4 className="text-lg font-semibold mb-3 flex items-center">
                            <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                            Python Example
                        </h4>
                        <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
                            <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
                                <span className="text-gray-300 text-sm font-mono">main.py</span>
                                <span className="text-xs bg-blue-600 text-blue-100 px-2 py-1 rounded">Python</span>
                            </div>
                            <div className="p-4 overflow-x-auto">
                                <pre className="text-sm leading-relaxed">
<span className="text-purple-400">import</span> <span className="text-blue-300">requests</span>{'\n'}
{'\n'}
<span className="text-gray-400"># 1. Login</span>{'\n'}
<span className="text-blue-300">login_response</span> <span className="text-white">=</span> <span className="text-blue-300">requests</span><span className="text-white">.</span><span className="text-yellow-300">post</span><span className="text-white">(</span><span className="text-green-300">'{webUrl}/api/auth/login'</span><span className="text-white">,</span> {'\n'}
    <span className="text-red-300">json</span><span className="text-white">=&#123;</span><span className="text-green-300">'username'</span><span className="text-white">:</span> <span className="text-green-300">'admin'</span><span className="text-white">,</span> <span className="text-green-300">'password'</span><span className="text-white">:</span> <span className="text-green-300">'your_password'</span><span className="text-white">&#125;</span><span className="text-white">)</span>{'\n'}
<span className="text-blue-300">token</span> <span className="text-white">=</span> <span className="text-blue-300">login_response</span><span className="text-white">.</span><span className="text-yellow-300">json</span><span className="text-white">()</span><span className="text-white">[</span><span className="text-green-300">'access_token'</span><span className="text-white">]</span>{'\n'}
{'\n'}
<span className="text-gray-400"># 2. Get projects</span>{'\n'}
<span className="text-blue-300">projects_response</span> <span className="text-white">=</span> <span className="text-blue-300">requests</span><span className="text-white">.</span><span className="text-yellow-300">get</span><span className="text-white">(</span><span className="text-green-300">'{webUrl}/api/projects'</span><span className="text-white">,</span>{'\n'}
    <span className="text-red-300">headers</span><span className="text-white">=&#123;</span><span className="text-green-300">'Authorization'</span><span className="text-white">:</span> <span className="text-green-300">f'Bearer &#123;</span><span className="text-blue-300">token</span><span className="text-green-300">&#125;'</span><span className="text-white">&#125;</span><span className="text-white">)</span>{'\n'}
<span className="text-blue-300">projects</span> <span className="text-white">=</span> <span className="text-blue-300">projects_response</span><span className="text-white">.</span><span className="text-yellow-300">json</span><span className="text-white">()</span>
                                </pre>
                            </div>
                        </div>
                    </div>

                    {/* Response Example */}
                    <div>
                        <h4 className="text-lg font-semibold mb-3 flex items-center">
                            <span className="w-3 h-3 bg-purple-500 rounded-full mr-2"></span>
                            Example Response
                        </h4>
                        <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
                            <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
                                <span className="text-gray-300 text-sm font-mono">response.json</span>
                                <span className="text-xs bg-purple-600 text-purple-100 px-2 py-1 rounded">JSON</span>
                            </div>
                            <div className="p-4 overflow-x-auto">
                                <pre className="text-sm leading-relaxed">
<span className="text-white">&#123;</span>{'\n'}
  <span className="text-blue-300">"access_token"</span><span className="text-white">:</span> <span className="text-green-300">"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."</span><span className="text-white">,</span>{'\n'}
  <span className="text-blue-300">"token_type"</span><span className="text-white">:</span> <span className="text-green-300">"bearer"</span><span className="text-white">,</span>{'\n'}
  <span className="text-blue-300">"username"</span><span className="text-white">:</span> <span className="text-green-300">"admin"</span>{'\n'}
<span className="text-white">&#125;</span>
                                </pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* API Categories */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">📚 API Categories</h3>
                <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h4 className="font-semibold text-blue-900">Authentication</h4>
                        <p className="text-blue-700 text-sm mt-1">Login, user info, password management</p>
                    </div>
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                        <h4 className="font-semibold text-green-900">Projects</h4>
                        <p className="text-green-700 text-sm mt-1">Project management, metrics, traces</p>
                    </div>
                    <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                        <h4 className="font-semibold text-purple-900">Sessions</h4>
                        <p className="text-purple-700 text-sm mt-1">Session management within projects</p>
                    </div>
                    <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                        <h4 className="font-semibold text-orange-900">System</h4>
                        <p className="text-orange-700 text-sm mt-1">System metrics and status monitoring</p>
                    </div>
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                        <h4 className="font-semibold text-red-900">Users</h4>
                        <p className="text-red-700 text-sm mt-1">User management (admin only)</p>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="text-center text-gray-500 text-sm py-4 border-t border-gray-200">
                <p>NovaTrace API Documentation - Auto-generated from OpenAPI specification</p>
                <p className="mt-1">For detailed endpoint information, use the interactive documentation above</p>
            </div>
        </div>
    );
};

export default Docs;
