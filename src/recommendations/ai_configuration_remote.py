import os
import pdb
from groq import Groq
import re
from dotenv import load_dotenv

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=my_api_key,
)

# Setup local coding models to use
# remote_summarization_model = "llama-3.3-70b-versatile"
# remote_summarization_model = "deepseek-r1-distill-llama-70b"
remote_summarization_model = "meta-llama/llama-4-scout-17b-16e-instruct"
# ----------------------------
# Remote LLM Response
# ----------------------------
def get_remote_response(content):    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model=remote_summarization_model
    )

    response = chat_completion.choices[0].message.content

    # Retrieve token usage
    tokens_used = chat_completion.usage.total_tokens
    input_tokens = chat_completion.usage.prompt_tokens
    output_tokens = chat_completion.usage.completion_tokens
    
    print(f"Total tokens used: {tokens_used}")
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")

    if response:      
        if "deepseek" in remote_summarization_model:       # For deepseek models, remove <think> tags
            return remove_think_tags(response)
        else:
            return response    
    else:
        return "Error!", "None"
    
def remove_think_tags(text):
    # Use regex to remove anything between <think> and </think>
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text