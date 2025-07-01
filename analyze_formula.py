#!/usr/bin/env python3
"""
Analyze the LiNT formula to understand the scoring direction.
"""

def analyze_lint_formula():
    """
    Analyze what the raw LiNT formula produces before any inversion.
    
    Formula: score = 3.204 + (15.845 * freq_log) - (1.331 * al_max) - (3.829 * content_words) + (13.096 * concrete)
    Current: return 100 - score
    
    Let's test with some hypothetical values:
    """
    
    print("=== ANALYZING LiNT FORMULA ===\n")
    
    # Test case 1: Very simple text
    print("1. VERY SIMPLE TEXT:")
    freq_log = 5.0      # High frequency words (common)
    al_max = 1          # Short dependencies
    content_words = 0.3 # Low content word density
    concrete = 0.8      # High concrete nouns
    
    raw_score = (3.204 + (15.845 * freq_log) - (1.331 * al_max) - (3.829 * content_words) + (13.096 * concrete))
    final_score = round(min(100.0, max(0.0, 100 - raw_score)), 2)
    
    print(f"   freq_log: {freq_log} (high frequency = common words)")
    print(f"   al_max: {al_max} (short dependencies)")
    print(f"   content_words: {content_words} (low density)")
    print(f"   concrete: {concrete} (high concreteness)")
    print(f"   Raw formula result: {raw_score:.2f}")
    print(f"   After 100-score: {final_score}")
    print(f"   → Should be EASY to read")
    print()
    
    # Test case 2: Very complex text
    print("2. VERY COMPLEX TEXT:")
    freq_log = 2.0      # Low frequency words (uncommon)
    al_max = 8          # Long dependencies
    content_words = 0.8 # High content word density
    concrete = 0.2      # Low concrete nouns
    
    raw_score = (3.204 + (15.845 * freq_log) - (1.331 * al_max) - (3.829 * content_words) + (13.096 * concrete))
    final_score = round(min(100.0, max(0.0, 100 - raw_score)), 2)
    
    print(f"   freq_log: {freq_log} (low frequency = uncommon words)")
    print(f"   al_max: {al_max} (long dependencies)")
    print(f"   content_words: {content_words} (high density)")
    print(f"   concrete: {concrete} (low concreteness)")
    print(f"   Raw formula result: {raw_score:.2f}")
    print(f"   After 100-score: {final_score}")
    print(f"   → Should be DIFFICULT to read")
    print()
    
    print("=== ANALYSIS ===")
    print("The raw formula produces:")
    print("- Higher scores for DIFFICULT text (complex words, long dependencies, high content density)")
    print("- Lower scores for EASY text (common words, short dependencies, low content density)")
    print()
    print("The '100 - score' inversion makes:")
    print("- Higher final scores = EASIER text")
    print("- Lower final scores = HARDER text")
    print()
    print("This matches the colleague's quote: 'score van 1 (erg makkelijk) tot 100 (erg moeilijk)'")
    print("BUT our current system inverts it to make high scores = easy!")
    print()
    print("CONCLUSION: The 100-score inversion might be WRONG!")
    print("The raw formula already produces the correct direction where high = difficult.")

if __name__ == "__main__":
    analyze_lint_formula()