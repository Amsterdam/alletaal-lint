# LiNT Methodology Implementation

This document explains how alletaal-lint implements the LiNT (Leesbaarheids­instrument voor Nederlandse Teksten) methodology and how it differs from the original T-Scan implementation.

## Scientific Foundation

The LiNT methodology was developed by Gebruiker Centraal based on extensive research into Dutch text readability. It uses four linguistic features to predict text difficulty:

1. **Word Frequency** (`wrd_freq_log_zn_corr`)
2. **Maximum Dependency Length** (`al_max`)
3. **Content Word Density** (`inhwrd_dz_zonder_abw`)
4. **Concrete Noun Proportion** (`conc_nw_ruim_p`)

## The LiNT2 Formula

```
score = 3.204 + (15.845 × freq_log) - (1.331 × max_dep) - (3.829 × content_words) + (13.096 × concrete_nouns)
final_score = min(100, max(0, 100 - score))
```

This formula is **identical** in both T-Scan and alletaal-lint implementations.

## Implementation Differences

### Feature Extraction Methods

| Feature | T-Scan Implementation | alletaal-lint Implementation |
|---------|----------------------|------------------------------|
| **Word Frequency** | SUBTLEX-NL database with complex corrections | `wordfreq` library with zipf scores |
| **Dependency Parsing** | Alpino parser (rule-based) | spaCy Dutch model (neural) |
| **Clause Detection** | Sophisticated clause boundary detection | Simplified (defaults to 1 clause/sentence) |
| **Noun Classification** | Semantic categorization | POS-tag based classification |

### Technical Stack Comparison

| Component | T-Scan | alletaal-lint |
|-----------|---------|---------------|
| **Language** | C++ | Python |
| **Parser** | Alpino | spaCy |
| **Frequency Data** | SUBTLEX-NL | wordfreq |
| **Tokenization** | Custom Dutch rules | spaCy tokenizer |
| **Dependencies** | Heavy (requires Alpino setup) | Lightweight (pip install) |

## Score Variance Analysis

### Expected Differences

Based on our analysis, scores may differ by **3-7 points** for complex sentences due to:

1. **Dependency Distance Calculation**:
   - Alpino tends to produce higher maximum dependency distances
   - Different grammatical analysis approaches

2. **Word Frequency Scoring**:
   - Different frequency databases yield different baselines
   - Varying approaches to frequency normalization

3. **Content Word Classification**:
   - T-Scan uses more sophisticated linguistic rules
   - Different handling of proper names and technical terms

### Score Variance Examples

| Sentence Type | Expected Variance | Primary Cause |
|---------------|-------------------|---------------|
| Simple sentences | 1-3 points | Frequency database differences |
| Complex sentences | 3-7 points | Dependency parsing differences |
| Technical text | 2-5 points | Content word classification |
| Sentences with names | 2-4 points | Proper name handling |

## Validation Approach

### What We Maintain

✅ **Scientific Validity**: Original LiNT formula and linguistic principles
✅ **Relative Ranking**: Correctly identifies more/less readable texts
✅ **Consistency**: Repeatable measurements for the same input
✅ **Interpretability**: Same difficulty levels (1-4) and thresholds

### What May Differ

⚠️ **Absolute Scores**: Numerical values may vary from T-Scan
⚠️ **Edge Cases**: Complex grammatical constructions may score differently
⚠️ **Technical Terms**: Different handling of domain-specific vocabulary

## Best Practices for Use

### Recommended Applications

1. **Comparative Analysis**: Comparing readability across different texts
2. **Content Optimization**: Iterative improvement of text readability
3. **Automated Assessment**: Integration into content management workflows
4. **Educational Tools**: Teaching about text complexity

### Interpretation Guidelines

1. **Focus on Trends**: Use for relative comparisons rather than absolute scores
2. **Consider Context**: Account for domain, audience, and purpose
3. **Validate Manually**: Combine with human assessment for critical applications
4. **Track Changes**: Monitor readability improvements over time

## Technical Implementation Details

### Word Frequency Calculation

```python
def get_word_frequency(text, lemma, tag, sub_tags):
    if tag not in ['N', 'ADJ', 'WW', 'BW']:
        return None
    
    if sub_tags and sub_tags[0] == 'eigen':
        return None  # Skip proper names

    freq = zipf_frequency(text, 'nl')
    return freq if freq > 0 else 1.3555  # Default for unknown words
```

### Dependency Distance Calculation

```python
def get_dependency_distance(token):
    if token.dep_ in ['punct']:
        return 0
    return abs(token.head.i - token.i)
```

### Content Word Classification

```python
def is_content_word_excluding_adverbs(token):
    return token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ', 'NUM', 'SYM'] and token.pos_ != 'ADV'
```

## Future Improvements

### Short Term
- Enhanced clause detection algorithms
- Improved semantic noun classification
- Calibration against T-Scan test cases

### Long Term
- Integration with Alpino parser for exact T-Scan compatibility
- Support for domain-specific frequency adjustments
- Multi-model ensemble for improved accuracy

## Research Citations

1. Kraf, R., & Pander Maat, H. (2009). Leesbaarheidsonderzoek: oude problemen, nieuwe kansen. *Tijdschrift voor Taalbeheersing*, 31(2), 97-123.

2. Pander Maat, H., Kraf, R., van den Bosch, A., Dekker, N., van Gompel, M., Kleijn, S., ... & van der Sloot, K. (2014). T-Scan: a new tool for analyzing Dutch text. *Computational Linguistics in the Netherlands Journal*, 4, 53-74.

3. Gebruiker Centraal. (2018). LiNT: Leesbaarheids­instrument voor Nederlandse Teksten. Available at: https://www.gebruikercentraal.nl/hulpmiddelen/lint-leesbaarheidsinstrument-voor-nederlandse-teksten/

## Contact & Support

For questions about methodology implementation or score interpretation:
- **Technical Issues**: [GitHub Issues](https://github.com/Amsterdam/alletaal-lint/issues)
- **Methodology Questions**: innovatie@amsterdam.nl
- **Research Collaboration**: Contact the original LiNT researchers