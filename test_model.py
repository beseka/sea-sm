from sentiment_analyzer import TurkishSentimentAnalyzer

def run_tests():
    print("Initializing Analyzer for Testing...")
    analyzer = TurkishSentimentAnalyzer()
    
    test_cases = [
        ("Mükemmel bir gün!", "POSITIVE", "Basic Positive"),
        ("Berbat bir servis.", "NEGATIVE", "Basic Negative"),
        ("Hiç sevmedim 🤮", "NEGATIVE", "Negative with Emoji"),
        ("Bayıldım 😍", "POSITIVE", "Positive with Emoji"),
        ("Harika (!)", "NEGATIVE", "Irony (Positive word + (!))"),
        ("Mükemmel ötesi bir film.", "POSITIVE", "Slang 'Mükemmel ötesi'"),
        ("Güzel değil.", "NEGATIVE", "Negation 'değil'"),
        ("İnanılmaz kötü.", "NEGATIVE", "Intensifier + Negative"),
        ("http://link.com harika", "POSITIVE", "URL removal check"),
        ("Fena değil aslında.", "POSITIVE", "Heuristic 'Fena değil'"),
        ("Sıkıntı yok, gayet iyi.", "POSITIVE", "Heuristic 'Sıkıntı yok'"),
        ("Tavsiye etmem, kaçın.", "NEGATIVE", "Heuristic 'Tavsiye etmem'"),
        ("Bok gibi bir film.", "NEGATIVE", "Insult 'bok gibi'"),
        ("Bu ürün beş para etmez.", "NEGATIVE", "Phrase 'beş para etmez'"),
        ("Tam anlamıyla rezalet.", "NEGATIVE", "Phrase 'rezalet'"),
        ("Lezzeti iğrençti.", "NEGATIVE", "Word 'iğrenç'"),
        ("Zıkkımın kökü.", "NEGATIVE", "Slang 'zıkkımın kökü'"),
    ]
    
    print(f"\n{'Test Case':<40} | {'Expected':<10} | {'Actual':<10} | {'Result':<6}")
    print("-" * 80)
    
    passed = 0
    for text, expected, description in test_cases:
        result = analyzer.predict(text)
        actual = result['label']
        is_pass = "PASS" if actual == expected else "FAIL"
        if is_pass == "PASS": passed += 1
        
        print(f"{text:<40} | {expected:<10} | {actual:<10} | {is_pass}")
        with open("results.txt", "a", encoding="utf-8") as f:
             f.write(f"{text} | {expected} | {actual} | {is_pass}\n")
        
        if is_pass == "FAIL":
            print(f"   -> Details: {result['heuristic_details']}")
            print(f"   -> Model Score: {result['model_raw_score']}, Adjusted: {result['score']}")
            with open("results.txt", "a", encoding="utf-8") as f:
                f.write(f"   -> Details: {result['heuristic_details']}\n")
                f.write(f"   -> Model Score: {result['model_raw_score']}, Adjusted: {result['score']}\n")

    print("-" * 80)
    with open("results.txt", "a", encoding="utf-8") as f:
        print(f"Tests Passed: {passed}/{len(test_cases)}")
        f.write(f"Tests Passed: {passed}/{len(test_cases)}\n")

if __name__ == "__main__":
    run_tests()
