BASE_CONTEXT_SYSTEM_PROMPT = (
    "You are an expert e-commerce analyst specializing in Shopify stores. "
    "Your task is to analyze store content and generate a comprehensive Base Context that captures the essence of the business."
)


BASE_CONTEXT_USER_PROMPT = (
    "Analyze the following Shopify store content and generate a Base Context following this exact JSON schema:\n\n"
    "{\n"
    '  "store_name": "string (the store\'s name)",\n'
    '  "url": "string (the store URL)",\n'
    '  "overview": "string (≤200 words describing what the store sells, key features, and value proposition)",\n'
    '  "icp": {\n'
    '    "one_liner": "string (concise description of ideal customer)",\n'
    "    \"personas\": [\"string array (customer types/segments, e.g., 'Busy professionals', 'Tech enthusiasts')\"],\n"
    '    "needs": ["string array (customer pain points/requirements the store addresses)"],\n'
    '    "buying_motivation": ["string array (reasons customers buy from this store)"]\n'
    "  },\n"
    '  "policies": {\n'
    '    "shipping": "string (shipping policy summary, or \'Not specified\' if not found)",\n'
    '    "returns": "string (returns policy summary, or \'Not specified\' if not found)"\n'
    "  },\n"
    '  "key_urls": {\n'
    '    "about": "string (about page URL if found, empty string if not)",\n'
    '    "faq_or_returns": "string (FAQ or returns page URL if found, empty string if not)"\n'
    "  },\n"
    "  \"tone\": [\"string array (brand tone characteristics, e.g., 'Professional', 'Friendly', 'Playful')\"],\n"
    '  "version": 1,\n'
    '  "last_built_at": "string (current ISO8601 timestamp)"\n'
    "}\n\n"
    "Important guidelines:\n"
    "1. The overview MUST be 200 words or less - be concise but comprehensive\n"
    "2. Extract actual information from the content - don't make assumptions\n"
    "3. If specific information isn't found, use reasonable defaults (e.g., 'Not specified' for policies)\n"
    "4. Personas should be specific customer types, not generic descriptions\n"
    "5. Tone should reflect the actual brand voice from the content\n"
    "6. All arrays must have at least one meaningful item\n"
    "7. Generate content in English even if the source is in another language\n\n"
    "Store Name Extraction:\n"
    "- CRITICAL: Extract the actual store/brand name from the content, NOT from the URL\n"
    "- Look for the store name in: page titles, headers, logo alt text, about sections, copyright notices\n"
    "- Prefer the official brand name as it appears in the content over URL-based extraction\n"
    "- If multiple variations exist, use the most formal/complete version found in the content\n"
    "- Only fall back to URL-based extraction if no clear store name is found in the content\n\n"
    "Store URL: {url}\n\n"
    "Store Content:\n{content}"
)
