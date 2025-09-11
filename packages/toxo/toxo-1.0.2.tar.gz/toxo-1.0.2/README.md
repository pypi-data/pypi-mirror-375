# TOXO - No-Code LLM Training Platform

🧠 **World's First Comprehensive No-Code LLM Training Platform**

Transform any black-box LLM into a domain expert without coding. Train sophisticated AI models through our web interface and deploy them instantly as `.toxo` files.

## 🚀 Quick Start

### Installation
```bash
pip install toxo
```

### Usage
```python
from toxo import ToxoLayer

# Load your trained model (created on toxotune.com)
layer = ToxoLayer.load("your_expert_model.toxo")

# Set your API key (Gemini/OpenAI)
layer.setup_api_key("your_api_key_here")

# Use your trained AI expert
response = layer.query("Your question here")
print(response)
```

### Async Usage
```python
import asyncio
from toxo import ToxoLayer

async def main():
    layer = ToxoLayer.load("your_expert_model.toxo")
    layer.setup_api_key("your_api_key_here")
    
    response = await layer.query_async("Your question here")
    print(response)

asyncio.run(main())
```

## 🎯 Key Features

- **🎨 No-Code Training**: Create AI experts through our web interface
- **⚡ Instant Deployment**: Download and use `.toxo` files immediately
- **🧠 Domain Expertise**: Specialized AI for any field or industry
- **🔄 Continuous Learning**: Models improve with feedback
- **📊 Advanced Analytics**: Performance monitoring and insights
- **🤖 Multi-Agent Systems**: Collaborative AI workflows
- **🔍 Smart Retrieval**: Advanced RAG and context processing
- **🎨 Multi-Modal**: Text, images, audio, video support

## 📖 Documentation

### Basic Methods

#### `ToxoLayer.load(path)`
Load a `.toxo` model file.
```python
layer = ToxoLayer.load("path/to/your_model.toxo")
```

#### `layer.setup_api_key(api_key)`
Configure your LLM API key (Gemini, OpenAI, etc.).
```python
layer.setup_api_key("your_api_key_here")
```

#### `layer.query(question, context=None)`
Synchronous query to your trained AI expert.
```python
response = layer.query("What is quantum computing?")
response = layer.query("Analyze this data", context={"data": "..."})
```

#### `layer.query_async(question, context=None)`
Asynchronous query for better performance.
```python
response = await layer.query_async("Your question here")
```

### Advanced Methods

#### `layer.get_info()`
Get information about your trained model.
```python
info = layer.get_info()
print(f"Domain: {info['domain']}")
print(f"Trained: {info['is_trained']}")
print(f"Performance: {info['metrics']}")
```

#### `layer.add_feedback(question, response, rating)`
Improve your model with feedback.
```python
layer.add_feedback("Question", "Response", 8.5)
```

#### `layer.get_capabilities()`
Discover what your model can do.
```python
capabilities = layer.get_capabilities()
print(capabilities)
```

## 🏗️ Creating Models

Models are created on our web platform at [toxotune.com](https://toxotune.com):

1. **🎯 Choose Domain**: Select your area of expertise
2. **📚 Add Training Data**: Upload documents, examples, or data
3. **🏋️ Train Model**: Our platform handles the complex training
4. **📦 Download**: Get your `.toxo` file ready for use
5. **🚀 Deploy**: Use anywhere with this Python package

## 🔧 Advanced Usage

### Context-Aware Queries
```python
# Provide context for better responses
context = {
    "user_role": "data_scientist",
    "project": "customer_analysis",
    "priority": "high"
}
response = layer.query("How should I approach this?", context=context)
```

### Batch Processing
```python
questions = [
    "What is machine learning?",
    "How does neural networks work?",
    "Explain deep learning"
]

responses = []
for question in questions:
    response = await layer.query_async(question)
    responses.append(response)
```

### Performance Monitoring
```python
# Get performance metrics
metrics = layer.get_performance_metrics()
print(f"Average response time: {metrics['avg_response_time']}")
print(f"Accuracy score: {metrics['accuracy']}")
```

## 🛠️ Requirements

- Python 3.8+
- Internet connection (for LLM API calls)
- API key for supported LLM providers (Gemini, OpenAI, etc.)

## 🔐 Supported LLM Providers

- **Google Gemini** (Recommended)
- **OpenAI GPT** (Coming Soon)
- **Anthropic Claude** (Coming Soon)
- **Local Models** (Coming Soon)

## 📊 Model Types

Create specialized AI experts for any domain:

- **📈 Business Intelligence**: Data analysis, reporting, insights
- **🔬 Research Assistant**: Literature review, hypothesis generation
- **💻 Code Expert**: Programming help, code review, debugging
- **📚 Educational Tutor**: Personalized learning and explanations
- **🎨 Creative Writer**: Content creation, storytelling, copywriting
- **⚕️ Healthcare Assistant**: Medical research, patient education
- **⚖️ Legal Advisor**: Contract analysis, legal research
- **🏦 Financial Analyst**: Market analysis, risk assessment
- **And many more...**

## 🆘 Support

- **Documentation**: [docs.toxotune.com](https://docs.toxotune.com)
- **Support**: [support@toxotune.com](mailto:support@toxotune.com)
- **Community**: [community.toxotune.com](https://community.toxotune.com)
- **Issues**: [GitHub Issues](https://github.com/toxotune/toxo-python/issues)

## 📄 License

Proprietary License - See [LICENSE](LICENSE) file for details.

## 🚀 Get Started

1. Visit [toxotune.com](https://toxotune.com)
2. Create your first AI expert
3. Download your `.toxo` file
4. Install this package: `pip install toxo`
5. Start using your trained AI!

---

**TOXO** - Democratizing AI Training for Everyone 🧠✨
# toxo_public_python_package
# toxo_public_python_package
