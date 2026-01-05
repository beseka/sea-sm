import streamlit as st
import time
from sentiment_analyzer import TurkishSentimentAnalyzer

# Page Config
st.set_page_config(
    page_title="Türkçe Duygu Analizi",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium" feel
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        color: #333333;
    }
    .stTextArea textarea {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .result-card {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .positive {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .negative {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    h1 {
        font-family: 'Inter', sans-serif;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_analyzer():
    return TurkishSentimentAnalyzer()

def main():
    st.title("Sosyal Medya Türkçe Duygu Analizi")
    st.markdown("### Sosyal Medya Yorumları için Sentimental Analiz Modeli")
    st.markdown("Yorumlarınızı aşağıya girerek duygu durumunu (Pozitif/Negatif) analiz edebilirsiniz. Model emojileri, ironiyi ve sosyal medya dilini anlaması için tasarlandı.")

    st.sidebar.header("Hakkında")
    st.sidebar.info(
        """
        Bu uygulama **BERT** tabanlı bir doğal dil işleme modeli kullanır.
        
        **Özellikler:**
        - Emoji Desteği 
        - Negation Handling
        - Türkçe Dilbilgisi Kuralları
        """
    )
    
    with st.spinner("Model Yükleniyor... (İlk açılışta biraz sürebilir)"):
        analyzer = load_analyzer()

    # Input
    user_input = st.text_area("Yorumunuzu giriniz:", height=150, placeholder="Örn: Bu ürün harika! Kargo çok hızlı geldi. 😍")

    if st.button("Analiz Et"):
        if user_input.strip():
            with st.spinner("Analiz ediliyor..."):
                # Simulate a tiny delay for UX (feeling of processing)
                time.sleep(0.5) 
                
                result = analyzer.predict(user_input)
                
                # Display Results
                label = result['label']
                score = result['score']
                details = result['heuristic_details']
                
                # Determine color class
                card_class = "positive" if label == "POSITIVE" else "negative"
                label_tr = "POZİTİF" if label == "POSITIVE" else "NEGATİF"

                st.markdown(f"""
                <div class="result-card {card_class}">
                    <h2>{label_tr}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                if details:
                    st.markdown("#### Detaylar:")
                    for detail in details:
                        st.info(detail, icon="ℹ️")

                # Json debug view (optional, could be hidden)
                with st.expander("Teknik Detaylar (JSON)"):
                    st.json(result)
        else:
            st.warning("Lütfen analiz için bir metin giriniz.")

if __name__ == "__main__":
    main()
