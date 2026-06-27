from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pandas as pd
import time
from datetime import datetime
from io import StringIO
import json
import os

# =====================================================================
# CONFIGURATION & ENVIRONMENT ABSTRACTION
# =====================================================================
# Target endpoints are pulled via environment variables or set to sandbox domains 
# to comply with rate boundaries and enterprise data privacy policies.
BASE_URL = os.environ.get("SOURCE_PIPELINE_URL", "https://sandbox.example-agricultural-data.com/mandi/")
FILE_NAME = "Master_Mandi_Normalized_DB.csv"
EXISTING_FILE_ID = os.environ.get("DRIVE_FILE_ID")

STATES = {
    "Andaman and Nicobar": "andaman-and-nicobar", "Andhra Pradesh": "andhra-pradesh", 
    "Arunachal Pradesh": "arunachal-pradesh", "Assam": "assam", "Bihar": "bihar", 
    "Chandigarh": "chandigarh", "Chhattisgarh": "chhattisgarh", "Goa": "goa", 
    "Gujarat": "gujarat", "Haryana": "haryana", "Himachal Pradesh": "himachal-pradesh", 
    "Jammu and Kashmir": "jammu-and-kashmir", "Karnataka": "karnataka", "Kerala": "kerala", 
    "Madhya Pradesh": "madhya-pradesh", "Maharashtra": "maharashtra", "Manipur": "manipur", 
    "Meghalaya": "meghalaya", "Nagaland": "nagaland", "NCT of Delhi": "nct-of-delhi", 
    "Odisha": "odisha", "Pondicherry": "pondicherry", "Punjab": "punjab", 
    "Rajasthan": "rajasthan", "Tamil Nadu": "tamil-nadu", "Telangana": "telangana", 
    "Tripura": "tripura", "Uttar Pradesh": "uttar-pradesh", "Uttarakhand": "uttarakhand", 
    "West Bengal": "west-bengal"
}

def clean_currency(col):
    """Removes currency symbols and formatting punctuation to cast as float."""
    return col.astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False).str.strip().astype(float)

def scrape_all_states():
    """Executes headless web automation to parse dynamic DOM elements across targets."""
    all_data = []
    
    # Configure headless switches for virtualized cloud container environments
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f"🚀 Starting Data Extraction Ingestion Layer: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for state, slug in STATES.items():
        print(f"Processing regional target: {state}...")
        try:
            driver.get(BASE_URL + slug)
            time.sleep(2)
            
            # Interactive Pagination Loop: Expands dynamic server-side tables safely
            clicks = 0
            while True:
                try:
                    btn_xpath = "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show more')]"
                    btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    driver.execute_script("arguments[0].click();", btn)
                    clicks += 1
                    time.sleep(1.5)
                except:
                    print(f"   ↳ Hydration window finalized for {state} after {clicks} pagination triggers.")
                    break 
            
            # Parse DOM state snapshot using Pandas HTML readers
            html = driver.page_source
            tables = pd.read_html(StringIO(html))
            
            for df in tables:
                if 'Market' in df.columns:
                    # Relational schema transformation layer
                    df['state'] = state.lower()
                    df['market'] = df['Market'].str.strip()
                    df['district'] = df['Market'].str.split(' ').str[0].str.strip()
                    df[['commodity', 'variety']] = df['Commodity'].str.split(' - ', n=1, expand=True)
                    df['commodity'] = df['commodity'].str.strip()
                    df['variety'] = df['variety'].fillna('Standard').str.strip()
                    
                    df['modal_price'] = clean_currency(df['Price'])
                    df[['max_price', 'min_price']] = df['High - Low'].str.split('-', expand=True)
                    df['max_price'] = clean_currency(df['max_price'])
                    df['min_price'] = clean_currency(df['min_price'])
                    df['arrival_date'] = df['Date'].str.strip()
                    
                    api_cols = ['state', 'district', 'market', 'commodity', 'variety', 'min_price', 'max_price', 'modal_price', 'arrival_date']
                    all_data.append(df[api_cols])
                    break
        except Exception as e:
            print(f"⚠️ Exception handled for target {state}: {e}")
            continue

    driver.quit()
    
    # Consolidate and cache staging data layer
    if all_data:
        master_df = pd.concat(all_data, ignore_index=True)
        master_df.to_csv(FILE_NAME, index=False)
        print(f"✅ Master Local Data Cache Compiled. Row Count: {len(master_df)}")
        return True
    return False

def upload_to_drive():
    """Connects to Google Drive API to overwrite the central master storage target file atomically."""
    print("☁️ Instantiating Cloud Upload Sync Pipeline...")
    if not EXISTING_FILE_ID:
        print("❌ CRITICAL ERROR: Target DRIVE_FILE_ID environment parameter is missing.")
        return

    try:
        creds_json = os.environ.get('GCP_CREDENTIALS')
        if not creds_json:
            print("❌ CRITICAL ERROR: GCP_CREDENTIALS authorization string context is empty.")
            return

        # Secure parsing of Service Account authorization descriptors
        credentials_info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        service = build('drive', 'v3', credentials=credentials)
        
        media = MediaFileUpload(FILE_NAME, mimetype='text/csv')
        print(f"📡 Exporting stream payload directly to Cloud ID: {EXISTING_FILE_ID}")
        
        # In-place file update execution logic to preserve active BI visualization semantic layers
        uploaded_file = service.files().update(
            fileId=EXISTING_FILE_ID, 
            media_body=media, 
            fields='id'
        ).execute()
        
        print(f"🎉 SUCCESS! Remote database instance fully synchronized. File Reference: {uploaded_file.get('id')}")

    except Exception as e:
        print(f"❌ PIPELINE SYNC FAILURE DIAGNOSTIC: {str(e)}")
        raise e

if __name__ == "__main__":
    if scrape_all_states():
        upload_to_drive()
