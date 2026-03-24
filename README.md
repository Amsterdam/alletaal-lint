# alletaal-lint

**Dutch Text Readability Assessment Tool using LiNT Methodology**

[![License: EUPL v1.2](https://img.shields.io/badge/License-EUPL%20v1.2-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

alletaal-lint is a simplified Dutch text readability assessment tool based on the LiNT (Leesbaarheids­instrument voor Nederlandse Teksten) methodology. It provides automated scoring of Dutch text readability using linguistic features such as word frequency, syntactic complexity, and content word density.

**Why this tool?** The original [T-Scan](https://github.com/CentreForDigitalHumanities/tscan) implementation requires Alpino parser, Frog NLP, and custom corpora — making integration complex. alletaal-lint uses modern, pip-installable tools (spaCy + wordfreq) to provide a practical approximation of the LiNT score.

## Features

- **Sentence-level and document-level readability analysis**
- **REST API** for integration with other systems
- **Command-line interface** for batch processing and scripting
- **Multiple output formats** (JSON, table)

## Quick Start

### Installation

```bash
pip install alletaal-lint
```

### Install Dutch Language Model

```bash
python -m spacy download nl_core_news_sm
# or use the built-in command:
alletaal-lint install-model
```

### Command Line Usage

```bash
# Score a single sentence
alletaal-lint sentence "Dit is een eenvoudige zin om te testen."

# Score text from a file
alletaal-lint score --file document.txt

# Get detailed analysis
alletaal-lint score --text "Your Dutch text here." --detailed

# Output as JSON
alletaal-lint score --text "Your text" --format json

# Start API server
alletaal-lint server --host 0.0.0.0 --port 8000
```

### Python API Usage

```python
from alletaal_lint import Document, Sentence

# Analyze a document
doc = Document("Dit is een voorbeeldtekst. Het bevat meerdere zinnen.")
score = doc.calculate_lint_score()
level = doc.get_difficulty_level()

print(f"Document score: {score}")
print(f"Difficulty level: {level}")  # 1-4 (1=easy, 4=very difficult)

# Analyze individual sentences
for sentence_text, sentence_score, sentence_level in doc.get_sentence_scores():
    print(f"'{sentence_text}' -> Score: {sentence_score}, Level: {sentence_level}")

# Analyze a single sentence
sentence = Sentence("Deze zin wordt geanalyseerd op leesbaarheid.")
print(f"Sentence score: {sentence.calculate_lint_score()}")
```

### REST API Usage

Start the server:
```bash
alletaal-lint server
```

Then make requests:

```bash
# Score a document
curl -X POST "http://localhost:8000/score-document" \
     -H "Content-Type: application/json" \
     -d '{"text": "Dit is een voorbeeldtekst voor analyse."}'

# Score a sentence
curl -X POST "http://localhost:8000/score-sentence" \
     -H "Content-Type: application/json" \
     -d '{"text": "Deze zin wordt geanalyseerd."}'

# Get detailed analysis
curl -X POST "http://localhost:8000/analyze-document" \
     -H "Content-Type: application/json" \
     -d '{"text": "Tekst met meerdere zinnen. Elke zin krijgt een score."}'
```

API documentation is available at `http://localhost:8000/docs` when the server is running.

## Understanding LiNT Scores

LiNT scores range from 0-100, with higher scores indicating more readable text:

| Score Range | Level | Description |
|-------------|-------|-------------|
| 0-36 | 4 | Very Difficult |
| 37-51 | 3 | Difficult |
| 52-61.5 | 2 | Moderate |
| 61.5+ | 1 | Easy |

### Linguistic Features

The LiNT score is calculated using the original LiNT2 formula coefficients with three active features:

1. **Word Frequency**: How common the words are in Dutch (via `wordfreq` zipf scale)
2. **Syntactic Complexity**: Maximum dependency distance in sentences (via spaCy)
3. **Content Word Density**: Proportion of content words excluding adverbs (per sentence)

> **Note**: The fourth LiNT feature — concrete noun proportion — is not implemented. The original T-Scan uses a Cornetto semantic lexicon to classify nouns as concrete/abstract. Since replicating this would require bundling a large lexicon (defeating the simplification goal), this feature returns 0.0 and its formula coefficient is effectively zeroed out.

## Methodology

This tool implements the LiNT methodology developed by Gebruiker Centraal and builds upon research from the T-Scan project. The scoring algorithm uses the following formula:

```
score = 3.204 + (15.845 × freq_log) - (1.331 × max_dep) - (3.829 × content_words) + (13.096 × concrete_nouns)
final_score = min(100, max(0, 100 - score))
```

### Differences from T-Scan

This tool is a **deliberate simplification** of [T-Scan](https://github.com/CentreForDigitalHumanities/tscan). The formula coefficients are identical to T-Scan's `lint_score_2`, but the feature extraction uses different tooling:

| Feature | alletaal-lint | T-Scan | Impact |
|---------|--------------|--------|--------|
| **Word frequency** | `wordfreq` library (zipf scale) | `log10(freq/billion)` from SUBTLEX-NL | Different scale ranges |
| **Dependency distance** | spaCy neural parser | Alpino rule-based parser | Different parse trees |
| **Content word density** | Per-sentence (clause count = 1) | Per-clause with full clause detection | Overestimates for multi-clause sentences |
| **Concrete nouns** | Not implemented (returns 0.0) | Cornetto semantic lexicon | Formula term zeroed out |
| **Difficulty thresholds** | 36 / 51 / 61.5 | 34 / 46 / 60 | Minor, design choice |

**Consequence**: Scores are not directly comparable to T-Scan. The tool provides consistent relative ranking of text difficulty within its own scoring system. For applications needing exact T-Scan compatibility, use T-Scan directly.

### Research Background

- Based on [LiNT methodology](https://www.gebruikercentraal.nl/hulpmiddelen/lint-leesbaarheidsinstrument-voor-nederlandse-teksten/) from Gebruiker Centraal
- Builds upon the [T-Scan project](https://github.com/CentreForDigitalHumanities/tscan) from Utrecht University
- Validated for Dutch text readability assessment
- Adapted for modern NLP frameworks while preserving scientific validity

## Installation & Requirements

### System Requirements

- Python 3.10 or higher
- 2GB RAM (for spaCy model)
- Internet connection (for initial model download)

### Dependencies

- `spacy` >= 3.7.0 (Dutch NLP processing)
- `wordfreq` >= 3.1.0 (Word frequency data)
- `fastapi` >= 0.115.0 (REST API)
- `typer` >= 0.15.0 (CLI interface)
- `rich` >= 13.0.0 (CLI formatting)

### Development Installation

```bash
git clone https://github.com/Amsterdam/alletaal-lint.git
cd alletaal-lint
make setup  # installs package, dev deps, and spaCy model
```

## Docker Usage

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Amsterdam/alletaal-lint.git
cd alletaal-lint

# Start the service
docker-compose up -d

# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f alletaal-lint

# Stop the service
docker-compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t alletaal-lint .

# Run the container
docker run -d -p 8000:8000 --name alletaal-lint alletaal-lint

# Check health
docker exec alletaal-lint curl -f http://localhost:8000/health

# View logs
docker logs alletaal-lint

# Stop and remove
docker stop alletaal-lint && docker rm alletaal-lint
```

### Production Deployment

For production use, consider:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  alletaal-lint:
    image: alletaal-lint:latest
    ports:
      - "8000:8000"
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    restart: unless-stopped
```

## Performance

- **Sentence processing**: ~10-50ms per sentence
- **Document processing**: Scales linearly with sentence count
- **Memory usage**: ~500MB (primarily spaCy model)
- **Concurrent requests**: Supports multiple simultaneous API requests

### OpenAPI Specification

An OpenAPI spec is available for integration with other systems:

```bash
# Export to file
alletaal-lint openapi --output openapi.json

# Or use the pre-generated spec in the repository root
```

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/score-sentence` | POST | Score a single sentence |
| `/score-document` | POST | Score an entire document |
| `/analyze-document` | POST | Detailed document analysis |
| `/health` | GET | Service health check |
| `/methodology` | GET | Implementation methodology details |
| `/docs` | GET | Interactive API documentation |

### Response Format

```json
{
  "lint_score": 67.5,
  "difficulty_level": 4
}
```

Detailed analysis includes additional metrics:
```json
{
  "document_score": 67.5,
  "document_level": 4,
  "sentence_count": 3,
  "average_sentence_length": 12.3,
  "sentences": [
    {
      "sentence": "Example sentence.",
      "lint_score": 65.2,
      "difficulty_level": 4,
      "word_frequency_log": 4.2,
      "max_dependency_length": 3,
      "content_words_proportion": 0.6,
      "concrete_nouns_proportion": 0.0
    }
  ]
}
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. One-command setup: `make setup`
3. Run tests: `make test`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=alletaal_lint

# Run specific tests
pytest tests/test_core.py -v
```

## License

This project is licensed under the European Union Public Licence v. 1.2 (EUPL-1.2). See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: Available in this README and API docs
- **Issues**: [GitHub Issues](https://github.com/Amsterdam/alletaal-lint/issues)
- **Contact**: innovatie@amsterdam.nl

---

**Made by the City of Amsterdam Innovation Team**