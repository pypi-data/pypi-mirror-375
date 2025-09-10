# 💎 Gemmit

> **Gem**ini + Com**mit** = **Gemmit**
>
> AI-powered conventional commit messages using Google's Gemini

[![PyPI version](https://badge.fury.io/py/gemmit.svg)](https://badge.fury.io/py/gemmit)

Gemmit uses Google's Gemini AI to generate professional, conventional commit messages from your staged changes. Say goodbye to "fix stuff" and "wip" commits!

## ✨ Features

- 🤖 **AI-powered**: Uses Google's Gemini for intelligent commit messages
- 📏 **Conventional**: Follows [Conventional Commits](https://conventionalcommits.org/) specification
- ⚡ **Fast**: Gemini Flash model for quick generation
- 🎯 **Interactive**: Review, edit, or regenerate messages
- 🚀 **Auto-commit**: Skip confirmation with `-y` flag
- 🔧 **Customizable**: Multiple models and configuration options

## 🚀 Quick Start

```bash
# Install
pip install gemmit

# Get API key from Google AI Studio
export GEMINI_API_KEY='your-api-key'

# Stage your changes
git add .

# Generate and commit
gemmit
```
