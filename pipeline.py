import anthropic

# Paste your Anthropic API key here (get it from https://console.anthropic.com)
API_KEY = "your-api-key-here"

client = anthropic.Anthropic(api_key=API_KEY)

prompt = input("What code do you want? ")

print("\nGenerating...\n")

with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=4096,
    messages=[{"role": "user", "content": f"Write Python code for: {prompt}. Return only the code, no explanation."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()
