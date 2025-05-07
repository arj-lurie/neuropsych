import pdb

from pydantic import BaseModel
from typing import List
import json
from collections import defaultdict


# === Models ===
class RecommendationTheme(BaseModel):
    theme: str
    count: int
    sample_recommendations: List[str]
    all_recommendations: List[str]  # <-- New field

class RecommendationSummary(BaseModel):
    themes: List[RecommendationTheme]

def merge_theme_summaries(summaries: List[RecommendationSummary]) -> RecommendationSummary:
    theme_map = defaultdict(lambda: {
        "count": 0,
        "sample_recommendations": set(),
        "all_recommendations": set()
    })

    # Merge data
    for summary in summaries:
        for theme in summary.themes:
            key = theme.theme.lower().strip()  # normalize theme names
            theme_map[key]["count"] += theme.count
            theme_map[key]["sample_recommendations"].update(theme.sample_recommendations)
            theme_map[key]["all_recommendations"].update(theme.all_recommendations)

    # Create merged themes
    merged_themes = [
        RecommendationTheme(
            theme=key.title(),
            count=value["count"],
            sample_recommendations=list(value["sample_recommendations"])[:3],
            all_recommendations=list(value["all_recommendations"])
        )
        for key, value in theme_map.items()
    ]

    return RecommendationSummary(themes=merged_themes)

# === Generate Instruction Per File ===
def get_ai_instruction_single_file(file_text: str, file_name: str):
    # Get the schema without the 'indent' argument
    schema_dict = RecommendationSummary.model_json_schema()
    # Convert the schema to a pretty-printed JSON string
    schema_json = json.dumps(schema_dict, indent=2)

    return f"""
        You are analyzing the recommendation section from a professional report.

        **Report Name:** {file_name}

        **Your Task:**
        1. Extract all actionable recommendations.
        2. Group similar recommendations under shared themes.
        3. For each theme:
            - Include `count = 1` (for this file).
            - Include **all extracted recommendations** in `all_recommendations`.
            - Include 1–3 of the most representative examples in `sample_recommendations`.

        **Output Format:**
        Respond with valid JSON conforming to this schema:

        {schema_json}

        Here is the report:

        {file_text}
    """