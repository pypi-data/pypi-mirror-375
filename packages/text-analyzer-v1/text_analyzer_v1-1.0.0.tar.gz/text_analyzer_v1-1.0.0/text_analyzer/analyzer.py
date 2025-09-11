import re

def analyze_text(text):
    """
    Analyze the given text and return statistics.

    :param text: The text to analyze
    :return: Dictionary with word count, sentence count, etc.
    """
    words = re.findall(r'\b\w+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    return {
        'word_count': len(words),
        'sentence_count': len(sentences),
        'character_count': len(text),
        'average_word_length': sum(len(word) for word in words) / len(words) if words else 0
    }
