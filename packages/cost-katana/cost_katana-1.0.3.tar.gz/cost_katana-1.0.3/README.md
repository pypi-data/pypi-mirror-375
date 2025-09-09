# Cost Katana Python SDK

A simple, unified interface for AI models with built-in cost optimization, failover, and analytics. Use any AI provider through one consistent API - no need to manage API keys or worry about provider-specific implementations!

## 🚀 Quick Start

### Installation

```bash
pip install cost-katana
```

### Get Your API Key

1. Visit [Cost Katana Dashboard](https://costkatana.com/dashboard)
2. Create an account or sign in
3. Go to API Keys section
4. Generate a new API key (starts with `dak_`)

### Basic Usage

```python
import cost_katana as ck

# Configure once with your API key
ck.configure(api_key='dak_your_key_here')

# Use any AI model with the same simple interface
model = ck.GenerativeModel('nova-lite')
response = model.generate_content("Explain quantum computing in simple terms")
print(response.text)
print(f"Cost: ${response.usage_metadata.cost:.4f}")
```

### Chat Sessions

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')

# Start a conversation
model = ck.GenerativeModel('claude-3-sonnet')
chat = model.start_chat()

# Send messages back and forth
response1 = chat.send_message("Hello! What's your name?")
print("AI:", response1.text)

response2 = chat.send_message("Can you help me write a Python function?")
print("AI:", response2.text)

# Get total conversation cost
total_cost = sum(msg.get('metadata', {}).get('cost', 0) for msg in chat.history)
print(f"Total conversation cost: ${total_cost:.4f}")
```

## 🎯 Why Cost Katana?

### Simple Interface, Powerful Backend
- **One API for all providers**: Use Google Gemini, Anthropic Claude, OpenAI GPT, AWS Bedrock models through one interface
- **No API key juggling**: Store your provider keys securely in Cost Katana, use one key in your code
- **Automatic failover**: If one provider is down, automatically switch to alternatives
- **Cost optimization**: Intelligent routing to minimize costs while maintaining quality

### Enterprise Features
- **Cost tracking**: Real-time cost monitoring and budgets
- **Usage analytics**: Detailed insights into model performance and usage patterns  
- **Team management**: Share projects and manage API usage across teams
- **Approval workflows**: Set spending limits with approval requirements

## 📚 Configuration Options

### Using Configuration File (Recommended)

Create `config.json`:

```json
{
  "api_key": "dak_your_key_here",
  "default_model": "gemini-2.0-flash",
  "default_temperature": 0.7,
  "cost_limit_per_day": 50.0,
  "enable_optimization": true,
  "enable_failover": true,
  "model_mappings": {
    "gemini": "gemini-2.0-flash-exp",
    "claude": "anthropic.claude-3-sonnet-20240229-v1:0",
    "gpt4": "gpt-4-turbo-preview"
  },
  "providers": {
    "google": {
      "priority": 1,
      "models": ["gemini-2.0-flash", "gemini-pro"]
    },
    "anthropic": {
      "priority": 2, 
      "models": ["claude-3-sonnet", "claude-3-haiku"]
    }
  }
}
```

```python
import cost_katana as ck

# Configure from file
ck.configure(config_file='config.json')

# Now use any model
model = ck.GenerativeModel('gemini')  # Uses mapping from config
```

### Environment Variables

```bash
export API_KEY=dak_your_key_here
export COST_KATANA_DEFAULT_MODEL=claude-3-sonnet
```

```python
import cost_katana as ck

# Automatically loads from environment
ck.configure()

model = ck.GenerativeModel()  # Uses default model from env
```

## 🤖 Supported Models

### Amazon Nova Models (Primary Recommendation)
- `nova-micro` - Ultra-fast and cost-effective for simple tasks
- `nova-lite` - Balanced performance and cost for general use
- `nova-pro` - High-performance model for complex tasks

### Anthropic Claude Models  
- `claude-3-haiku` - Fast and cost-effective responses
- `claude-3-sonnet` - Balanced performance for complex tasks
- `claude-3-opus` - Most capable Claude model for advanced reasoning
- `claude-3.5-haiku` - Latest fast model with enhanced capabilities
- `claude-3.5-sonnet` - Advanced reasoning and analysis

### Meta Llama Models
- `llama-3.1-8b` - Good balance of performance and efficiency
- `llama-3.1-70b` - Large model for complex reasoning
- `llama-3.1-405b` - Most capable Llama model
- `llama-3.2-1b` - Compact and efficient
- `llama-3.2-3b` - Efficient for general tasks

### Mistral Models
- `mistral-7b` - Efficient open-source model
- `mixtral-8x7b` - High-quality mixture of experts
- `mistral-large` - Advanced reasoning capabilities

### Cohere Models
- `command` - General purpose text generation
- `command-light` - Lighter, faster version
- `command-r` - Retrieval-augmented generation
- `command-r-plus` - Enhanced RAG with better reasoning

### Friendly Aliases
- `fast` → Nova Micro (optimized for speed)  
- `balanced` → Nova Lite (balanced cost/performance)
- `powerful` → Nova Pro (maximum capabilities)

## ⚙️ Advanced Usage

### Generation Configuration

```python
from cost_katana import GenerativeModel, GenerationConfig

config = GenerationConfig(
    temperature=0.3,
    max_output_tokens=1000,
    top_p=0.9
)

model = GenerativeModel('claude-3-sonnet', generation_config=config)
response = model.generate_content("Write a haiku about programming")
```

### Multi-Agent Processing

```python
# Enable multi-agent processing for complex queries
model = GenerativeModel('gemini-2.0-flash')
response = model.generate_content(
    "Analyze the economic impact of AI on job markets",
    use_multi_agent=True,
    chat_mode='balanced'
)

# See which agents were involved
print("Agent path:", response.usage_metadata.agent_path)
print("Optimizations applied:", response.usage_metadata.optimizations_applied)
```

### Cost Optimization Modes

```python
# Different optimization strategies
fast_response = model.generate_content(
    "Quick summary of today's news",
    chat_mode='fastest'  # Prioritize speed
)

cheap_response = model.generate_content(
    "Detailed analysis of market trends", 
    chat_mode='cheapest'  # Prioritize cost
)

balanced_response = model.generate_content(
    "Help me debug this Python code",
    chat_mode='balanced'  # Balance speed and cost
)
```

## 🖥️ Command Line Interface

Cost Katana includes a comprehensive CLI for easy interaction:

```bash
# Initialize configuration
cost-katana init

# Test your setup
cost-katana test

# List available models
cost-katana models

# Start interactive chat
cost-katana chat --model gemini-2.0-flash

# Use specific config file
cost-katana chat --config my-config.json
```

## 🧬 SAST (Semantic Abstract Syntax Tree) Features

Cost Katana includes advanced SAST capabilities for semantic optimization and analysis:

### SAST Optimization

```bash
# Optimize a prompt using SAST
cost-katana sast optimize "Write a detailed analysis of market trends"

# Optimize from file
cost-katana sast optimize --file prompt.txt --output optimized.txt

# Cross-lingual optimization
cost-katana sast optimize "Analyze data" --cross-lingual --language en

# Preserve ambiguity for analysis
cost-katana sast optimize "Complex query" --preserve-ambiguity
```

### SAST Comparison

```bash
# Compare traditional vs SAST optimization
cost-katana sast compare "Your prompt here"

# Compare with specific language
cost-katana sast compare --file prompt.txt --language en
```

### SAST Vocabulary & Analytics

```bash
# Explore SAST vocabulary
cost-katana sast vocabulary

# Search semantic primitives
cost-katana sast vocabulary --search "analysis" --category "action"

# Get SAST performance statistics
cost-katana sast stats

# View SAST showcase with examples
cost-katana sast showcase

# Telescope ambiguity demonstration
cost-katana sast telescope

# Test universal semantics across languages
cost-katana sast universal "concept" --languages "en,es,fr"
```

### SAST Python API

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')
client = ck.CostKatanaClient()

# Optimize with SAST
result = client.optimize_with_sast(
    prompt="Your prompt here",
    language="en",
    cross_lingual=True,
    preserve_ambiguity=False
)

# Compare SAST vs traditional
comparison = client.compare_sast_vs_traditional(
    prompt="Your prompt here",
    language="en"
)

# Get SAST vocabulary stats
stats = client.get_sast_vocabulary_stats()

# Search semantic primitives
primitives = client.search_semantic_primitives(
    term="analysis",
    category="action",
    limit=10
)

# Test universal semantics
universal_test = client.test_universal_semantics(
    concept="love",
    languages=["en", "es", "fr"]
)
```

## 🧠 Cortex Engine Features

Cost Katana's Cortex engine provides intelligent processing capabilities:

### Cortex Operations

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')
client = ck.CostKatanaClient()

# Enable Cortex with SAST processing
result = client.optimize_with_sast(
    prompt="Your prompt",
    service="openai",
    model="gpt-4o-mini",
    # Cortex features
    enableCortex=True,
    cortexOperation="sast",
    cortexStyle="conversational",
    cortexFormat="plain",
    cortexSemanticCache=True,
    cortexPreserveSemantics=True,
    cortexIntelligentRouting=True,
    cortexSastProcessing=True,
    cortexAmbiguityResolution=True,
    cortexCrossLingualMode=False
)
```

### Cortex Capabilities

- **Semantic Caching**: Intelligent caching of semantic representations
- **Intelligent Routing**: Smart routing based on content analysis
- **Ambiguity Resolution**: Automatic resolution of ambiguous language
- **Cross-lingual Processing**: Multi-language semantic understanding
- **Semantic Preservation**: Maintains semantic meaning during optimization

## 🌐 Gateway Features

Cost Katana acts as a unified gateway to multiple AI providers:

### Provider Abstraction

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')

# Same interface, different providers
models = [
    'nova-lite',           # Amazon Nova
    'claude-3-sonnet',     # Anthropic Claude
    'gemini-2.0-flash',    # Google Gemini
    'gpt-4',               # OpenAI GPT
    'llama-3.1-70b'        # Meta Llama
]

for model in models:
    response = ck.GenerativeModel(model).generate_content("Hello!")
    print(f"{model}: {response.text[:50]}...")
```

### Intelligent Routing

```python
# Cost Katana automatically routes to the best provider
model = ck.GenerativeModel('balanced')  # Uses intelligent routing

# Different optimization modes
fast_response = model.generate_content(
    "Quick summary",
    chat_mode='fastest'    # Routes to fastest provider
)

cheap_response = model.generate_content(
    "Detailed analysis",
    chat_mode='cheapest'   # Routes to most cost-effective provider
)

balanced_response = model.generate_content(
    "Complex reasoning",
    chat_mode='balanced'   # Balances speed and cost
)
```

### Failover & Redundancy

```python
# Automatic failover if primary provider is down
model = ck.GenerativeModel('claude-3-sonnet')

try:
    response = model.generate_content("Your prompt")
except ck.ModelNotAvailableError:
    # Cost Katana automatically tries alternative providers
    print("Primary model unavailable, using fallback...")
    response = model.generate_content("Your prompt")
```

## 📊 Usage Analytics

Track your AI usage and costs:

```python
import cost_katana as ck

ck.configure(config_file='config.json')

model = ck.GenerativeModel('claude-3-sonnet')
response = model.generate_content("Explain machine learning")

# Detailed usage information
metadata = response.usage_metadata
print(f"Model used: {metadata.model}")
print(f"Cost: ${metadata.cost:.4f}")
print(f"Latency: {metadata.latency:.2f}s")
print(f"Tokens: {metadata.total_tokens}")
print(f"Cache hit: {metadata.cache_hit}")
print(f"Risk level: {metadata.risk_level}")
```

## 🔧 Error Handling

```python
from cost_katana import GenerativeModel
from cost_katana.exceptions import (
    CostLimitExceededError,
    ModelNotAvailableError,
    RateLimitError
)

try:
    model = GenerativeModel('expensive-model')
    response = model.generate_content("Complex analysis task")
    
except CostLimitExceededError:
    print("Cost limit reached! Check your budget settings.")
    
except ModelNotAvailableError:
    print("Model is currently unavailable. Trying fallback...")
    model = GenerativeModel('backup-model')
    response = model.generate_content("Complex analysis task")
    
except RateLimitError:
    print("Rate limit hit. Please wait before retrying.")
```

## 🌟 Comparison with Direct Provider SDKs

### Before (Google Gemini)
```python
import google.generativeai as genai

# Need to manage API key
genai.configure(api_key="your-google-api-key")

# Provider-specific code
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content("Hello")

# No cost tracking, no failover, provider lock-in
```

### After (Cost Katana)
```python
import cost_katana as ck

# One API key for all providers
ck.configure(api_key='dak_your_key_here')

# Same interface, any provider
model = ck.GenerativeModel('nova-lite')
response = model.generate_content("Hello")

# Built-in cost tracking, failover, optimization
print(f"Cost: ${response.usage_metadata.cost:.4f}")
```

## 🏢 Enterprise Features

- **Team Management**: Share configurations across team members
- **Cost Centers**: Track usage by project or department  
- **Approval Workflows**: Require approval for high-cost operations
- **Analytics Dashboard**: Web interface for usage insights
- **Custom Models**: Support for fine-tuned and custom models
- **SLA Monitoring**: Track model availability and performance

## 🔒 Security & Privacy

- **Secure Key Storage**: API keys encrypted at rest
- **No Data Retention**: Your prompts and responses are not stored
- **Audit Logs**: Complete audit trail of API usage
- **GDPR Compliant**: Full compliance with data protection regulations

## 📖 API Reference

### GenerativeModel

```python
class GenerativeModel:
    def __init__(self, model_name: str, generation_config: GenerationConfig = None)
    def generate_content(self, prompt: str, **kwargs) -> GenerateContentResponse
    def start_chat(self, history: List = None) -> ChatSession
    def count_tokens(self, prompt: str) -> Dict[str, int]
```

### ChatSession

```python
class ChatSession:
    def send_message(self, message: str, **kwargs) -> GenerateContentResponse
    def get_history(self) -> List[Dict]
    def clear_history(self) -> None
    def delete_conversation(self) -> None
```

### CostKatanaClient

```python
class CostKatanaClient:
    def __init__(self, api_key: str = None, base_url: str = None, config_file: str = None)
    
    # Core Methods
    def send_message(self, message: str, model_id: str, **kwargs) -> Dict[str, Any]
    def get_available_models(self) -> List[Dict[str, Any]]
    def create_conversation(self, title: str = None, model_id: str = None) -> Dict[str, Any]
    def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]
    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]
    
    # SAST Methods
    def optimize_with_sast(self, prompt: str, **kwargs) -> Dict[str, Any]
    def compare_sast_vs_traditional(self, prompt: str, **kwargs) -> Dict[str, Any]
    def get_sast_vocabulary_stats(self) -> Dict[str, Any]
    def search_semantic_primitives(self, term: str = None, **kwargs) -> Dict[str, Any]
    def get_telescope_demo(self) -> Dict[str, Any]
    def test_universal_semantics(self, concept: str, languages: List[str] = None) -> Dict[str, Any]
    def get_sast_stats(self) -> Dict[str, Any]
    def get_sast_showcase(self) -> Dict[str, Any]
```

### GenerateContentResponse

```python
class GenerateContentResponse:
    text: str                           # Generated text
    usage_metadata: UsageMetadata       # Cost, tokens, latency info
    thinking: Dict                      # AI reasoning (if available)
```

### UsageMetadata

```python
class UsageMetadata:
    model: str                          # Model used
    cost: float                         # Cost in USD
    latency: float                      # Response time in seconds
    total_tokens: int                   # Total tokens used
    cache_hit: bool                     # Whether response was cached
    risk_level: str                     # Risk assessment level
    agent_path: List[str]               # Multi-agent processing path
    optimizations_applied: List[str]    # Applied optimizations
```

## 🤝 Support

- **Documentation**: [docs.costkatana.com](https://docs.costkatana.com)
- **Discord Community**: [discord.gg/costkatana](https://discord.gg/Wcwzw8wM)
- **Email Support**: abdul@hypothesize.tech
- **GitHub Issues**: [github.com/cost-katana/python-sdk](https://github.com/cost-katana/python-sdk)
- **GitHub Repository**: [github.com/Hypothesize-Tech/cost-katana-python](https://github.com/Hypothesize-Tech/cost-katana-python)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Ready to optimize your AI costs?** Get started at [costkatana.com](https://costkatana.com) 🚀# cost-katana-python
