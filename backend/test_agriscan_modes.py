import requests
import json
import os

BASE_URL = "http://localhost:8000/api/v1"

def print_result(mode, result):
    print(f"\n--- {mode} TEST RESULT ---")
    print(json.dumps(result, indent=2))
    print("-" * 30)

def test_chatbot_mode():
    print("\nTesting Mode 2: Kisan Chatbot...")
    
    # Test 1: Fertilizer Query
    payload = {"query": "Best fertilizer for wheat?"}
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            print("✅ Chatbot (Wheat Fertilizer) - Success")
            print_result("CHATBOT", response.json())
        else:
            print(f"❌ Chatbot Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

    # Test 2: Hinglish Query
    payload = {"query": "Patto ka peela padna"}
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            print("✅ Chatbot (Hinglish Yellow Leaves) - Success")
            print_result("CHATBOT (HINGLISH)", response.json())
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_visual_mode():
    print("\nTesting Mode 1: Visual Diagnosis (Image Upload)...")
    
    # Create a dummy image if not exists (although previous step created it)
    # real content is better for mock ai logic check if it reads image
    with open("test_image.jpg", "wb") as f:
        f.write(os.urandom(1024)) # Random bytes

    files = {'file': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')}
    params = {'user_name': 'TestFarmer', 'lang': 'en'}
    
    try:
        response = requests.post(f"{BASE_URL}/scan/upload", files=files, params=params)
        if response.status_code == 200:
            data = response.json()
            # Verify new fields exist
            if "diagnosis" in data and "advisory_text" in data:
                print("✅ Visual Diagnosis - Success (New Fields Found)")
                print_result("VISUAL DIAGNOSIS", {
                    "diagnosis": data.get("diagnosis"),
                    "risk_level": data.get("risk_level"),
                    "advisory_text": data.get("advisory_text"),
                    "action_plan": data.get("action_plan")
                })
            else:
                print("⚠️ Visual Diagnosis - Success but MISSING new fields!")
                print_result("PARTIAL RESPONSE", data)
        else:
             print(f"❌ Upload Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("Running AgriScan AI Mode Tests...\n")
    test_chatbot_mode()
    test_visual_mode()
    print("\nTests Completed.")
