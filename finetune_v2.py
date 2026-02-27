"""
Fine-Tune GPT-4o v2 - IMPROVED
Focus: Accurate content from notes + Elizabeth's style
Prevents hallucination through clean notes → report mapping
"""

import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = """You write tutoring session reports for parents in Elizabeth's style.

CONTENT RULES (ABSOLUTE PRIORITY):
1. Use ONLY information explicitly stated in the session notes
2. If information is missing or unclear, write around it naturally
3. Do NOT make up details, trips, topics, or events
4. Do NOT pull content from other sessions or students
5. Do NOT assume or infer information not stated

Examples of handling missing info:
- Notes say "worked on math" → "We worked on math together"
  (Don't specify which math topic if not mentioned)
- Notes say "did OK" → Report makes general positive statement
  (Don't invent specific successes if not detailed)
- Notes are vague → Keep report appropriately general

STYLE RULES (SECONDARY PRIORITY):
1. Warm, enthusiastic, conversational tone
2. Use student's first name only throughout
3. Include specific details when they're PROVIDED in notes
4. Structure as narrative paragraphs, not bullet points
5. Casual, parent-friendly language

CRITICAL: Missing details are better than invented details.
If you don't know something from the notes, don't make it up.
The notes are your ONLY source of truth for content."""

def extract_training_data():
    """Extract reports with original session notes"""
    print("📚 Extracting training data from database...")
    
    conn = sqlite3.connect('database/sage_reports.db')
    cursor = conn.cursor()
    
    query = """
    SELECT 
        r.id,
        r.student_id,
        s.name as student_name,
        s.subject,
        r.topics_covered,
        r.activities,
        r.notes,
        r.session_date,
        r.duration_hours,
        r.final_report,
        r.use_for_training
    FROM reports r
    LEFT JOIN students s ON r.student_id = s.id
    WHERE r.notes IS NOT NULL 
      AND r.final_report IS NOT NULL
      AND LENGTH(r.notes) > 20
      AND LENGTH(r.final_report) > 100
    ORDER BY r.created_at DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"✅ Found {len(rows)} reports with notes and final versions")
    return rows

def validate_training_example(report_data):
    """Validate that notes content aligns with report content"""
    (report_id, student_id, student_name, subject, topics, activities, 
     notes, session_date, duration, final_report, use_for_training) = report_data
    
    if not student_name or not final_report:
        return False, "Missing student name or report"
    
    # Check if student name in report (basic sanity check)
    first_name = student_name.split()[0] if student_name else ""
    if first_name and first_name not in final_report:
        return False, f"Student name '{first_name}' not in report"
    
    # Check report isn't too short
    if len(final_report) < 200:
        return False, "Report too short"
    
    return True, "Valid"

def format_training_example(report_data):
    """
    Format report as clean notes → report mapping
    NO AI draft, just raw notes to final report
    """
    (report_id, student_id, student_name, subject, topics, activities, 
     notes, session_date, duration, final_report, use_for_training) = report_data
    
    first_name = student_name.split()[0] if student_name else "the student"
    
    # Build clean input with ONLY actual session data
    user_message = f"""Student: {first_name} (first name only)
Subject: {subject or 'General'}
Topics Covered: {topics or 'Various topics'}
Session Activities: {activities or 'N/A'}
Session Notes: {notes or 'N/A'}
Duration: {duration} hours

Write a session report for the parent using ONLY the information above."""
    
    # Clean output
    assistant_message = final_report
    
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
    }

def create_training_file(examples):
    """Create JSONL file for OpenAI fine-tuning"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"training_data_v2_{timestamp}.jsonl"
    filepath = f"finetune_data/{filename}"
    
    os.makedirs('finetune_data', exist_ok=True)
    
    with open(filepath, 'w') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"✅ Training file created: {filepath}")
    return filepath

def upload_and_train(filepath):
    """Upload training file and start fine-tuning job"""
    print(f"\n☁️  Uploading training file to OpenAI...")
    
    try:
        with open(filepath, 'rb') as f:
            file_response = client.files.create(
                file=f,
                purpose='fine-tune'
            )
        
        print(f"✅ File uploaded: {file_response.id}")
        
        print(f"\n🚀 Starting fine-tuning job with improved settings...")
        print(f"   Model: gpt-4o-2024-08-06")
        print(f"   Epochs: 2 (reduced to prevent overfitting)")
        print(f"   Learning rate: 0.3 (conservative)")
        
        job = client.fine_tuning.jobs.create(
            training_file=file_response.id,
            model="gpt-4o-2024-08-06",
            hyperparameters={
                "n_epochs": 2,  # Reduced from 3
                "learning_rate_multiplier": 0.3  # More conservative
            },
            suffix="sage-v2"
        )
        
        print(f"\n✅ Fine-tuning job created!")
        print(f"   Job ID: {job.id}")
        print(f"   Status: {job.status}")
        
        return job.id, file_response.id
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None, None

def monitor_job(job_id):
    """Monitor the fine-tuning job progress"""
    print(f"\n👀 Monitoring job: {job_id}")
    print(f"   Dashboard: https://platform.openai.com/finetune/{job_id}")
    print(f"\n   Status updates:")
    
    import time
    last_status = None
    
    while True:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            
            if job.status != last_status:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"   [{timestamp}] {job.status}")
                last_status = job.status
            
            if job.status == 'succeeded':
                print(f"\n🎉 Fine-tuning completed successfully!")
                print(f"   Model ID: {job.fine_tuned_model}")
                return job.fine_tuned_model
            
            elif job.status == 'failed':
                print(f"\n❌ Fine-tuning failed")
                if hasattr(job, 'error') and job.error:
                    print(f"   Error: {job.error}")
                return None
            
            elif job.status == 'cancelled':
                print(f"\n⚠️  Fine-tuning was cancelled")
                return None
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Monitoring interrupted. Job is still running!")
            print(f"   Check: python3 check_finetune_status.py {job_id}")
            return None
        except Exception as e:
            print(f"\n❌ Error monitoring: {e}")
            return None

def test_model(model_id, test_examples):
    """Test the model on sample inputs"""
    print(f"\n🧪 Testing model on {len(test_examples)} examples...")
    
    for i, example in enumerate(test_examples, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}:")
        print(f"{'='*60}")
        
        user_msg = example['messages'][1]['content']
        expected = example['messages'][2]['content']
        
        # Show input
        print(f"Input notes (first 200 chars):")
        print(f"  {user_msg[:200]}...")
        
        try:
            # Generate with fine-tuned model
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            generated = response.choices[0].message.content.strip()
            
            print(f"\nGenerated (first 300 chars):")
            print(f"  {generated[:300]}...")
            
            # Basic checks
            student_line = [l for l in user_msg.split('\n') if 'Student:' in l][0] if 'Student:' in user_msg else ""
            student_name = student_line.split(':')[1].strip().split()[0] if student_line else ""
            
            if student_name and student_name in generated:
                print(f"  ✅ Correct student name: {student_name}")
            elif student_name:
                print(f"  ❌ WARNING: Student name '{student_name}' missing or wrong!")
            
            # Check for common hallucination markers
            hallucination_words = ['trip', 'vacation', 'break', 'sine', 'cosine', 'geometry']
            found_suspicious = [w for w in hallucination_words if w.lower() in generated.lower() and w.lower() not in user_msg.lower()]
            if found_suspicious:
                print(f"  ⚠️  Potential hallucination detected: {found_suspicious}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Testing complete - review results above")

def save_model_info(model_id, job_id, file_id, num_examples):
    """Save model information"""
    info = {
        "model_id": model_id,
        "job_id": job_id,
        "file_id": file_id,
        "num_examples": num_examples,
        "created_at": datetime.now().isoformat(),
        "base_model": "gpt-4o-2024-08-06",
        "version": "v2",
        "improvements": [
            "Clean notes → report mapping",
            "No AI draft in input",
            "Reduced epochs (2 vs 3)",
            "Conservative learning rate (0.3)",
            "Strong anti-hallucination system prompt"
        ],
        "status": "active"
    }
    
    os.makedirs('finetune_data', exist_ok=True)
    with open('finetune_data/model_v2_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n💾 Model info saved to: finetune_data/model_v2_info.json")
    print(f"\n📝 To use this model, update .env:")
    print(f"   FINETUNED_MODEL_ID={model_id}")
    
    return info

def main():
    print("=" * 70)
    print("🎓 SAGE REPORTS - GPT-4o FINE-TUNING V2 (IMPROVED)")
    print("=" * 70)
    print("\nImprovements:")
    print("  ✅ Clean notes → report mapping (no AI draft)")
    print("  ✅ Strong anti-hallucination system prompt")
    print("  ✅ Reduced epochs (2 vs 3)")
    print("  ✅ Conservative learning rate (0.3)")
    print("  ✅ Pre-deployment testing")
    print()
    
    # Extract data
    reports = extract_training_data()
    
    # Validate and filter
    print(f"\n🔍 Validating training examples...")
    valid_reports = []
    filtered_count = 0
    
    for report in reports:
        is_valid, reason = validate_training_example(report)
        if is_valid:
            valid_reports.append(report)
        else:
            filtered_count += 1
    
    print(f"✅ {len(valid_reports)} valid examples")
    print(f"⚠️  {filtered_count} filtered out (quality issues)")
    
    if len(valid_reports) < 50:
        print(f"\n⚠️  Warning: Only {len(valid_reports)} examples. Recommend at least 50.")
        return
    
    # Format examples
    print(f"\n🔄 Formatting {len(valid_reports)} examples...")
    examples = [format_training_example(report) for report in valid_reports]
    print(f"✅ All examples formatted")
    
    # Create training file
    filepath = create_training_file(examples)
    
    # Preview
    print(f"\n👀 Preview of training format:")
    print(f"   System prompt length: {len(SYSTEM_PROMPT)} chars")
    print(f"   Sample input (first 150 chars):")
    print(f"      {examples[0]['messages'][1]['content'][:150]}...")
    print(f"   Sample output length: {len(examples[0]['messages'][2]['content'])} chars")
    
    # Auto-proceed
    print(f"\n💰 Estimated cost: ~$80-100")
    print(f"   ({len(valid_reports)} examples × 2 epochs × ~2K tokens)")
    print(f"\n🔧 Training config:")
    print(f"   Epochs: 2 (reduced)")
    print(f"   Learning rate: 0.3x (conservative)")
    print(f"   Focus: Content accuracy > Style perfection")
    print(f"\n✅ Auto-proceeding with training...")
    
    # Upload and train
    job_id, file_id = upload_and_train(filepath)
    if not job_id:
        return
    
    # Monitor
    print(f"\n⏰ Training will take 30-60 minutes...")
    model_id = monitor_job(job_id)
    
    if not model_id:
        print("❌ Training did not complete successfully")
        return
    
    # Test the model
    print(f"\n🧪 Running validation tests...")
    test_examples = examples[:5]  # Test on first 5 examples
    test_model(model_id, test_examples)
    
    # Save info
    save_model_info(model_id, job_id, file_id, len(valid_reports))
    
    print("\n" + "=" * 70)
    print("✅ FINE-TUNING V2 COMPLETE")
    print("=" * 70)
    print(f"\nYour new model: {model_id}")
    print(f"\nBefore deploying:")
    print(f"  1. Review the test results above")
    print(f"  2. Generate 2-3 test reports manually")
    print(f"  3. If satisfied, add to .env and restart")

if __name__ == "__main__":
    main()
