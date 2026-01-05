import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import emoji
import re

class TurkishSentimentAnalyzer:
    def __init__(self, model_name="savasy/bert-base-turkish-sentiment-cased"):
        """
        Initializes the Turkish Sentiment Analyzer with a BERT-based model.
        """
        self.model_name = model_name
        self.pipeline = None
        self._load_model()
        
        # Emoji sentiment dictionary (can be expanded)
        self.emoji_sentiments = {
            'positive': ['😂', '❤️', '😍', '🔥', '👏', '👍', '💪', '💖', '🥰', '🤣'],
            'negative': ['😭', '😡', '🤬', '👎', '🤮', '😒', '🙄', '😤', '🤢', '💩']
        }

    def _load_model(self):
        """Loads the model and tokenizer."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def preprocess(self, text):
        """
        Cleans the text for better model performance.
        - Removes mentions (@user)
        - Removes URLs
        - Normalizes repeated characters (e.g., "cooook" -> "cook") - kept simple
        """
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        
        return text.strip()

    def analyze_heuristics(self, text):
        """
        Analyzes the text for emojis, irony, and negation signals.
        Returns a modifier score (-1 to 1 range approx) to adjust the model's confidence.
        """
        score_modifier = 0.0
        details = []

        # Emoji Analysis
        found_emojis = [c for c in text if c in emoji.EMOJI_DATA]
        pos_emoji_count = sum(1 for e in found_emojis if e in self.emoji_sentiments['positive'])
        neg_emoji_count = sum(1 for e in found_emojis if e in self.emoji_sentiments['negative'])

        if pos_emoji_count > 0:
            score_modifier += 0.2 * pos_emoji_count
            details.append(f"Found {pos_emoji_count} positive emojis.")
        if neg_emoji_count > 0:
            score_modifier -= 0.2 * neg_emoji_count
            details.append(f"Found {neg_emoji_count} negative emojis.")

        if "(!)" in text or "(!.)" in text:
            score_modifier -= 1.5 
            details.append("Irony marker '(!)' detected.")
        
        if '...' in text and '?' in text:
             pass 

        if "mükemmel ötesi" in text.lower() or "efsane" in text.lower():
             score_modifier += 0.1

        # Specific phrases that BERT might get wrong or that contain complex negation
        lower_text = text.lower()
        
        # "Fena değil" -> Not bad (Positive context usually)
        if "fena değil" in lower_text or "kötü değil" in lower_text:
             score_modifier += 1.5 # Stronger push to positive (was 0.8)
             details.append("Detected 'not bad' pattern (corrected to Positive).")

        # "Sıkıntı yok", "Sorun yok" -> No problem (Positive)
        if "sıkıntı yok" in lower_text or "sorun yok" in lower_text or "dert değil" in lower_text:
             score_modifier += 0.5
             details.append("Detected 'no problem' pattern (Positive).")
             
        # "Tavsiye etmem" -> Not recommended (Strong Negative)
        # BERT usually gets this, but beneficial to reinforce
        if "tavsiye etmem" in lower_text or "sakın almayın" in lower_text or "uzak durun" in lower_text:
             score_modifier -= 0.5
             details.append("Detected warning phrase (Negative).")

        # Explicit strong negative phrases/insults (slang)
        # These are often missed or misunderstood by the model as positive (e.g. "bok gibi")
        strong_negative_phrases = [
            "bok gibi", "beş para etmez", "rezalet", "iğrenç", "lanet olsun", 
            "allah belanı", "aptal", "gerizekalı", "çöp", "kusturucu", "yüz karası",
            "berbat ötesi", "defol", "zıkkımın kökü", "hayal kırıklığı"
        ]
        
        for phrase in strong_negative_phrases:
            if phrase in lower_text:
                score_modifier -= 2.0 # Very strong negation
                details.append(f"Detected strong negative phrase: '{phrase}'")


        return score_modifier, details

    def predict(self, text):

        clean_text = self.preprocess(text)
        if not clean_text and text: # If cleaning removed everything (e.g. only a link)
             clean_text = text # Fallback

        # BERT Prediction
        result = self.pipeline(clean_text)[0]
        model_label = result['label']
        model_score = result['score']
        current_val = model_score if model_label.lower() == 'positive' else -model_score

        # Apply Heuristics
        heuristic_score, heuristic_details = self.analyze_heuristics(text)
        
        # Combine
        final_val = current_val + heuristic_score
        
        # Clamp between -1 and 1
        final_val = max(min(final_val, 1.0), -1.0)
        
        # Determine final label
        final_label = "POSITIVE" if final_val > 0 else "NEGATIVE"
        final_confidence = abs(final_val)

        return {
            "label": final_label,
            "score": final_confidence,
            "original_text": text,
            "processed_text": clean_text,
            "heuristic_details": heuristic_details,
            "model_raw_label": model_label,
            "model_raw_score": model_score
        }

if __name__ == "__main__":
    # Quick Test
    analyzer = TurkishSentimentAnalyzer()
    examples = [
        "Bu ürün harika! 😍",
        "Hiç beğenmedim, berbat. 🤮",
        "Ne kadar da güzel bir paketleme (!)",
        "Eh işte fena değil."
    ]
    
    print(f"{'Text':<40} | {'Label':<10} | {'Score':<6} | Notes")
    print("-" * 80)
    for text in examples:
        res = analyzer.predict(text)
        notes = ", ".join(res['heuristic_details'])
        print(f"{text:<40} | {res['label']:<10} | {res['score']:.4f} | {notes}")
