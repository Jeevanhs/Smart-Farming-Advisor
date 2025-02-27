import streamlit as st
from PIL import Image
import base64
from datetime import datetime
from groq import Groq
import os
from dotenv import load_dotenv
import io
import requests

# Load environment variables
load_dotenv()

groq_client = Groq(api_key='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')


# Page config and styling
st.set_page_config(
    page_title="Smart Farming Advisor", 
    page_icon="🌾", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for more attractive UI
st.markdown("""
    <style>
    /* Global Styling */
    body {
        
        background-size: cover;
        color: #f4f4f4;
        font-family: 'Montserrat', sans-serif;
    }

    /* Full Page Blur Effect */
    .main {
        backdrop-filter: blur(10px);
        background: rgba(0, 0, 0, 0.6);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* Sidebar Enhancements */
    .css-1aumxhk {
        background: linear-gradient(135deg, #1d1d1d, #333);
        color: white;
        border-right: 5px solid #ffcc00;
        box-shadow: 8px 0 15px rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar Buttons */
    .stSidebar .stButton {
        width: 100%;
        margin-bottom: 15px;
        background: linear-gradient(45deg, #ffcc00, #ff6600) !important;
        color: black !important;
        font-weight: bold;
        transition: all 0.5s ease-in-out;
        border-radius: 25px !important;
        box-shadow: 0 5px 15px rgba(255, 204, 0, 0.3);
    }
    .stSidebar .stButton:hover {
        background: linear-gradient(45deg, #ff6600, #cc3300) !important;
        transform: scale(1.1);
    }

    /* Input Fields */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > select, 
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 2px solid #ffcc00 !important;
        border-radius: 25px !important;
        padding: 14px !important;
        font-size: 18px !important;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus, 
    .stSelectbox > div > div > select:focus, 
    .stTextArea textarea:focus {
        border-color: #ff6600 !important;
        box-shadow: 0 0 10px rgba(255, 204, 0, 0.5);
        background: rgba(255, 255, 255, 0.2) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #ffcc00, #ff6600) !important;
        color: black !important;
        font-weight: bold;
        border-radius: 25px !important;
        padding: 15px 30px !important;
        transition: all 0.4s ease-in-out !important;
        font-size: 18px !important;
        text-transform: uppercase;
        box-shadow: 0 6px 15px rgba(255, 204, 0, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff6600, #cc3300) !important;
        transform: scale(1.1);
    }
    
    /* Card Containers */
    .stContainer {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        box-shadow: 0 12px 25px rgba(255, 255, 255, 0.2);
        padding: 35px;
        border: 2px solid #ffcc00;
        transition: all 0.4s ease;
    }
    .stContainer:hover {
        box-shadow: 0 15px 30px rgba(255, 204, 0, 0.4);
        transform: translateY(-8px);
    }
    
    /* Headings */
    h1, h2, h3 {
        color: white;
        font-weight: bold;
        font-family: 'Montserrat', sans-serif;
        text-transform: uppercase;
        background: linear-gradient(to right, #ffcc00, #ff6600);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 14px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #ffcc00, #ff6600);
        border-radius: 12px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #ff6600, #cc3300);
    }
    </style>
    """, unsafe_allow_html=True)



# Utility Functions
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image_with_llama(image):
    try:
        base64_image = encode_image(image)
        
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image in detail and provide insights about the main elements, objects, and any notable characteristics."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Error analyzing image: {str(e)}")

def get_water_advice(crop_type, soil_type):
    prompt = f"""As an agricultural expert, provide detailed water management advice for:
    Crop: {crop_type}
    Soil Type: {soil_type}
    Include watering frequency, amount, and best practices."""
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting water advice: {str(e)}"

def analyze_disease_with_vision(image):
    try:
        base64_image = encode_image(image)
        
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this plant image and identify: \
                                    1. Any visible disease symptoms \
                                    2. Disease name if recognized \
                                    3. Severity level \
                                    4. Potential causes \
                                    5. Treatment recommendations"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Error analyzing plant disease: {str(e)}")

def get_agriculture_advice(question):
    prompt = f"""As an agricultural expert, please provide comprehensive advice about: {question}
    Include:
    - Detailed recommendations
    - Best practices
    - Common mistakes to avoid
    - Sustainable approaches
    - Related topics for further learning"""
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting agriculture advice: {str(e)}"

def get_agricultural_advice(crop_name):
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""As an agricultural expert, provide detailed advice for growing {crop_name}. Include:
    1. Optimal growing conditions
    2. Water requirements
    3. Common issues and solutions
    4. Best practices for maximum yield
    Keep it concise but informative."""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error getting agricultural advice: {str(e)}"

def analyze_crop_image(image):
    crop_analysis = analyze_image_with_llama(image)
    advice = get_agricultural_advice(crop_analysis)
    
    return {
        "crop_analysis": crop_analysis,
        "agricultural_advice": advice
    }

def get_bio_fertilizer_advice(crop_type, soil_type, current_stage):
    prompt = f"""As an agricultural expert, provide detailed bio-fertilizer recommendations for:
    Crop: {crop_type}
    Soil Type: {soil_type}
    Growth Stage: {current_stage}
    
    Include:
    1. Recommended bio-fertilizers
    2. Application methods and timing
    3. Expected benefits
    4. Precautions and best practices
    5. Integration with other organic practices
    6. Cost-effectiveness comparison"""
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting bio-fertilizer advice: {str(e)}"

def get_scheme_information(state, category):
    prompt = f"""As an agricultural financial advisor in India, provide detailed information about current {category} schemes in {state} for small farmers. Include:
    1. Names of available schemes
    2. Eligibility criteria
    3. Maximum loan/subsidy amount
    4. Interest rates (if applicable)
    5. Application process
    6. Required documents
    7. Key benefits
    8. Contact information or where to apply"""
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting scheme information: {str(e)}"

# Session State Management
def change_section(section):
    st.session_state.current_section = section

# Main navigation with icons
def create_sidebar():
    st.sidebar.title("🚜 Smart Farming Assistant")
    sections = [
        ("🏠 Home", "Home"),
        ("🌱 Agriculture Advice", "Agriculture Advice"),
        ("💧 Water Management", "Water Management"),
        ("🔍 Image Analysis", "Image Analysis"),
        ("🏥 Disease Identification", "Disease Identification"),
        ("🌿 Bio Fertilizer Advisory", "Bio Fertilizer Advisory"),
        ("💰 Micro-Loan & Subsidies", "Micro-Loan & Subsidies")
    ]

    for icon_text, section in sections:
        st.sidebar.button(
            icon_text,
            key=f"nav_{section}",
            on_click=change_section,
            args=(section,),
            use_container_width=True
        )

# Section Rendering
def render_section():
    st.markdown(f"# {st.session_state.current_section}")
    st.markdown("---")
    
    if st.session_state.current_section == "Home":
        st.markdown("""
        ## Welcome to Smart Farming Assistant! 🌾
        ### What Can We Help You With?
        - 🌱 Get expert agricultural advice
        - 💧 Optimize water management
        - 🔍 Analyze crop health
        - 🏥 Identify plant diseases
        - 💰 Find farming subsidies
        """)

    elif st.session_state.current_section == "Water Management":
        st.header("Water Management 💧")
        crop_type = st.text_input("Crop Type:")
        soil_type = st.selectbox("Soil Type:", ["Sandy", "Clay", "Loamy", "Silt"])
        if st.button("Get Water Advice"):
            if crop_type:
                water_advice = get_water_advice(crop_type, soil_type)
                st.write(water_advice)
            else:
                st.warning("Please enter a crop type")

    elif st.session_state.current_section == "Image Analysis":
        st.header("Crop Analysis 🔍")
        uploaded_file = st.file_uploader("Upload crop image", type=['png', 'jpg', 'jpeg'], key="analysis")
        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                with st.spinner("Analyzing crop and generating advice..."):
                    results = analyze_crop_image(image)
                st.subheader("Agricultural Advice")
                st.write(results["agricultural_advice"])
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")

    elif st.session_state.current_section == "Disease Identification":
        st.header("Disease Identification 🏥")
        uploaded_file = st.file_uploader("Upload plant image", type=['png', 'jpg', 'jpeg'], key="disease")
        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                with st.spinner("Analyzing plant disease..."):
                    diagnosis = analyze_disease_with_vision(image)
                    st.subheader("Disease Analysis")
                    st.write(diagnosis)
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")

    elif st.session_state.current_section == "Agriculture Advice":
        st.header("Agriculture Advice 🌱")
        user_question = st.text_area("Ask any agriculture related question:", 
                                    placeholder="Example: How do I improve soil fertility naturally?")
        
        if st.button("Get Advice"):
            if user_question:
                with st.spinner("Thinking..."):
                    try:
                        advice = get_agriculture_advice(user_question)
                        st.markdown("### Expert Advice:")
                        st.write(advice)
                        
                        st.markdown("### Related Topics:")
                        st.markdown("""
                        - Soil Management
                        - Crop Rotation
                        - Pest Control
                        - Organic Farming
                        """)
                    except Exception as e:
                        st.error(f"Unable to get advice: {str(e)}")
            else:
                st.warning("Please enter your question first")

    elif st.session_state.current_section == "Bio Fertilizer Advisory":
        st.header("Bio Fertilizer Advisory 🌱")
        
        col1, col2 = st.columns(2)
        
        with col1:
            crop_type = st.text_input("Crop Type:", key="bio_crop")
        soil_type = st.selectbox(
            "Soil Type:",
            ["Sandy", "Clay", "Loamy", "Silt", "Peaty", "Chalky"],
            key="bio_soil"
        )
        growth_stage = st.selectbox(
            "Growth Stage:",
            ["Seedling", "Vegetative", "Flowering", "Fruiting", "Maturity"],
            key="bio_stage"
        )
    
        if st.button("Get Bio-Fertilizer Recommendations", key="bio_advice"):
            if crop_type:
                with st.spinner("Generating recommendations..."):
                    advice = get_bio_fertilizer_advice(crop_type, soil_type, growth_stage)
                    
                    st.markdown("### Recommended Bio-Fertilizer Strategy:")
                    st.write(advice)
            else:
                st.warning("Please enter a crop type")

    elif st.session_state.current_section == "Micro-Loan & Subsidies":
        st.header("Micro-Loan & Subsidy Assistance 💰")
        
        col1, col2 = st.columns(2)
        
        with col1:
            state = st.selectbox(
                "Select State:",
                ["Andhra Pradesh", "Bihar", "Gujarat", "Haryana", "Karnataka", 
                 "Kerala", "Madhya Pradesh", "Maharashtra", "Punjab", "Rajasthan", 
                 "Tamil Nadu", "Telangana", "Uttar Pradesh", "West Bengal"]
            )
            
            category = st.selectbox(
                "Select Category:",
                ["Crop Loans", "Equipment Purchase", "Land Development", 
                 "Irrigation Schemes", "Storage Infrastructure", "All Schemes"]
            )
        
        if st.button("Find Available Schemes"):
            with st.spinner(f"Finding schemes in {state}..."):
                schemes = get_scheme_information(state, category)
                
                st.markdown("### Available Schemes and Benefits")
                st.write(schemes)
                
                # Additional Resources
                st.markdown("### Important Links")
                st.markdown("""
                - [PM Kisan Portal](https://pmkisan.gov.in/)
                - [NABARD Schemes](https://www.nabard.org/)
                - [State Agriculture Department](https://agriculture.gov.in/)
                - [Kisan Credit Card](https://www.government-schemes.com/kisan-credit-card-scheme/)
                """)
                
                # Contact Information
                st.markdown("### Need Help?")
                st.info("""
                Contact Kisan Call Centre:
                - Toll Free: 1800-180-1551
                - Available 24x7
                """)

# Main Application Initialization
def main():
    # Initialize session state
    if 'current_section' not in st.session_state:
        st.session_state.current_section = "Home"

    create_sidebar()
    render_section()

# Application Entry Point
if __name__ == "__main__":
    main()
