import requests
import json

# Setup local coding models to use
# local_coding_model = "codegemma"
# local_summary_model = "gemma:2b"
local_summary_model = "llama3.2"
# local_coding_model = "qwen2.5-coder:32b"

# ----------------------------
# Local LLM Response
# ----------------------------
def get_local_response(content):
    
    messages = [
        {
            "role": "user", 
            "content": content
        },
    ]

    # Combine all messages into a single prompt
    prompt = "\n".join([message["content"] for message in messages])
    
    # Reset the model first
    reset_ai_model(local_summary_model)
    
    # Query Ollama model with combined prompt
    response = query_ollama_model(prompt, model=local_summary_model)  
       
    if response:
        return response
    else:
        return "Error!", "None"

# --------------------------------------------------
# Function to call the Ollama-based Local Model
# --------------------------------------------------
def query_ollama_model(prompt: str, model: str = "llama3.2", response_format: dict = None) -> dict:
    url = "http://127.0.0.1:11434/api/generate"  # Change to your Ollama endpoint if different
    payload = {
        "model": model,  # Name of your model (prometheus-local, llama3.2)
        "prompt": prompt,
        "stream": False,
        "format": response_format,
        "temperature": 0.9        
    }
    headers = {
        "Content-Type": "application/json"
    }
    # pdb.set_trace()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise an error for bad responses

    if response.status_code == 200:
        try:
            # Get the response content and use the passed schema for formatting
            response_data = response.json()['response']  # Adjust based on actual response structure
            
            if response_format:
                # Optionally validate or format according to the response_format here
                return response_data  # Just return raw data for now
            else:
                return response_data
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def reset_ai_model(model):
    url = "http://127.0.0.1:11434/api/generate"  # Change to your Ollama endpoint if different
    payload = {
        "model": model,  # Name of your model (prometheus-local, llama3.2)
        "prompt": "",
        "keep_alive": 0        
    }
    headers = {
        "Content-Type": "application/json"
    }
    # pdb.set_trace()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise an error for bad responses

    if response.status_code == 200:
        try:
            # Get the response content and use the passed schema for formatting
            response_data = response.json()['response']  # Adjust based on actual response structure                    
            return response_data  # Just return raw data for now            
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None