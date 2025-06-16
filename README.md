# alletaal-lint

**Dutch Text Readability Assessment Tool using LiNT Methodology**

[![License: EUPL v1.2](https://img.shields.io/badge/License-EUPL%20v1.2-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

alletaal-lint is a Dutch text readability assessment tool based on the LiNT (Leesbaarheids­instrument voor Nederlandse Teksten) methodology. It provides automated scoring of Dutch text readability using linguistic features such as word frequency, syntactic complexity, content word density, and concreteness.

## Features

- **Sentence-level and document-level readability analysis**
- **REST API** for integration with other systems
- **Command-line interface** for batch processing and scripting
- **Multiple output formats** (JSON, table)
- **Scientific methodology** based on validated research
- **Easy integration** with existing workflows

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
print(f"Difficulty level: {level}")  # 1-4 (1=very difficult, 4=easy)

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
| 0-36 | 1 | Very Difficult |
| 37-51 | 2 | Difficult |
| 52-61.5 | 3 | Moderate |
| 61.5+ | 4 | Easy |

### Linguistic Features

The LiNT score is calculated using four key linguistic features:

1. **Word Frequency**: How common the words are in Dutch
2. **Syntactic Complexity**: Maximum dependency distance in sentences
3. **Content Word Density**: Proportion of content words (excluding adverbs)
4. **Concreteness**: Proportion of concrete nouns

### Score Interpretation & Compatibility

**Important Note**: This implementation uses modern NLP tools (spaCy) and may produce scores that differ from the original T-Scan implementation. The differences are due to:

- **Different parsing approaches**: spaCy vs. Alpino parser
- **Feature extraction methods**: Simplified vs. complex linguistic analysis
- **Frequency databases**: wordfreq vs. T-Scan's frequency data

**Key Points**:
- **Scientifically valid**: Uses the original LiNT formula and methodology
- **Consistent results**: Provides reliable relative readability assessment
- **Modern technology**: Benefits from current NLP advances
- **Score variance**: May differ 3-7 points from T-Scan for complex sentences
- **Relative ranking**: Correctly identifies more/less readable texts

## Methodology

This tool implements the LiNT methodology developed by Gebruiker Centraal and builds upon research from the T-Scan project. The scoring algorithm uses the following formula:

```
score = 3.204 + (15.845 × freq_log) - (1.331 × max_dep) - (3.829 × content_words) + (13.096 × concrete_nouns)
final_score = min(100, max(0, 100 - score))
```

### Implementation Approach

This modern implementation maintains the core LiNT formula while using contemporary NLP tools:

**Feature Extraction**:
- **Word Frequency**: Uses `wordfreq` library with Dutch language data
- **Dependency Parsing**: Uses spaCy's Dutch model (`nl_core_news_sm`)
- **Content Word Classification**: Based on spaCy POS tags and morphological features
- **Syntactic Analysis**: spaCy dependency parsing for distance calculations

**Differences from Original T-Scan**:
- **Parser**: spaCy instead of Alpino (affects dependency distance calculation)
- **Frequency Data**: wordfreq instead of SUBTLEX-NL (affects word frequency scores)
- **Clause Detection**: Simplified approach vs. T-Scan's sophisticated clause analysis
- **Semantic Classification**: POS-based vs. T-Scan's semantic noun categorization

### Validation & Accuracy

- **Formula Accuracy**: ✅ Identical to original LiNT2 formula
- **Relative Assessment**: ✅ Correctly ranks text difficulty
- **Absolute Scores**: ⚠️ May vary 3-7 points from T-Scan due to parsing differences
- **Consistency**: ✅ Provides reliable, repeatable measurements

### Research Background

- Based on [LiNT methodology](https://www.gebruikercentraal.nl/hulpmiddelen/lint-leesbaarheidsinstrument-voor-nederlandse-teksten/) from Gebruiker Centraal
- Builds upon the [T-Scan project](https://github.com/CentreForDigitalHumanities/tscan) from Utrecht University
- Validated for Dutch text readability assessment
- Adapted for modern NLP frameworks while preserving scientific validity

## Installation & Requirements

### System Requirements

- Python 3.9 or higher
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
pip install -e ".[dev]"
python -m spacy download nl_core_news_sm
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

## Use Cases

### Content Creation
- Evaluate readability during writing
- Optimize text for target audiences
- Ensure accessibility compliance

### Publishing & Media
- Automated content quality checks
- Editorial workflow integration
- Reader accessibility assessment

### Government & Public Services
- Clear communication compliance
- Public document assessment
- Accessibility requirements

### Education & Training
- Learning material evaluation
- Language proficiency assessment
- Writing skill development

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/score-sentence` | POST | Score a single sentence |
| `/score-document` | POST | Score an entire document |
| `/analyze-document` | POST | Detailed document analysis |
| `/health` | GET | Service health check |
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
      "concrete_nouns_proportion": 0.3
    }
  ]
}
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Set up development environment: `pip install -e ".[dev]"`
3. Install pre-commit hooks: `pre-commit install`
4. Run tests: `pytest`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=alletaal_lint

# Run specific tests
pytest tests/test_core.py -v
```

## Roadmap

- [ ] Batch processing improvements
- [ ] Additional output formats
- [ ] Integration with popular CMS platforms
- [ ] Enhanced linguistic features
- [ ] Performance optimizations
- [ ] Multi-language support framework

## License

This project is licensed under the European Union Public Licence v. 1.2 (EUPL-1.2). See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: Available in this README, [METHODOLOGY.md](METHODOLOGY.md), and API docs
- **Issues**: [GitHub Issues](https://github.com/Amsterdam/alletaal-lint/issues)
- **Contact**: innovatie@amsterdam.nl

## Acknowledgments

- **Gebruiker Centraal** for the LiNT methodology
- **Centre for Digital Humanities (Utrecht University)** for T-Scan research
- **City of Amsterdam** for open source development and maintenance
- **spaCy team** for excellent NLP tools
- **Contributors** who help improve this tool

---

**Made by the City of Amsterdam Innovation Team**