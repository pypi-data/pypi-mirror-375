# HyperLLM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A unified Python interface for multiple LLM providers with intelligent caching and cost-saving interactive development mode. **Stop burning money on API calls during development** - use interactive mode to prototype with real LLMs at zero api cost!

## 🚀 Why HyperLLM?

**Save Development Costs**: Interactive mode eliminates expensive API calls during prototyping. Copy prompts to your clipboard, paste responses back, and build your application without the API meter running.

**Provider Freedom**: Switch between OpenAI, Anthropic, local Ollama, or any custom API with a single line of code. No vendor lock-in, no rewriting.

**Smart Caching**: Never pay for the same prompt twice. Responses are automatically cached and reused across development and production.

**Developer Experience**: Built by developers, for developers. Clipboard integration, file I/O, and seamless workflows that just work.

## ✨ Features

- 🔄 **Unified Interface**: One API for all LLM providers - OpenAI, Anthropic, Ollama, and more
- 💰 **Cost-Saving Interactive Mode**: Develop without API costs using copy-paste workflow  
- 💾 **Intelligent Caching**: Automatic response caching with prompt-based deduplication
- 🔌 **Extensible Provider System**: Easy to add new providers or custom APIs
- 📋 **Clipboard Integration**: Automatic prompt copying for seamless workflows
- 📁 **File I/O Support**: Read prompts from and write responses to files
- 🛡️ **Production Ready**: Robust error handling, validation, and monitoring
- 🎯 **Zero Configuration**: Works out of the box with sensible defaults

## 📦 Installation

```bash
# Basic installation
pip install hyperllm

# With specific provider support
pip install hyperllm[openai]      # OpenAI GPT models
pip install hyperllm[anthropic]   # Anthropic Claude models  
pip install hyperllm[clipboard]   # Enhanced clipboard features

# Install everything
pip install hyperllm[all]
```

## 🚀 Quick Start

```python
from hyperllm import HyperLLM

# Initialize once, use everywhere
interface = HyperLLM()

# Configure your preferred provider
interface.set_llm('openai', 
                  api_key='your-api-key', 
                  model='gpt-4')

# Get responses (cached automatically)
response = interface.get_response("Explain quantum computing simply")
print(response)

# Subsequent identical prompts use cache - zero cost!
cached_response = interface.get_response("Explain quantum computing simply")
```

## 🔥 Interactive Development Mode

**The game-changer for LLM development costs:**

```bash
# Enable interactive mode - save money during development!
export LLM_INTERACTIVE_MODE=true
```

```python
from hyperllm import HyperLLM

interface = HyperLLM()
interface.set_llm('openai')  # Provider doesn't matter in interactive mode

# This copies prompt to clipboard and waits for your response
response = interface.get_response("Write a Python function to sort a list")

# Workflow:
# 1. Prompt automatically copied to clipboard ✨  
# 2. Paste into ChatGPT/Claude/etc.
# 3. Copy response and paste back
# 4. Response cached for production use
# 5. Zero API costs during development! 💰
```

**Perfect for:**
- Prompt engineering and iteration
- Building demos and prototypes  
- Testing different prompt variations
- Learning and experimentation

## 🌐 Supported Providers

### OpenAI GPT Models
```python
interface.set_llm('openai',
                  api_key='sk-...',
                  model='gpt-4o',           # or gpt-3.5-turbo, gpt-4, etc.
                  temperature=0.7,
                  max_tokens=2000)
```

### Anthropic Claude
```python
interface.set_llm('anthropic',          # or 'claude'
                  api_key='sk-ant-...',
                  model='claude-3-sonnet-20240229',
                  max_tokens=2000)
```

### Local Ollama
```python
interface.set_llm('ollama',
                  base_url='http://localhost:11434',
                  model='llama2',         # or codellama, mistral, etc.
                  temperature=0.7)
```

### Custom APIs (OpenAI Compatible)
```python
interface.set_llm('custom',
                  base_url='https://api.your-provider.com',
                  api_key='your-key',
                  model='your-model',
                  headers={'Custom-Header': 'value'})
```

### Check Available Providers
```python
from hyperllm import get_available_providers

providers = get_available_providers()
for name, info in providers.items():
    status = "✅ Available" if info['available'] else "❌ Missing deps"
    print(f"{name}: {status}")
```

## 💾 Smart Caching System

Responses are automatically cached using prompt hashing:

```python
# First call - hits API/interactive mode
response1 = interface.get_response("What is machine learning?")

# Subsequent calls - instant cache retrieval, zero cost
response2 = interface.get_response("What is machine learning?") 

# Manage cache
stats = interface.get_cache_stats()
print(f"Cached responses: {stats['total_entries']}")

interface.clear_cache()  # Clean slate when needed
```

## 🛠️ Advanced Usage

### One-Line Setup
```python
from hyperllm import create_interface

# Create and configure in one step
interface = create_interface('anthropic',
                           cache_dir='/custom/cache',
                           api_key='sk-ant-...',
                           model='claude-3-opus-20240229')
```

### File-Based Workflows
```bash
# Configure file I/O for automated workflows
export PROMPT_OUTPUT_FILE="/tmp/prompt.txt"
export RESPONSE_INPUT_FILE="/tmp/response.txt"  
export LLM_INTERACTIVE_MODE=true
```

### Provider Comparison
```python
# Easy A/B testing between providers
providers = [
    ('openai', {'model': 'gpt-4'}),
    ('anthropic', {'model': 'claude-3-sonnet-20240229'}),
    ('ollama', {'model': 'llama2'})
]

for name, config in providers:
    interface.set_llm(name, **config)
    response = interface.get_response("Compare these approaches...")
    print(f"{name}: {response[:100]}...")
```

### Custom Provider Registration
```python
from hyperllm.providers import register_provider, BaseLLMProvider

class MyProvider(BaseLLMProvider):
    def validate_config(self):
        return True
    
    def _setup_client(self):
        pass
        
    def generate_response(self, prompt, **kwargs):
        return f"Custom response for: {prompt}"

# Register and use
register_provider('myprovider', MyProvider)
interface.set_llm('myprovider')
```

## 🎯 Real-World Examples

### Development to Production Pipeline
```python
import os
from hyperllm import HyperLLM

# Development phase - zero API costs
os.environ['LLM_INTERACTIVE_MODE'] = 'true'

interface = HyperLLM()
interface.set_llm('openai')

# Build your prompts interactively
prompts = [
    "Generate a REST API design for a blog",
    "Write error handling for user authentication", 
    "Create database schema for user profiles"
]

for prompt in prompts:
    response = interface.get_response(prompt)
    # Responses cached automatically

# Production deployment - use cached responses + API
os.environ['LLM_INTERACTIVE_MODE'] = 'false'
interface.set_llm('openai', api_key=os.environ['OPENAI_API_KEY'])

# Cached responses used when available, new prompts hit API
response = interface.get_response("Generate a REST API design for a blog")  # From cache!
new_response = interface.get_response("Add OAuth2 to the API")  # New API call
```

### Multi-Model Analysis
```python
# Compare responses across providers effortlessly
interface = HyperLLM()
test_prompt = "Explain the trade-offs of microservices architecture"

results = {}
for provider in ['openai', 'anthropic', 'ollama']:
    try:
        interface.set_llm(provider, **provider_configs[provider])
        results[provider] = interface.get_response(test_prompt)
    except Exception as e:
        results[provider] = f"Error: {e}"

# Analyze differences in responses
for provider, response in results.items():
    print(f"\n=== {provider.title()} ===")
    print(response)
```

## 📊 Use Cases

- **🧪 Prototype Development**: Build LLM features without burning budget
- **🔬 Prompt Engineering**: Iterate on prompts using interactive mode
- **⚡ Production Applications**: Seamless transition from development to production
- **📈 A/B Testing**: Compare providers and models effortlessly
- **🎓 Learning & Experimentation**: Explore LLMs without cost concerns
- **🏗️ Enterprise Integration**: Unified interface for multiple LLM services

## 📈 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_INTERACTIVE_MODE` | Enable interactive development mode | `false` |
| `PROMPT_OUTPUT_FILE` | File to write prompts (interactive mode) | None |
| `RESPONSE_INPUT_FILE` | File to read responses (interactive mode) | None |
| `OPENAI_API_KEY` | Default OpenAI API key | None |
| `ANTHROPIC_API_KEY` | Default Anthropic API key | None |

## 🔧 Error Handling

```python
from hyperllm import HyperLLM
from hyperllm.providers.base import ConfigurationError, APIError

try:
    interface = HyperLLM()
    interface.set_llm('openai', api_key='invalid-key')
    response = interface.get_response("Test prompt")
    
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🤝 Contributing

We welcome contributions! HyperLLM is designed to be extensible and community-driven.

### Quick Start for Contributors

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/hyperllm.git
   cd hyperllm
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode with all dependencies
   pip install -e ".[all,dev]"
   ```

3. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

### 🛠️ Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest tests/ --cov=hyperllm --cov-report=html

# Run linting
flake8 hyperllm tests
black hyperllm tests

# Type checking
mypy hyperllm
```

### 📋 Contributing Guidelines

#### Adding New Providers

We're always looking for new LLM provider integrations! Here's how to add one:

1. **Create Provider File**
   ```python
   # hyperllm/providers/newprovider_provider.py
   from .base import BaseLLMProvider
   
   class NewProviderProvider(BaseLLMProvider):
       def validate_config(self):
           # Validate configuration
           pass
           
       def _setup_client(self):
           # Initialize client
           pass
           
       def generate_response(self, prompt, **kwargs):
           # Implement response generation
           pass
   ```

2. **Register Provider**
   ```python
   # Add to hyperllm/providers/__init__.py
   from .newprovider_provider import NewProviderProvider
   
   PROVIDER_REGISTRY['newprovider'] = NewProviderProvider
   ```

3. **Add Tests**
   ```python
   # tests/test_providers/test_newprovider.py
   import unittest
   from hyperllm.providers.newprovider_provider import NewProviderProvider
   
   class TestNewProviderProvider(unittest.TestCase):
       def test_validation(self):
           # Test provider validation
           pass
   ```

4. **Update Documentation**
   - Add usage example to README
   - Document configuration options
   - Add to provider comparison table

#### Code Style

- **Black** for code formatting
- **flake8** for linting  
- **mypy** for type hints
- **pytest** for testing
- **Google style** docstrings

#### Commit Guidelines

```bash
# Use conventional commits
git commit -m "feat: add support for NewProvider LLM"
git commit -m "fix: handle timeout errors in OpenAI provider" 
git commit -m "docs: add examples for interactive mode"
```

### 🐛 Bug Reports

Found a bug? Please open an issue with:

1. **Environment details** (Python version, OS, package version)
2. **Minimal reproduction code**
3. **Expected vs actual behavior**
4. **Error messages/stack traces**

### 💡 Feature Requests

Have an idea? We'd love to hear it! Open an issue with:

1. **Use case description**
2. **Proposed API/interface**
3. **Benefits and alternatives considered**

### 🎯 Good First Issues

Look for issues labeled `good-first-issue`:

- Adding new provider integrations
- Improving error messages
- Adding configuration examples
- Writing documentation
- Adding tests for edge cases

### 📚 Development Resources

- **Provider Base Class**: `hyperllm/providers/base.py`
- **Main Interface**: `hyperllm/interface.py`
- **Test Examples**: `tests/test_providers/`
- **Integration Examples**: `examples/`

### 🏆 Contributors

Thanks to all contributors who make HyperLLM better!

<!-- Will be auto-generated -->

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI**: https://pypi.org/project/hyperllm/
- **Documentation**: https://github.com/hyper-swe/hyperllm#readme
- **Issues**: https://github.com/hyper-swe/hyperllm/issues
- **Changelog**: https://github.com/hyper-swe/hyperllm/releases

## ⭐ Support the Project

If HyperLLM saves you development time and costs, please:

- ⭐ **Star the repository**
- 🐛 **Report bugs** and suggest features
- 🤝 **Contribute** new providers or improvements
- 📢 **Share** with other developers

---

**Made with ❤️ by developers who got tired of expensive LLM development cycles.**

*HyperLLM - One interface, all providers, zero waste.*
