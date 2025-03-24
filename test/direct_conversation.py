import requests
import json

# Configuration
BASE_URL = "http://localhost:5002"  # The Flask server runs on port 5002

def test_direct_conversation(message):
    """
    Send a message to the direct_conversation endpoint and get the LLM response.
    """
    # Endpoint URL
    url = f"{BASE_URL}/direct_conversation"
    
    # Request headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "message": message
    }
    
    # Send POST request
    response = requests.post(url, headers=headers, json=payload)
    
    # Print the result
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("\nResponse:")
        print(f"Assistant: {result['content']}")
        print("\nChain of Thoughts:")
        print(result['chain_of_thoughts'])
        return result
    else:
        print("\nError:")
        print(response.text)
        return None

if __name__ == "__main__":
    # Test message
    message = "Hello, I'm feeling quite stressed today. My mother has been forgetting to take her medication."
    
    # Run the test
    test_direct_conversation(message) 