import os
import anthropic
from openai import OpenAI

openai_client = OpenAI()
anthropic_client = anthropic.Anthropic()


def generate_code_with_codex(prompt: str) -> str:
    response = openai_client.responses.create(
        model="codex-mini-latest",
        input=prompt,
    )
    return response.output_text


def review_code_with_claude(original_prompt: str, generated_code: str) -> str:
    review_prompt = f"""You are an expert code reviewer. A user requested the following:

<user_request>
{original_prompt}
</user_request>

OpenAI Codex generated this code:

<generated_code>
{generated_code}
</generated_code>

Please:
1. Review the code for correctness, security issues, and best practices
2. Improve the code where needed
3. Return the final, improved version of the code with a brief explanation of any changes made"""

    with anthropic_client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": review_prompt}],
    ) as stream:
        return stream.get_final_message()


def run_pipeline(prompt: str) -> dict:
    print(f"[1/2] Generating code with OpenAI Codex...")
    generated_code = generate_code_with_codex(prompt)
    print(f"Codex output:\n{generated_code}\n")

    print(f"[2/2] Reviewing and improving with Claude...")
    claude_response = review_code_with_claude(prompt, generated_code)

    result = {
        "prompt": prompt,
        "codex_output": generated_code,
        "claude_review": [],
    }

    for block in claude_response.content:
        if block.type == "text":
            result["claude_review"].append({"type": "text", "content": block.text})
        elif block.type == "thinking":
            result["claude_review"].append({"type": "thinking", "content": block.thinking})

    return result


if __name__ == "__main__":
    prompt = input("Enter your code generation prompt: ").strip()
    if not prompt:
        prompt = "Write a Python function that reads a CSV file and returns a list of dictionaries"

    output = run_pipeline(prompt)

    print("\n" + "=" * 60)
    print("FINAL CLAUDE-REVIEWED OUTPUT")
    print("=" * 60)
    for block in output["claude_review"]:
        if block["type"] == "text":
            print(block["content"])
