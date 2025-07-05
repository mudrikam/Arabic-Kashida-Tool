import re
import json

def parse_gemini_response(response):
    """
    Parse Gemini response to extract clean text for the textarea.
    If JSON is found, return all fields as multi-line text without field names.
    """
    if not response:
        return ""
    json_obj = extract_json_object_from_response(response)
    if json_obj:
        return format_json_fields(json_obj)
    text = response.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.split('\n')
        if len(lines) > 2:
            text = '\n'.join(lines[1:-1])
        else:
            text = text[3:-3]
    text = re.sub(r'`([^`]+)`', r'\1', text)
    explanation_patterns = [
        r'^Here\'s the.*?:\s*',
        r'^Here is the.*?:\s*',
        r'^The corrected.*?:\s*',
        r'^Corrected.*?:\s*',
        r'^Result.*?:\s*',
        r'^Answer.*?:\s*',
        r'^Translation.*?:\s*',
    ]
    for pattern in explanation_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_json_object_from_response(response):
    """
    Extract JSON object from Gemini response.
    Tries to find JSON in code blocks or inline.
    """
    if not response:
        return None
    json_patterns = [
        r'```json\s*\n(.*?)\n```',
        r'```\s*\n(\{.*?\})\n```',
        r'```\s*(\{.*?\})```',
    ]
    for pattern in json_patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    json_match = re.search(r'\{.*?\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    return None

def format_json_fields(json_obj):
    """
    Format JSON object fields as content only without field names.
    """
    if not isinstance(json_obj, dict):
        return ""
    
    lines = []
    
    if "result" in json_obj and json_obj["result"]:
        lines.append(str(json_obj["result"]))
    
    if "arti" in json_obj and json_obj["arti"]:
        lines.append("\n" + str(json_obj["arti"]))
    
    if "cara_baca" in json_obj and json_obj["cara_baca"]:
        lines.append("\n" + str(json_obj["cara_baca"]))
    
    if "asbabun_nuzul" in json_obj and json_obj["asbabun_nuzul"]:
        lines.append("\n" + str(json_obj["asbabun_nuzul"]))
    
    if "sumber" in json_obj and json_obj["sumber"]:
        lines.append("\n" + str(json_obj["sumber"]))
    
    if "hadith_text" in json_obj and json_obj["hadith_text"]:
        lines.append("\n" + str(json_obj["hadith_text"]))
    
    if "hadith_source" in json_obj and json_obj["hadith_source"]:
        lines.append("\n" + str(json_obj["hadith_source"]))
    
    if "hadith_warning" in json_obj and json_obj["hadith_warning"]:
        lines.append("\n⚠️ " + str(json_obj["hadith_warning"]))
    
    return '\n'.join(lines).strip()

def extract_arabic_text(response):
    """
    Extract only Arabic text from the response, removing explanations.
    """
    if not response:
        return ""
    text = parse_gemini_response(response)
    lines = text.split('\n')
    arabic_lines = []
    for line in lines:
        line = line.strip()
        if line and has_arabic_text(line):
            arabic_lines.append(line)
    return '\n'.join(arabic_lines)

def has_arabic_text(text):
    """
    Check if text contains Arabic characters.
    """
    arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
    return bool(re.search(arabic_pattern, text))