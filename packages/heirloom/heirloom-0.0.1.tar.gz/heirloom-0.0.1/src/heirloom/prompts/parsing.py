import json
import re


def parse_jsx_like_text(text: str) -> list[dict]:
    messages = []
    
    # Regex to find top-level tags like <system>, <user>, <assistant>, <tool>
    # It captures the tag name, its attributes, and its inner content.
    # (?s) is a flag that makes '.' match newlines.
    pattern = re.compile(r"<(?P<tag>\w+)(?P<attrs>.*?)>(.*?)(?:</(?P=tag)>)", re.DOTALL)
    
    # Regex to parse attributes like name="..." id="..."
    attr_pattern = re.compile(r'(\w+)="([^"]+)"')

    for match in pattern.finditer(text):
        tag = match.group('tag')
        attrs_str = match.group('attrs').strip()
        content = match.group(3).strip()

        if tag == 'system' or tag == 'user':
            messages.append({"role": tag, "content": content})
            
        elif tag == 'assistant':
            # The assistant message contains a tool call, parse it
            tool_match = re.search(r'<tool\s+name="([^"]+)"\s+id="([^"]+)">\s*({[\s\S]*?})\s*</tool>', content, re.DOTALL)
            if tool_match:
                name, tool_id, args_json_str = tool_match.groups()
                # Ensure arguments are a properly formatted JSON string
                args_dict = json.loads(args_json_str)
                
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_id,
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args_dict) # OpenAI expects a string
                        }
                    }]
                })
                
        elif tag == 'tool':
            # This is a tool result message, parse its attributes
            attrs = dict(attr_pattern.findall(attrs_str))
            tool_call_id = attrs.get('id')
            if tool_call_id:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": content
                })
                
    return messages
