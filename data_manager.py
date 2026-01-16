import json
import logging
import pandas as pd
import streamlit as st
from typing import Dict, Optional, List, Any
from pathlib import Path
from config import DATA_FILE, LOG_FILE
# Try importing GSheets, but don't fail if strictly local dev without packages
try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self.use_cloud = False
        self.conn = None
        
        # Check if we should try cloud storage
        # 1. Dependency exists
        # 2. Secrets exist (specifically 'connections.gsheets' or 'gcp_service_account')
        try:
             if HAS_GSHEETS and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                try:
                    self.conn = st.connection("gsheets", type=GSheetsConnection)
                    self.use_cloud = True
                    logger.info("Using Google Sheets for storage.")
                except Exception as e:
                    logger.error(f"Failed to connect to Google Sheets: {e}. Falling back to local.")
        except FileNotFoundError:
            # st.secrets raises FileNotFoundError if no secrets file exists locally
            pass
        except Exception:
            # Generic catch for other secrets issues
            pass
        
        if not self.use_cloud:
            self._ensure_data_file()

    def _ensure_data_file(self):
        """Ensure local data file exists with valid JSON."""
        if not self.data_file.exists():
            self.save_data({})
        else:
            try:
                # Just verify it loads
                with open(self.data_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                logger.error("Corrupted data file found. Backing up and resetting.")
                self.data_file.rename(self.data_file.with_suffix('.bak'))
                self.save_data({})

    def load_data(self) -> Dict:
        """Load data from either Google Sheets or local JSON."""
        if self.use_cloud:
            try:
                # Read from Sheet 1. Expected format: Date col, other cols.
                df = self.conn.read(worksheet="Sheet1", ttl=0) # ttl=0 for fresh data
                if df.empty:
                    return {}
                
                # Convert DF back to Dict logic {date: {row_data}}
                # Ensure date column is string
                if 'date' not in df.columns:
                    logger.warning("Google Sheet missing 'date' column.")
                    return {}
                
                df['date'] = df['date'].astype(str)
                # Convert to records
                records = df.to_dict('records')
                # Map to {date: record}
                data_dict = {row['date']: row for row in records}
                return data_dict

            except Exception as e:
                logger.error(f"Cloud load failed: {e}. Returning empty.")
                return {} # Return empty on failure to prevent crashing
        else:
            # Local fallback
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading local data: {e}")
                return {}

    def save_data(self, data: Dict) -> bool:
        """Save data to storage."""
        if self.use_cloud:
            try:
                # Convert Dict {date: {row}} back to DataFrame
                df = pd.DataFrame(list(data.values()))
                
                # Ensure date is first column for readability
                if 'date' in df.columns:
                    cols = ['date'] + [c for c in df.columns if c != 'date']
                    df = df[cols]
                
                # Update the sheet
                self.conn.update(worksheet="Sheet1", data=df)
                return True
            except Exception as e:
                logger.error(f"Cloud save failed: {e}")
                st.error("Failed to save to Cloud Database.")
                return False
        else:
            try:
                with open(self.data_file, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception as e:
                logger.error(f"Error saving local data: {e}")
                return False

    def save_entry(self, date: str, entry: Dict) -> bool:
        """Save a single day's entry."""
        # For efficiency in a real app, we might just append a row.
        # But for simplicity and consistency with the dict structure, we load-update-save.
        # Google Sheets API is fast enough for this scale.
        data = self.load_data()
        data[date] = entry
        logger.info(f"Saving entry for {date} (Cloud: {self.use_cloud})")
        return self.save_data(data)

    def get_entry(self, date: str) -> Dict:
        """Retrieve a specific day's entry."""
        data = self.load_data()
        return data.get(date, {})

    def get_date_range(self, days: int) -> Dict:
        """Get data for the last N days."""
        data = self.load_data()
        from utils import get_date_range
        dates = get_date_range(days)
        return {d: data.get(d) for d in dates if d in data}

    def get_statistics(self) -> Dict[str, float]:
        """Calculate basic statistics from data."""
        data = self.load_data()
        if not data:
            return {"avg_severity": 0.0, "avg_sleep": 0.0, "avg_stress": 0.0}
            
        total_entries = len(data)
        
        avg_severity = sum(float(d.get('symptom_severity', 0)) for d in data.values()) / total_entries
        avg_sleep = sum(float(d.get('sleep_hours', 0)) for d in data.values()) / total_entries
        avg_stress = sum(float(d.get('stress_level', 0)) for d in data.values()) / total_entries
        
        return {
            "avg_severity": round(avg_severity, 1),
            "avg_sleep": round(avg_sleep, 1),
            "avg_stress": round(avg_stress, 1)
        }
    
    def get_processed_data(self) -> pd.DataFrame:
        """
        Load data and convert to DataFrame with advanced features:
        - Rolling averages
        - Lagged features
        """
        data = self.load_data()
        from utils import convert_to_dataframe
        df = convert_to_dataframe(data)
        
        if df.empty:
            return df
            
        # Ensure correct types
        cols_to_numeric = ['symptom_severity', 'sleep_hours', 'stress_level', 'exercise']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 1. Rolling Averages (Trend Analysis)
        if len(df) >= 3: 
            df['severity_7d_avg'] = df['symptom_severity'].rolling(window=7, min_periods=1).mean()
            df['stress_7d_avg'] = df['stress_level'].rolling(window=7, min_periods=1).mean()
        
        # 2. Lagged Features (Causal Analysis)
        if 'stress_level' in df.columns:
            df['stress_lag1'] = df['stress_level'].shift(1)
        if 'sleep_hours' in df.columns:
            df['sleep_lag1'] = df['sleep_hours'].shift(1)
        if 'symptom_severity' in df.columns:
            df['severity_lag1'] = df['symptom_severity'].shift(1)

        return df

    def delete_entry(self, date: str) -> bool:
        """Remove an entry."""
        data = self.load_data()
        if date in data:
            del data[date]
            logger.info(f"Deleted entry for {date}")
            return self.save_data(data)
        return False
