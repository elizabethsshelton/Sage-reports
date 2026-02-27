"""Test report generation with fine-tuned model"""
import os
from dotenv import load_dotenv
load_dotenv()

from backend.ai_service import AIService

# Initialize with OpenAI
ai_service = AIService(provider='openai')

print(f"Provider: {ai_service.provider}")
print(f"Model: {ai_service.model}")
print(f"Client: {ai_service.client}")

# Try generating a simple report
try:
    report = ai_service.generate_report(
        student_name="Test Student",
        subject="Math",
        topics_covered="Algebra",
        activities="Practice problems",
        notes="Student did well, needs more practice with factoring",
        sample_reports=[],
        previous_reports=[]
    )
    print("\n✅ Report generated successfully!")
    print("\n" + "="*60)
    print(report)
    print("="*60)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
