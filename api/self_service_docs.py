"""
Self-Service Documentation & SDK Examples
Provides code snippets and examples for every endpoint
"""

from flask import Blueprint, jsonify, render_template_string
from flask_cors import cross_origin
import logging

logger = logging.getLogger(__name__)

# Create documentation blueprint
docs_bp = Blueprint('docs', __name__, url_prefix='/api/docs')

# SDK Examples for different languages
SDK_EXAMPLES = {
    'python': {
        'installation': """
# Install using pip
pip install crypto-trading-sdk

# Or using the requests library directly
pip install requests
""",
        'basic_usage': """
import requests
import json

class CryptoTradingAPI:
    def __init__(self, base_url='http://localhost:5000', api_version='v2'):
        self.base_url = base_url
        self.api_version = api_version
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Version': api_version
        })
    
    def generate_signal(self, symbol='BTC-USDT', timeframe='1H'):
        url = f"{self.base_url}/api/{self.api_version}/signals/generate"
        params = {'symbol': symbol, 'timeframe': timeframe}
        response = self.session.get(url, params=params)
        return response.json()
    
    def get_risk_profile(self, profile='MODERATE', balance=10000):
        url = f"{self.base_url}/api/{self.api_version}/risk-management/profile"
        params = {'profile': profile, 'account_balance': balance}
        response = self.session.get(url, params=params)
        return response.json()
    
    def smc_analysis(self, symbol='BTC-USDT'):
        url = f"{self.base_url}/api/{self.api_version}/smc/analyze"
        params = {'symbol': symbol}
        response = self.session.get(url, params=params)
        return response.json()

# Usage example
api = CryptoTradingAPI()

# Get trading signal
signal = api.generate_signal('BTC-USDT', '1H')
print(f"Signal: {signal['data']['signal']}, Confidence: {signal['data']['confidence']}%")

# Get risk profile
risk = api.get_risk_profile('CONSERVATIVE', 50000)
print(f"Risk Profile: {risk['profile']['current_profile']}")

# Get SMC analysis
smc = api.smc_analysis('ETH-USDT')
print(f"SMC Analysis: {smc['data']['analysis']}")
""",
        'advanced_usage': """
# Advanced example with error handling and async support
import asyncio
import aiohttp

class AsyncCryptoTradingAPI:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        
    async def fetch(self, session, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            async with session.get(url, params=params) as response:
                return await response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def multi_symbol_analysis(self, symbols):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in symbols:
                tasks.append(self.fetch(session, '/api/v2/signals/generate', {'symbol': symbol}))
            
            results = await asyncio.gather(*tasks)
            return dict(zip(symbols, results))

# Usage
async def main():
    api = AsyncCryptoTradingAPI()
    symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
    results = await api.multi_symbol_analysis(symbols)
    
    for symbol, data in results.items():
        print(f"{symbol}: {data}")

# Run async
asyncio.run(main())
"""
    },
    
    'javascript': {
        'installation': """
// Using npm
npm install crypto-trading-sdk

// Or using fetch API (built-in)
// No installation needed
""",
        'basic_usage': """
// Basic JavaScript/Node.js SDK
class CryptoTradingAPI {
    constructor(baseUrl = 'http://localhost:5000', apiVersion = 'v2') {
        this.baseUrl = baseUrl;
        this.apiVersion = apiVersion;
    }
    
    async generateSignal(symbol = 'BTC-USDT', timeframe = '1H') {
        const url = `${this.baseUrl}/api/${this.apiVersion}/signals/generate`;
        const params = new URLSearchParams({ symbol, timeframe });
        
        try {
            const response = await fetch(`${url}?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Version': this.apiVersion
                }
            });
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { error: error.message };
        }
    }
    
    async getRiskProfile(profile = 'MODERATE', balance = 10000) {
        const url = `${this.baseUrl}/api/${this.apiVersion}/risk-management/profile`;
        const params = new URLSearchParams({ 
            profile, 
            account_balance: balance 
        });
        
        const response = await fetch(`${url}?${params}`);
        return await response.json();
    }
    
    async smcAnalysis(symbol = 'BTC-USDT') {
        const url = `${this.baseUrl}/api/${this.apiVersion}/smc/analyze`;
        const params = new URLSearchParams({ symbol });
        
        const response = await fetch(`${url}?${params}`);
        return await response.json();
    }
}

// Usage example
const api = new CryptoTradingAPI();

// Get trading signal
api.generateSignal('BTC-USDT', '1H').then(signal => {
    console.log(`Signal: ${signal.data.signal}, Confidence: ${signal.data.confidence}%`);
});

// Get risk profile
api.getRiskProfile('AGGRESSIVE', 100000).then(risk => {
    console.log(`Risk Profile:`, risk.profile);
});

// Get SMC analysis
api.smcAnalysis('ETH-USDT').then(smc => {
    console.log(`SMC Analysis:`, smc.data);
});
""",
        'react_example': """
// React Hook Example
import { useState, useEffect } from 'react';

const useCryptoSignal = (symbol = 'BTC-USDT', timeframe = '1H') => {
    const [signal, setSignal] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const fetchSignal = async () => {
            try {
                setLoading(true);
                const response = await fetch(
                    `http://localhost:5000/api/v2/signals/generate?symbol=${symbol}&timeframe=${timeframe}`
                );
                const data = await response.json();
                setSignal(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        
        fetchSignal();
        
        // Refresh every 5 minutes
        const interval = setInterval(fetchSignal, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, [symbol, timeframe]);
    
    return { signal, loading, error };
};

// Component usage
function TradingSignal() {
    const { signal, loading, error } = useCryptoSignal('BTC-USDT', '1H');
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            <h2>Trading Signal</h2>
            <p>Action: {signal?.data?.signal}</p>
            <p>Confidence: {signal?.data?.confidence}%</p>
        </div>
    );
}
"""
    },
    
    'go': {
        'installation': """
// Install using go get
go get github.com/your-org/crypto-trading-sdk-go

// Or create your own client
// No external dependencies needed
""",
        'basic_usage': """
package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
    "net/url"
)

type CryptoTradingAPI struct {
    BaseURL    string
    APIVersion string
    Client     *http.Client
}

type SignalResponse struct {
    Version string `json:"version"`
    Data    struct {
        Signal     string  `json:"signal"`
        Confidence float64 `json:"confidence"`
    } `json:"data"`
}

func NewCryptoTradingAPI() *CryptoTradingAPI {
    return &CryptoTradingAPI{
        BaseURL:    "http://localhost:5000",
        APIVersion: "v2",
        Client:     &http.Client{},
    }
}

func (api *CryptoTradingAPI) GenerateSignal(symbol, timeframe string) (*SignalResponse, error) {
    params := url.Values{}
    params.Add("symbol", symbol)
    params.Add("timeframe", timeframe)
    
    url := fmt.Sprintf("%s/api/%s/signals/generate?%s", 
        api.BaseURL, api.APIVersion, params.Encode())
    
    req, err := http.NewRequest("GET", url, nil)
    if err != nil {
        return nil, err
    }
    
    req.Header.Add("Content-Type", "application/json")
    req.Header.Add("X-API-Version", api.APIVersion)
    
    resp, err := api.Client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }
    
    var signal SignalResponse
    err = json.Unmarshal(body, &signal)
    if err != nil {
        return nil, err
    }
    
    return &signal, nil
}

func main() {
    api := NewCryptoTradingAPI()
    
    // Get trading signal
    signal, err := api.GenerateSignal("BTC-USDT", "1H")
    if err != nil {
        fmt.Printf("Error: %v\\n", err)
        return
    }
    
    fmt.Printf("Signal: %s, Confidence: %.2f%%\\n", 
        signal.Data.Signal, signal.Data.Confidence)
}
"""
    },
    
    'curl': {
        'basic_usage': """
# Basic cURL examples

# 1. Generate Trading Signal
curl -X GET "http://localhost:5000/api/v2/signals/generate?symbol=BTC-USDT&timeframe=1H" \\
     -H "Content-Type: application/json" \\
     -H "X-API-Version: v2"

# 2. Get Risk Profile
curl -X GET "http://localhost:5000/api/v2/risk-management/profile?profile=MODERATE&account_balance=10000" \\
     -H "Content-Type: application/json"

# 3. SMC Analysis
curl -X GET "http://localhost:5000/api/v2/smc/analyze?symbol=ETH-USDT" \\
     -H "Content-Type: application/json"

# 4. Multi-Timeframe Analysis
curl -X GET "http://localhost:5000/api/v2/analysis/multi-timeframe?symbol=BTC-USDT"

# 5. POST Request with JSON Body
curl -X POST "http://localhost:5000/api/v2/signals/generate" \\
     -H "Content-Type: application/json" \\
     -d '{"symbol": "BTC-USDT", "timeframe": "4H", "confidence_threshold": 80}'

# 6. Batch Analysis
curl -X POST "http://localhost:5000/api/v2/batch/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{"symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT"]}'
"""
    }
}

# Endpoint documentation
ENDPOINT_DOCS = {
    '/api/v2/signals/generate': {
        'description': 'Generate trading signals with AI analysis',
        'methods': ['GET', 'POST'],
        'parameters': {
            'symbol': 'Trading pair (e.g., BTC-USDT)',
            'timeframe': 'Time interval (1m, 5m, 15m, 30m, 1H, 4H, 1D)',
            'confidence_threshold': 'Minimum confidence level (0-100)'
        },
        'response': {
            'signal': 'BUY/SELL/HOLD',
            'confidence': 'Confidence percentage',
            'analysis': 'Detailed analysis',
            'risk_level': 'LOW/MEDIUM/HIGH'
        }
    },
    '/api/v2/risk-management/profile': {
        'description': 'Manage personalized risk profiles',
        'methods': ['GET', 'POST'],
        'parameters': {
            'profile': 'CONSERVATIVE/MODERATE/AGGRESSIVE',
            'account_balance': 'Account balance in USD',
            'symbol': 'Optional: specific symbol for analysis'
        },
        'response': {
            'profile': 'Current risk profile',
            'settings': 'Profile configuration',
            'recommendations': 'Trading recommendations'
        }
    },
    '/api/v2/smc/analyze': {
        'description': 'Smart Money Concept analysis',
        'methods': ['GET', 'POST'],
        'parameters': {
            'symbol': 'Trading pair',
            'timeframe': 'Time interval',
            'include_choch': 'Include CHoCH analysis',
            'include_fvg': 'Include Fair Value Gaps'
        },
        'response': {
            'market_structure': 'Current market structure',
            'order_blocks': 'Identified order blocks',
            'liquidity_zones': 'Liquidity areas',
            'choch': 'Change of Character detection'
        }
    }
}

@docs_bp.route('/', methods=['GET'])
@cross_origin()
def documentation_home():
    """Main documentation page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .section { margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 5px; }
            .endpoint { background: #fff; padding: 10px; margin: 10px 0; border-left: 3px solid #007bff; }
            code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; }
            pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🚀 Crypto Trading API Documentation</h1>
        
        <div class="section">
            <h2>Quick Start</h2>
            <p>Base URL: <code>http://localhost:5000</code></p>
            <p>Current Version: <code>v2</code></p>
            <p>Authentication: <code>API Key (coming soon)</code></p>
        </div>
        
        <div class="section">
            <h2>Available SDKs</h2>
            <ul>
                <li><a href="/api/docs/sdk/python">Python SDK & Examples</a></li>
                <li><a href="/api/docs/sdk/javascript">JavaScript/Node.js SDK & Examples</a></li>
                <li><a href="/api/docs/sdk/go">Go SDK & Examples</a></li>
                <li><a href="/api/docs/sdk/curl">cURL Examples</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Main Endpoints</h2>
            <ul>
                <li><a href="/api/docs/endpoint?path=/api/v2/signals/generate">Signal Generation</a></li>
                <li><a href="/api/docs/endpoint?path=/api/v2/risk-management/profile">Risk Management</a></li>
                <li><a href="/api/docs/endpoint?path=/api/v2/smc/analyze">SMC Analysis</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>API Versioning</h2>
            <p>We maintain backward compatibility with clear versioning:</p>
            <ul>
                <li><strong>v2</strong> (Current) - Enhanced features and structure</li>
                <li><strong>v1</strong> (Deprecated) - Will be sunset on 2026-02-01</li>
            </ul>
            <p>Always use the latest version for new integrations.</p>
        </div>
    </body>
    </html>
    """
    return html

@docs_bp.route('/sdk/<language>', methods=['GET'])
@cross_origin()
def get_sdk_examples(language):
    """Get SDK examples for specific language"""
    if language not in SDK_EXAMPLES:
        return jsonify({
            'error': f'SDK examples not available for {language}',
            'available': list(SDK_EXAMPLES.keys())
        }), 404
    
    examples = SDK_EXAMPLES[language]
    
    # Format as HTML for better readability
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{language.title()} SDK Examples</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-tomorrow.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .example {{ margin: 20px 0; }}
            pre {{ border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>{language.title()} SDK Examples</h1>
        <a href="/api/docs/">← Back to Documentation</a>
        
        {"".join(f'''
        <div class="example">
            <h2>{key.replace('_', ' ').title()}</h2>
            <pre><code class="language-{language}">{value}</code></pre>
        </div>
        ''' for key, value in examples.items())}
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-javascript.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-go.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-bash.min.js"></script>
    </body>
    </html>
    """
    
    return html

@docs_bp.route('/endpoint', methods=['GET'])
@cross_origin()
def get_endpoint_docs():
    """Get documentation for specific endpoint"""
    endpoint_path = request.args.get('path')
    
    if endpoint_path not in ENDPOINT_DOCS:
        return jsonify({
            'error': f'Documentation not found for {endpoint_path}',
            'available_endpoints': list(ENDPOINT_DOCS.keys())
        }), 404
    
    return jsonify(ENDPOINT_DOCS[endpoint_path])

@docs_bp.route('/openapi', methods=['GET'])
@cross_origin()
def get_openapi_spec():
    """Get OpenAPI specification"""
    return jsonify({
        'openapi': '3.1.0',
        'info': {
            'title': 'Crypto Trading API',
            'version': '2.0.0',
            'description': 'AI-powered cryptocurrency trading analysis platform'
        },
        'servers': [
            {'url': 'http://localhost:5000/api/v2', 'description': 'Local development'},
            {'url': 'https://api.example.com/v2', 'description': 'Production'}
        ],
        'paths': ENDPOINT_DOCS
    })

logger.info("📚 Self-Service Documentation initialized with SDK examples")