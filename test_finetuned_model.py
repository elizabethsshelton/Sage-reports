"""
Test the fine-tuned model with a sample report generation
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def test_model(model_id=None):
    """Test the fine-tuned model with a sample input"""
    
    # Get model ID from .env if not provided
    if not model_id:
        model_id = os.getenv('FINETUNED_MODEL_ID')
    
    if not model_id:
        print("❌ No model ID provided and FINETUNED_MODEL_ID not set in .env")
        print("Usage: python test_finetuned_model.py [model_id]")
        return
    
    print(f"\n{'='*60}")
    print(f"TESTING FINE-TUNED MODEL")
    print(f"{'='*60}")
    print(f"Model: {model_id}")
    
    # Sample test input
    test_input = """Student: Alex
Subject: Mathematics
Topics Covered: Algebra, Quadratic Equations
Session Activities: Worked through practice problems, reviewed factoring techniques
Session Notes: Alex struggled with factoring at first but really picked it up by the end. Made some mistakes with signs but caught on quickly. Needs to practice more but showed great improvement. Was enthusiastic about learning.
Duration: 1.5 hours

Here is the AI's first draft of the report:

Session Report for Alex
Date: Today
Subject: Mathematics

Topics Covered:
- Algebra
- Quadratic Equations

Session Activities:
Alex worked through several practice problems focusing on factoring techniques. We reviewed the fundamental concepts and applied them to increasingly complex equations.

Additional Notes:
Alex demonstrated progress in understanding factoring methods. Some difficulty was observed with sign management, though improvement was noted throughout the session. Continued practice is recommended.

Please revise this report to match the preferred style and tone."""
    
    print(f"\n📝 Test Input:")
    print(f"Student: Alex (Math session on quadratic equations)")
    print(f"\n⏳ Generating report with fine-tuned model...\n")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that writes tutoring session reports for parents. You write in a warm, enthusiastic, and conversational style."
                },
                {
                    "role": "user",
                    "content": test_input
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        generated_report = response.choices[0].message.content
        
        print(f"{'='*60}")
        print(f"GENERATED REPORT:")
        print(f"{'='*60}")
        print(generated_report)
        print(f"\n{'='*60}")
        
        # Show token usage
        print(f"\n📊 Token Usage:")
        print(f"   Input: {response.usage.prompt_tokens}")
        print(f"   Output: {response.usage.completion_tokens}")
        print(f"   Total: {response.usage.total_tokens}")
        print(f"   Estimated cost: ${(response.usage.prompt_tokens * 3.75 + response.usage.completion_tokens * 15) / 1_000_000:.4f}")
        
        print(f"\n✅ Test complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    import sys
    model_id = sys.argv[1] if len(sys.argv) > 1 else None
    test_model(model_id)
