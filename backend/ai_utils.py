"""
AI-powered dataset analysis and step validation using OpenRouter + Gemini 2.5 Flash
"""

import json
import httpx
import pandas as pd
from typing import Optional
import dotenv
import os

# Load environment variables from a .env file if present
dotenv.load_dotenv()

# Allow overriding via environment, provide sensible defaults for non-secret values
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# Store dataset context per session
_DATASET_CONTEXT = {}


async def analyze_dataset(session_id: str, df: pd.DataFrame) -> dict:
    """
    Analyze dataset comprehensively and store context for later validation.
    Returns dataset insights and recommendations.
    """
    print(f"\n🔍 [ANALYZE_DATASET] Started for session: {session_id}")
    
    # Calculate statistics
    stats = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isnull().sum().to_dict(),
        "duplicates": len(df) - len(df.drop_duplicates()),
        "numeric_cols": df.select_dtypes(include=['float64', 'int64']).columns.tolist(),
        "categorical_cols": df.select_dtypes(include=['object']).columns.tolist(),
        "memory_usage": df.memory_usage(deep=True).sum() / 1024**2,  # MB
    }
    
    print(f"📊 Dataset Stats: {stats['shape'][0]} rows, {stats['shape'][1]} columns")
    print(f"📈 Numeric: {len(stats['numeric_cols'])}, Categorical: {len(stats['categorical_cols'])}")
    
    # Add numeric statistics
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    if not numeric_df.empty:
        stats["numeric_stats"] = {
            "mean": numeric_df.mean().to_dict(),
            "std": numeric_df.std().to_dict(),
            "min": numeric_df.min().to_dict(),
            "max": numeric_df.max().to_dict(),
            "correlation": numeric_df.corr().to_dict(),
        }
    
    # Create prompt for dataset analysis
    prompt = f"""Analyze this dataset and provide insights:

Dataset Shape: {stats['shape']}
Columns: {stats['columns']}
Data Types: {json.dumps(stats['dtypes'], indent=2)}
Missing Values: {json.dumps(stats['missing'], indent=2)}
Duplicate Rows: {stats['duplicates']}
Memory Usage: {stats['memory_usage']:.2f} MB

Numeric Columns: {stats['numeric_cols']}
Categorical Columns: {stats['categorical_cols']}

Provide a brief analysis (2-3 sentences) covering:
1. Data quality issues (missing values, duplicates)
2. Column recommendations (what to keep/remove)
3. Preprocessing suggestions (scaling, encoding, outlier handling)

Format as JSON with keys: "quality_issues", "column_recommendations", "preprocessing_suggestions"
"""
    
    insights = await _call_ai(prompt, "dataset_analysis")
    
    # Store context for future validations (including dataframe for later use)
    _DATASET_CONTEXT[session_id] = {
        "stats": stats,
        "insights": insights,
        "df": df,  # Store full dataframe for validation context
    }
    
    print(f"✅ [ANALYZE_DATASET] Completed for session: {session_id}\n")
    
    return {
        "stats": stats,
        "ai_insights": insights,
    }


async def validate_step(
    session_id: str,
    step_name: str,
    action_description: str,
    affected_columns: list = None,
    **kwargs
) -> dict:
    """
    Validate a preprocessing step using AI.
    Returns recommendation and whether to warn the user.
    
    step_name: "drop_columns", "handle_missing", "remove_outliers", "scale", "encode", "correlation"
    action_description: Human-readable description of what will happen
    """
    
    print(f"\n⚙️  [VALIDATE_STEP] Step: {step_name} | Session: {session_id}")
    print(f"📝 Action: {action_description}")
    print(f"🔧 Affected Columns: {affected_columns}")
    
    context = _DATASET_CONTEXT.get(session_id, {})
    stats = context.get("stats", {})
    df = context.get("df", None)
    
    # Build sample data string (first 2 rows)
    sample_data_str = ""
    if df is not None and not df.empty:
        sample_rows = df.head(2).to_string()
        sample_data_str = f"\nSample Data (first 2 rows):\n{sample_rows}\n"
    
    # Calculate impact information
    impact_str = ""
    if affected_columns and df is not None:
        # Get data for affected columns
        affected_data = df[affected_columns].describe().to_string() if affected_columns else ""
        impact_str = f"\nImpact Summary - Affected Columns Statistics:\n{affected_data}\n"
    
    prompt = f"""You are a data preprocessing expert. Review this preprocessing step and decide if it's safe and beneficial.

DATASET CONTEXT:
- Shape: {stats.get('shape', 'unknown')}
- All Columns: {stats.get('columns', [])}
- Data Types: {json.dumps(stats.get('dtypes', {}), indent=2, default=str)}
- Missing Values: {json.dumps(stats.get('missing', {}), indent=2, default=str)}
- Numeric Columns: {stats.get('numeric_cols', [])}
- Categorical Columns: {stats.get('categorical_cols', [])}
{sample_data_str}

PREPROCESSING STEP:
- Step Type: {step_name}
- Description: {action_description}
- Affected Columns: {affected_columns}
- Additional Details: {json.dumps(kwargs, indent=2, default=str)}
{impact_str}

IMPORTANT: If columns will be DROPPED, list them explicitly. Analyze if this will:
1. Cause information loss?
2. Affect model performance?
3. Create data quality issues?

Evaluate this action:
1. Is it a good idea? (yes/no)
2. Any risks or warnings? (list them, especially column drops)
3. Recommendation (brief 1-2 sentences)

Format as JSON with keys: "is_good", "risks", "recommendation"
"""
    
    print(f"📊 Prompt includes: stats, columns, sample rows, affected column stats\n")
    
    validation = await _call_ai(prompt, f"validate_{step_name}")
    
    # Ensure risks is always a list
    risks = validation.get('risks', [])
    if isinstance(risks, str):
        # If AI returned a string, split by common separators
        risks = [r.strip() for r in risks.split('\n') if r.strip()]
    if not isinstance(risks, list):
        risks = []
    
    is_recommended = validation.get('is_good', True)
    if isinstance(is_recommended, str):
        is_recommended = is_recommended.lower() in ['yes', 'true', 'y']
    
    print(f"✅ [VALIDATE_STEP] Decision: {'✓ RECOMMENDED' if is_recommended else '⚠️  CAUTION'}")
    print(f"📌 Recommendation: {validation.get('recommendation', 'N/A')}")
    if risks:
        print(f"⚠️  Risks/Warnings:")
        for i, risk in enumerate(risks, 1):
            print(f"   {i}. {risk}")
    print()
    
    return {
        "step": step_name,
        "action": action_description,
        "is_recommended": is_recommended,
        "warnings": risks,
        "recommendation": validation.get("recommendation", "Proceed with caution"),
    }


async def _call_ai(prompt: str, context_tag: str = "") -> dict:
    """
    Call OpenRouter API with Gemini 2.5 Flash model.
    """
    try:
        if not OPENROUTER_KEY:
            print("❌ AI Error: OPENROUTER_KEY is not set in the environment. Set it in your system env or .env file.")
            return {"error": "Missing OPENROUTER_KEY environment variable"}

        print(f"\n{'='*80}")
        print(f"[AI] {context_tag.upper()} - SENDING PROMPT")
        print(f"{'='*80}")
        print(f"PROMPT:\n{prompt}\n")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENROUTER_API_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "HTTP-Referer": "https://automl.local",
                    "X-Title": "AutoML-AI",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                }
            )
            
            if response.status_code != 200:
                print(f"❌ AI API Error: {response.status_code}")
                return {"error": f"AI service returned {response.status_code}"}
            
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print(f"[AI] {context_tag.upper()} - RAW RESPONSE")
            print(f"{'='*80}")
            print(f"RAW CONTENT:\n{content}\n")
            
            # Try to parse JSON from response
            try:
                # Extract JSON if wrapped in markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                parsed = json.loads(content)
                print(f"[AI] {context_tag.upper()} - PARSED RESPONSE")
                print(f"{'='*80}")
                print(f"PARSED JSON:\n{json.dumps(parsed, indent=2)}\n")
                return parsed
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse JSON: {str(e)}")
                print(f"Returning raw response\n")
                return {"raw_response": content}
                
    except Exception as e:
        print(f"❌ AI Error: {str(e)}")
        return {"error": str(e)}


def cleanup_session(session_id: str) -> None:
    """Clean up AI context for a session."""
    _DATASET_CONTEXT.pop(session_id, None)
