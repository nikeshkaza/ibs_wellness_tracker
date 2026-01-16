import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"
OPENAI_MAX_TOKENS = 1000

# UI Labels & Mappings
SEVERITY_LABELS = {
    1: "Minimal", 2: "Very Mild", 3: "Mild", 4: "Low-Moderate",
    5: "Moderate", 6: "Noticeable", 7: "Uncomfortable", 8: "Severe",
    9: "Very Severe", 10: "Unbearable"
}

SLEEP_QUALITY_LABELS = {
    1: "Terrible", 2: "Very Poor", 3: "Poor", 4: "Below Average",
    5: "Average", 6: "Decent", 7: "Good", 8: "Very Good",
    9: "Excellent", 10: "Perfect"
}

STRESS_LEVEL_LABELS = {
    1: "Zen", 2: "Calm", 3: "Relaxed", 4: "Manageable",
    5: "Neutral", 6: "Busy", 7: "Stressed", 8: "High Stress",
    9: "Very High", 10: "Overwhelming"
}

# Advanced Tracking Options
BRISTOL_SCALE = {
    1: "Type 1: Separate hard lumps (Severe Constipation)",
    2: "Type 2: Lumpy sausage (Mild Constipation)",
    3: "Type 3: Sausage with cracks (Normal)",
    4: "Type 4: Smooth sausage/snake (Ideal)",
    5: "Type 5: Soft blobs, clear-cut edges (Mild Diarrhea)",
    6: "Type 6: Mushy pieces, ragged edges (Moderate Diarrhea)",
    7: "Type 7: Watery, no solid pieces (Severe Diarrhea)"
}

MEAL_SPEED_OPTIONS = [
    "Slow / Mindful (20+ min)", 
    "Average (10-20 min)", 
    "Fast / Rushed (<10 min)", 
    "Distracted (TV/Phone)"
]

STRESS_TYPE_OPTIONS = [
    "None", 
    "Acute (Sudden Event)", 
    "Chronic (Background Anxiety)", 
    "Social/Work", 
    "Physical/Fatigue"
]

# File Paths
DATA_FILE = Path("data/ibs_data.json")
LOG_FILE = Path("logs/app.log")

# Prompt Templates
DAILY_ANALYSIS_PROMPT = """
You are an expert IBS Wellness Assistant. Analyze the following daily log and return a Valid JSON object.
Do NOT return markdown formatting like ```json ... ```. Just the raw JSON object.

Data:
{data}

Required JSON Structure:
{{
    "wellness_score": <int 1-100 based on overall health>,
    "summary": "<concise summary of the day>",
    "triggers": ["<potential trigger 1>", "<potential trigger 2>"],
    "recommendations": ["<actionable tip 1>", "<actionable tip 2>"]
}}
"""

WEEKLY_ANALYSIS_PROMPT = """
You are an expert IBS Wellness Assistant. Analyze the following weekly data and return a Valid JSON object.
Do NOT return markdown formatting like ```json ... ```. Just the raw JSON object.

Data:
{data}

Required JSON Structure:
{{
    "wellness_score": <int 1-100 average wellness>,
    "trend_analysis": "<analysis of symptom/lifestyle trends>",
    "identified_triggers": [
        {{"trigger": "<trigger name>", "confidence": "<High/Medium/Low>"}}
    ],
    "recommendations": ["<strategic recommendation 1>", "<strategic recommendation 2>"]
}}
"""
