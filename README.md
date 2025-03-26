# 🚀 Sapiens - AI-Powered Banking Recommendations

## 📌 Table of Contents

- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction

This project is an intelligent banking recommendation system that leverages AI to provide personalized financial product recommendations. It analyzes user spending patterns, interests, and financial behavior to suggest the most suitable Wells Fargo credit cards and financial products. By combining natural language processing with financial data analysis, Sapiens makes banking recommendations more accessible and personalized than ever before.

## 🎥 Demo

📚 [Live Demo](https://drive.google.com/file/d/1BVdtTW4s25q2qA5pSDChtbd1y1MAu4nf/view?usp=sharing) \
🎢 [Video Demo](https://drive.google.com/file/d/1BVdtTW4s25q2qA5pSDChtbd1y1MAu4nf/view?usp=sharing) 


## 💡 Inspiration

The inspiration for This project came from our growing interest in Generative AI (GenAI) and the strong support we received from Wells Fargo’s management. We realized that AI could significantly enhance financial services for our customers. Participating in this hackathon allowed us to challenge ourselves, gain hands-on experience, and develop AI-driven banking solutions.

We aimed to:

- Analyze real spending patterns and user interests
- Provide personalized recommendations based on actual behavior
- Make banking recommendations accessible through voice interaction
- Focus specifically on Wells Fargo products to ensure relevant suggestions

## ⚙️ What It Does

This project is designed to provide a seamless AI-driven banking experience by offering personalized recommendations based on user data and voice inputs.

- *Smart Product Recommendations*: Analyzes spending patterns and user interests to recommend the most suitable Wells Fargo credit cards and financial products.
- *Voice Interaction*: Accepts voice queries in MP3 format, transcribes the audio, and generates personalized banking recommendations.
- *Behavioral Analysis*: Considers multiple factors including:
  - Spending categories and patterns
  - Monthly transaction amounts
  - User interests and hobbies
  - Location and income level
  - Credit score
- *Social Media Integration*: Updates recommendations based on new social media posts to keep suggestions relevant.
- *Detailed Reasoning*: Provides clear explanations for each recommendation, including how it matches user behavior.

## 🧐 How We Built It

As developers exploring GenAI and LLMs for the first time, we focused on learning and applying AI-driven technologies effectively. Our approach involved:

### 1. Data Processing Layer

- *Financial Data Processing*

  - Implemented FinancialDataLoader to handle multiple data sources:
    - Bank transactions from Account\_Statement.csv
    - Credit card usage from credit\_card\_transactions.csv
    - KYC information from KYC\_Details.csv
  - Used pandas for efficient data manipulation and analysis
  - Implemented data validation and cleaning pipelines

- *Spending Pattern Analysis*

  - Developed DataExtractor class to analyze:
    - Monthly spending trends
    - Category-wise expenditure
    - Transaction frequency patterns
    - Merchant preferences
  - Generated spending summaries with:
    - Total bank spend
    - Credit card spend
    - Category breakdowns
    - Monthly averages

- *User Interest Extraction*

  - Processed social media posts and emails
  - Implemented interest categorization
  - Generated user interest profiles
  - Tracked interest changes over time

### 2. AI/ML Layer

- *Mistral 7B Integration*

  - Implemented LLMInteraction class for recommendation generation
  - Used Mistral 7B Instruct v0.2 (Q4\_K\_M quantized) for:
    - Natural language understanding
    - Context-aware recommendations
    - Reasoning generation
  - Optimized prompts for:
    - Credit card recommendations
    - Product suggestions
    - User behavior analysis

- *Voice Processing*

  - Implemented VoiceProcessor for audio interaction
  - Supported multiple audio formats:
    - WAV (native)
    - MP3 (with conversion)
    - M4A (with conversion)
  - Used Google Speech Recognition for transcription
  - Implemented audio format conversion using pydub

### 3. Integration Layer

- *Wells Fargo Product Integration*

  - Direct integration with Wells Fargo product data:
    - Credit cards from Wells\_Fargo\_Credit\_Card\_Details.csv
    - Loans from Wells\_Fargo\_Loan\_Details.csv
  - Implemented product matching algorithm
  - Generated personalized recommendations based on:
    - User spending patterns
    - Income level
    - Credit score
    - Location
    - Interests

- *Real-time Updates*

  - Implemented incremental update system
  - Processed new social media posts
  - Updated user interests dynamically
  - Regenerated recommendations efficiently

### 4. Output Generation

- *JSON-based Output System*
  - Generated structured recommendations in JSON format
  - Created separate files for:
    - Spending analysis
    - KYC details
    - User interests
    - Product recommendations
    - Credit card suggestions

## 🚧 Challenges We Faced

Developing This project was an exciting learning experience, but as new learners in GenAI and LLM-based solutions, we faced multiple challenges:

1. *Learning About LLMs*: Understanding how large language models function and their applications in financial recommendations.
2. *How to Use LLMs*: Experimenting with prompt engineering and fine-tuning to improve recommendation accuracy.
3. *Using Cursor AI for Faster Development*: Leveraging Cursor AI to streamline the coding and debugging process.
4. *How to Use Voice Models*: Integrating and fine-tuning voice recognition models for improved accuracy in voice-based queries.
5. *Generating Sample Data*: Creating realistic transaction data and user profiles for testing the recommendation system.

## 🏃 How to Run

1. *Clone the Repository*
   ```bash
   git clone https://github.com/your-repo/sapiens.git
   cd sapiens
   ```

2. *Create Virtual Environment*
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   .\venv\Scripts\activate   # Windows
   ```

3. *Install Dependencies*
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. *Download AI Models*
   ```bash
   mkdir -p models
   # Download and save model manually from: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
   ```
5. *Set Up Environment Variables*
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your configuration
   # Required variables:
   MODEL_PATH=models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   DATA_DIR=data
   OUTPUT_DIR=output
   ```
6. *Create Required Directories*
   ```bash
   # Create data directory
   mkdir -p data

   # Create output directory
   mkdir -p output

   # Create audio directory for voice files
   mkdir -p audio
   ```
7. *Basic Usage*
   ```bash
   python main.py
    #Load all your financial data
    #Analyze spending patterns
    #Generate personalized recommendations
    #Save results in the output directory
   ```
   
## 🏠 Tech Stack

- 🔹 Core: Python 3.8+
- 🔹 AI/ML: Mistral 7B, SpeechRecognition
- 🔹 Data Processing: pandas, numpy
- 🔹 Audio Processing: pydub
- 🔹 Voice: Google Speech Recognition
- 🔹 File Formats: WAV, MP3, M4A
- 🔹 Data Sources: CSV, JSON

## Developeres 
- 🔹 Raj Tushar 
- 🔹 Beeravalli Raja Kishor Reddy
- 🔹 Ramalingam Sasidharan 

