"""
Fine-Tune GPT-4o on Elizabeth's Report Editing Patterns
Creates a custom model that learns from original AI outputs → final edited versions
"""

import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables first
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_training_data():
    """Extract all reports with both AI-generated and final versions"""
    print("📚 Extracting training data from database...")
    
    conn = sqlite3.connect('database/sage_reports.db')
    cursor = conn.cursor()
    
    # Get all reports with both versions and meaningful edits
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
        r.ai_generated_report,
        r.final_report,
        r.use_for_training
    FROM reports r
    LEFT JOIN students s ON r.student_id = s.id
    WHERE r.ai_generated_report IS NOT NULL 
      AND r.final_report IS NOT NULL
      AND r.ai_generated_report != r.final_report
      AND LENGTH(r.final_report) > 100
    ORDER BY r.created_at DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    print(f"✅ Found {len(rows)} reports with edits")
    return rows

def format_training_example(report_data):
    """
    Format a single report as OpenAI training example
    Using Approach B: Edit Pattern Learning
    """
    (report_id, student_id, student_name, subject, topics, activities, 
     notes, session_date, duration, ai_generated, final_report, use_for_training) = report_data
    
    # Extract first name only
    first_name = student_name.split()[0] if student_name else "the student"
    
    # Build the input context (what the AI will see during training)
    user_message = f"""Student: {first_name}
Subject: {subject or 'General'}
Topics Covered: {topics or 'Various topics'}
Session Activities: {activities or 'N/A'}
Session Notes: {notes or 'N/A'}
Duration: {duration} hours

Here is the AI's first draft of the report:

{ai_generated}

Please revise this report to match the preferred style and tone."""
    
    # The expected output (what we want the AI to learn to generate)
    assistant_message = final_report
    
    # System message defining the role
    system_message = """You are an AI that writes tutoring session reports for parents. You write in a warm, enthusiastic, and conversational style. You include specific details about what the student worked on, how they performed, and areas for improvement. You use the student's first name only. You avoid formal academic language and prefer energetic, parent-friendly phrasing."""
    
    # OpenAI fine-tuning format
    return {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
    }

def create_training_file(examples):
    """Create JSONL file for OpenAI fine-tuning"""
    print(f"\n📝 Creating training file with {len(examples)} examples...")
    
    filename = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    filepath = f"finetune_data/{filename}"
    
    # Create directory if needed
    os.makedirs('finetune_data', exist_ok=True)
    
    # Write JSONL format
    with open(filepath, 'w') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"✅ Training file created: {filepath}")
    return filepath

def upload_and_train(filepath):
    """Upload training file and start fine-tuning job"""
    print(f"\n☁️  Uploading training file to OpenAI...")
    
    try:
        # Upload the file
        with open(filepath, 'rb') as f:
            file_response = client.files.create(
                file=f,
                purpose='fine-tune'
            )
        
        print(f"✅ File uploaded: {file_response.id}")
        
        # Create fine-tuning job
        print(f"\n🚀 Starting fine-tuning job...")
        print(f"   Model: gpt-4o-2024-08-06")
        print(f"   This will take approximately 30-60 minutes...")
        
        job = client.fine_tuning.jobs.create(
            training_file=file_response.id,
            model="gpt-4o-2024-08-06",
            hyperparameters={
                "n_epochs": 3  # 3 passes through the data
            },
            suffix="sage-reports"  # Will appear in model name
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
    print(f"   You can also check status at: https://platform.openai.com/finetune/{job_id}")
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
                if job.error:
                    print(f"   Error: {job.error}")
                return None
            
            elif job.status == 'cancelled':
                print(f"\n⚠️  Fine-tuning was cancelled")
                return None
            
            # Wait before checking again
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Monitoring interrupted. Job is still running!")
            print(f"   Check status at: https://platform.openai.com/finetune/{job_id}")
            return None
        except Exception as e:
            print(f"\n❌ Error monitoring job: {e}")
            return None

def save_model_info(model_id, job_id, file_id, num_examples):
    """Save the fine-tuned model information"""
    print(f"\n💾 Saving model information...")
    
    info = {
        "model_id": model_id,
        "job_id": job_id,
        "file_id": file_id,
        "num_examples": num_examples,
        "created_at": datetime.now().isoformat(),
        "base_model": "gpt-4o-2024-08-06",
        "status": "active"
    }
    
    # Save to JSON file
    os.makedirs('finetune_data', exist_ok=True)
    with open('finetune_data/model_info.json', 'w') as f:
        json.dumps(info, f, indent=2)
    
    # Also update .env file
    print(f"\n📝 To use this model, add to your .env file:")
    print(f"   FINETUNED_MODEL_ID={model_id}")
    
    return info

def main():
    """Main fine-tuning pipeline"""
    print("=" * 60)
    print("🎓 SAGE REPORTS - GPT-4o FINE-TUNING")
    print("=" * 60)
    
    # Step 1: Extract data
    reports = extract_training_data()
    
    if len(reports) < 10:
        print(f"\n⚠️  Warning: Only {len(reports)} examples found. Recommend at least 50.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Step 2: Format examples
    print(f"\n🔄 Formatting {len(reports)} examples for training...")
    examples = [format_training_example(report) for report in reports]
    print(f"✅ All examples formatted")
    
    # Step 3: Create training file
    filepath = create_training_file(examples)
    
    # Show a preview
    print(f"\n👀 Preview of first training example:")
    print(f"   System: {examples[0]['messages'][0]['content'][:100]}...")
    print(f"   User input length: {len(examples[0]['messages'][1]['content'])} chars")
    print(f"   Expected output length: {len(examples[0]['messages'][2]['content'])} chars")
    
    # Step 4: Auto-proceed (user already confirmed)
    print(f"\n💰 Estimated cost: ~$80-100 for training")
    print(f"   ({len(reports)} examples × ~2K tokens × 2 × 3 epochs)")
    print(f"\n✅ Proceeding with fine-tuning...")
    
    # Step 5: Upload and start training
    job_id, file_id = upload_and_train(filepath)
    
    if not job_id:
        print("❌ Failed to start fine-tuning job")
        return
    
    # Step 6: Monitor progress
    print(f"\n⏰ The fine-tuning job is now running...")
    print(f"   Monitoring progress (this will take 30-60 minutes)...")
    
    model_id = monitor_job(job_id)
    if model_id:
        save_model_info(model_id, job_id, file_id, len(reports))
    
    print("\n" + "=" * 60)
    print("✅ FINE-TUNING PIPELINE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
