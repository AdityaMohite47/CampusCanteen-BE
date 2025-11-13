import json , re

def sanitize_llm_json(text : str):
    if not text or not isinstance(text, str):
        raise ValueError("Empty or invalid response text")

    # Extract JSON inside triple backticks if present
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    # Remove any leading or trailing junk outside the JSON braces
    json_match = re.search(r"({.*})", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    # Fix invalid JSON newlines inside strings (unescaped)
    # This replaces raw newlines between quotes with '\n'
    def fix_newlines_in_strings(s):
        return re.sub(
            r'(?<!\\)"((?:[^"\\]|\\.)*?)"(?=\s*[,:}])',
            lambda m: '"' + m.group(1).replace("\n", "\\n") + '"',
            s,
            flags=re.DOTALL
        )

    text = fix_newlines_in_strings(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nCleaned text:\n{text}")