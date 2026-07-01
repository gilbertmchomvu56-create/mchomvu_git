"""
Sentiment Analysis using TextBlob Polarity Scoring
Methodology: tz_complaint_analysis.ipynb — Step 5.1
Institutions: NMB Bank, CRDB Bank, Vodacom M-Pesa, Tigo Pesa
"""
from textblob import TextBlob

INSTITUTIONS = ['Vodacom', 'Tigo', 'NMB', 'CRDB']

def get_polarity(text):
    """Returns TextBlob polarity score (-1 to +1)"""
    return TextBlob(str(text)).sentiment.polarity

def polarity_to_label(score):
    """Maps polarity score to sentiment label (same thresholds as notebook)"""
    if score > 0.05:
        return 'Positive'
    elif score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def predict_sentiment(text):
    """Full prediction — returns sentiment, confidence, polarity"""
    score = get_polarity(text)
    sentiment = polarity_to_label(score)
    confidence = round(0.5 + min(abs(score), 1.0) / 2, 2)
    return {
        'sentiment': sentiment,
        'confidence': confidence,
        'polarity': round(score, 3)
    }

def predict_bulk(texts):
    return [predict_sentiment(str(t)) for t in texts]

def detect_institution(text):
    """Detect which institution the complaint is about"""
    text_lower = str(text).lower()
    for inst in INSTITUTIONS:
        if inst.lower() in text_lower:
            return inst
    return 'Other'
