"""Setup script for QuietAudit SDK"""

from setuptools import setup, find_packages

setup(
    name="quietaudit-sdk",
    version="0.1.0",
    author="QuietStack",
    author_email="support@quietstack.com",
    description="Immutable audit trails for AI decisions",
    long_description="""
QuietAudit SDK provides seamless blockchain-based audit logging for AI models.

Add immutable audit trails to any AI decision with just 2 lines of code:

```python
from quietaudit_sdk import wrap_model
import openai

# Wrap your existing AI client
openai_client = openai.OpenAI(api_key="sk-...")
audited_openai = wrap_model(openai_client, quietaudit_api_key="qa_live_...")

# Same API, automatic blockchain audit trails
response = audited_openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Approve this loan"}]
)
```

Perfect for:
- AI compliance and governance
- Financial services AI decisions  
- Healthcare AI applications
- Any AI system requiring audit trails
    """,
    long_description_content_type="text/markdown",
    url="https://github.com/quietstack/quietaudit-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.3.0"],
    },
    keywords="ai audit blockchain compliance governance",
    project_urls={
        "Bug Reports": "https://github.com/quietstack/quietaudit-sdk/issues",
        "Source": "https://github.com/quietstack/quietaudit-sdk",
        "Documentation": "https://docs.quietstack.com/sdk",
    },
)