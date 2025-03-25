# Personalized Banking Services

A Python-based system that provides personalized banking product recommendations based on user data, spending patterns, and social media activity.

## Project Structure

```
personalised_banking_services/
├── data/                      # Data directory
│   ├── Account_Statement.csv              # User's bank transactions
│   ├── credit_card_transactions.csv       # Credit card transaction history
│   ├── KYC_Details.csv                    # Know Your Customer details
│   ├── social_media_posts.csv             # User's social media activity
│   ├── emails_to_wells_fargo.csv          # Email communications
│   ├── Receiver_vs_Category.csv           # Transaction categorization
│   ├── Wells_Fargo_Credit_Card_Details.csv# Available credit card products
│   ├── Wells_Fargo_Loan_Details.csv       # Available loan products
│   └── credit_card_list.csv               # User's existing credit cards
├── src/
│   ├── ai/
│   │   ├── llm_interaction.py    # LLM-based recommendation generation
│   │   └── llm_analyzer.py       # LLM-based analysis of user data
│   ├── analysis/
│   │   └── financial_analyzer.py # Financial data analysis
│   ├── data_processing/
│   │   ├── data_loader.py        # Data loading and preprocessing
│   │   └── data_extractor.py     # Feature extraction and analysis
│   └── config.py                 # Configuration settings
├── output/                    # Generated recommendations and analysis
│   ├── spending_analysis.json
│   ├── kyc_details.json
│   ├── user_interests.json
│   ├── product_recommendations.json
│   └── credit_card_recommendations.json
├── main.py                    # Main script
└── README.md                  # This file
```

## Features

1. **Data Processing**
   - Transaction analysis
   - Spending pattern recognition
   - Social media interest extraction
   - KYC information processing

2. **Recommendation Generation**
   - Credit card recommendations
   - Loan recommendations
   - Other financial product suggestions
   - Personalized based on user profile

3. **Real-time Updates**
   - Update recommendations with new social media posts
   - Maintain historical data
   - Incremental updates

## Requirements

1. Python 3.8+
2. Required packages:
   ```
   pandas>=2.0.0
   numpy>=1.24.0
   scikit-learn>=1.3.0
   llama-cpp-python>=0.2.0
   sentence-transformers>=2.2.0
   ```

## LLM Model Details

This project was developed and demoed using:
- Mistral 7B Instruct v0.2 (Q4_K_M quantized version)
- Download from Hugging Face: [mistral-7b-instruct-v0.2.Q4_K_M.gguf](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf)
- Place in the `models` directory

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/personalised_banking_services.git
   cd personalised_banking_services
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Required Models**
   ```bash
   # Create models directory
   mkdir -p models
   
   # Download sentence transformer model
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('models/sentence_transformer')"
   
   # Download Llama model (example using 7B model)
   # Note: You'll need to download the model file manually from Hugging Face
   # and place it in the models directory
   ```

5. **Prepare Data Directory**
   ```bash
   # Create data directory if it doesn't exist
   mkdir -p data
   ```

6. **Configure Data Files**
   Place the following CSV files in the `data` directory:
   - `Account_Statement.csv` - Bank transaction history
   - `credit_card_transactions.csv` - Credit card usage
   - `KYC_Details.csv` - Personal information
   - `social_media_posts.csv` - Social media activity
   - `emails_to_wells_fargo.csv` - Email communications
   - `Receiver_vs_Category.csv` - Transaction categorization
   - `Wells_Fargo_Credit_Card_Details.csv` - Available credit cards
   - `Wells_Fargo_Loan_Details.csv` - Available loan products
   - `credit_card_list.csv` - Existing credit cards

7. **Configure Settings**
   Update the `src/config.py` file with your settings:
   ```python
   # Base directory paths
   BASE_DIR = Path(__file__).parent.parent
   DATA_DIR = BASE_DIR / "data"
   OUTPUT_DIR = BASE_DIR / "output"

   # Data file paths
   DATA_FILES = {
       "transactions": DATA_DIR / "Account_Statement.csv",
       "credit_card_transactions": DATA_DIR / "credit_card_transactions.csv",
       "social_media": DATA_DIR / "social_media_posts.csv",
       "kyc": DATA_DIR / "KYC_Details.csv",
       "emails": DATA_DIR / "emails_to_wells_fargo.csv",
       "receiver_categories": DATA_DIR / "Receiver_vs_Category.csv",
       "credit_cards": DATA_DIR / "Wells_Fargo_Credit_Card_Details.csv",
       "loans": DATA_DIR / "Wells_Fargo_Loan_Details.csv",
       "credit_card_list": DATA_DIR / "credit_card_list.csv"
   }

   # Create output directory if it doesn't exist
   OUTPUT_DIR.mkdir(exist_ok=True)
   ```

8. **Verify Setup**
   ```bash
   # Run a test analysis
   python main.py --test
   ```

### Data Format Requirements

1. **Account Statement CSV**
   ```csv
   Date,Description,Amount,Category
   2024-03-01,Grocery Store,-50.00,Food
   2024-03-02,Salary,3000.00,Income
   ```

2. **Credit Card Transactions CSV**
   ```csv
   Date,Merchant,Amount,Category
   2024-03-01,Amazon,-100.00,Shopping
   2024-03-02,Gas Station,-40.00,Transportation
   ```

3. **KYC Details CSV**
   ```csv
   Field,Value
   Name,John Doe
   Age,30
   Income,75000
   Employment,Full-time
   ```

4. **Social Media Posts CSV**
   ```csv
   Date,Platform,Content,Engagement
   2024-03-20,Twitter,Post content here,15
   2024-03-20,Instagram,Another post,25
   ```

### Troubleshooting

1. **Model Download Issues**
   - Ensure sufficient disk space (at least 10GB)
   - Check internet connection
   - Verify write permissions in the models directory

2. **Data Loading Errors**
   - Verify CSV file formats
   - Check file permissions
   - Ensure all required files are present

3. **Memory Issues**
   - Reduce batch size in config.py
   - Use smaller model variants
   - Close other memory-intensive applications

## Running the Scripts

### 1. Full Pipeline

To run the complete analysis pipeline:

```bash
python main.py
```

This will:
- Load all data from the `data` directory
- Process transactions and user information
- Generate recommendations
- Save results to the `output` directory

### 2. Update with New Social Media Posts

To update recommendations based on new social media activity:

```bash
python main.py --update-social path/to/new_posts.csv
```

The new posts CSV file should have the following format:
```csv
Date,Platform,Content,Engagement
2024-03-20,Twitter,Post content here,15
2024-03-20,Instagram,Another post,25
```

## System Workflow

1. **Data Collection and Loading**
   - System loads various data sources from the `data` directory
   - Transaction data from bank statements and credit cards
   - KYC information and user details
   - Social media posts and engagement metrics
   - Available banking products information

2. **Data Processing Pipeline**
   - `data_loader.py`: 
     - Handles loading and initial preprocessing of all data sources
   - `data_extractor.py`: 
     - Extracts relevant features and patterns from the data
     - Validates data format and completeness
     - Handles missing values and data cleaning

3. **Analysis Phase**
   - `financial_analyzer.py`: 
     - Analyzes spending patterns and transaction history
     - Identifies spending categories and trends
     - Calculates financial metrics and ratios
     - Generates spending analysis reports
   
   - `llm_analyzer.py`:
     - Processes social media posts and user communications
     - Extracts user interests and preferences
     - Analyzes sentiment and engagement patterns
     - Identifies lifestyle indicators

4. **Recommendation Generation**
   - `llm_interaction.py`:
     - Combines insights from financial and social analysis
     - Matches user profile with available products
     - Generates personalized recommendations
     - Provides reasoning for each recommendation

5. **Output Generation**
   - Saves analysis results in JSON format
   - Creates detailed recommendation reports
   - Maintains historical data for trend analysis

6. **Update Process**
   - When new social media posts are added:
     - Only processes the new data
     - Updates user interests and preferences
     - Regenerates recommendations without full pipeline rerun
     - Maintains consistency with existing analysis

## Output Files

1. **spending_analysis.json**
   - Total spending
   - Category-wise spending
   - Top merchants
   - Monthly trends

2. **kyc_details.json**
   - User profile
   - Income details
   - Updated interests and hobbies

3. **user_interests.json**
   - Extracted interests from social media
   - Transaction-based interests

4. **product_recommendations.json**
   - Recommended credit cards
   - Loan suggestions
   - Other financial products
   - Reasons for recommendations

5. **credit_card_recommendations.json**
   - Detailed credit card recommendations
   - Card benefits
   - Annual fees
   - Interest rates

## Error Handling

The system includes comprehensive error handling for:
- Missing files
- Invalid data formats
- Processing errors
- Data validation failures

Error messages are color-coded for better visibility:
- 🔵 Blue: Processing information
- 🟢 Green: Success messages
- 🟡 Yellow: Warnings
- 🔴 Red: Errors 