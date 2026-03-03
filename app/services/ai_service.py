from google.genai import client, types
import json

def ai_to_json(text: str):
    """
    يحول نص PDF إلى جدول JSON باستخدام Gemini
    """

    prompt = f"""
Convert the following text into a table in JSON format.

Text:
{text}

Return only JSON, like:
[
  {{"Column1": "Value1", "Column2": "Value2"}},
  ...
]
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    content = response.result[0].content[0].text

    try:
        data = json.loads(content)
    except Exception as e:
        print("AI JSON parsing error:", e)
        data = []

    return data
