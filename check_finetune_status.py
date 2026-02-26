"""
Check the status of a fine-tuning job
Usage: python check_finetune_status.py [job_id]
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def check_status(job_id):
    """Check and display the status of a fine-tuning job"""
    try:
        job = client.fine_tuning.jobs.retrieve(job_id)
        
        print(f"\n{'='*60}")
        print(f"FINE-TUNING JOB STATUS")
        print(f"{'='*60}")
        print(f"Job ID: {job.id}")
        print(f"Status: {job.status}")
        print(f"Model: {job.model}")
        print(f"Created: {job.created_at}")
        
        if job.status == 'succeeded':
            print(f"\n✅ SUCCESS!")
            print(f"Fine-tuned Model ID: {job.fine_tuned_model}")
            print(f"\nTo use this model, add to .env:")
            print(f"FINETUNED_MODEL_ID={job.fine_tuned_model}")
        
        elif job.status == 'running' or job.status == 'validating_files':
            print(f"\n⏳ Job is still running...")
            if job.estimated_finish:
                print(f"Estimated finish: {job.estimated_finish}")
        
        elif job.status == 'failed':
            print(f"\n❌ Job failed!")
            if job.error:
                print(f"Error: {job.error}")
        
        # Show training metrics if available
        if hasattr(job, 'result_files') and job.result_files:
            print(f"\nResult files available: {len(job.result_files)}")
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def list_all_jobs():
    """List all fine-tuning jobs"""
    try:
        jobs = client.fine_tuning.jobs.list(limit=10)
        
        print(f"\n{'='*60}")
        print(f"RECENT FINE-TUNING JOBS")
        print(f"{'='*60}")
        
        for job in jobs.data:
            status_emoji = {
                'succeeded': '✅',
                'failed': '❌',
                'running': '⏳',
                'cancelled': '⚠️'
            }.get(job.status, '❓')
            
            print(f"\n{status_emoji} {job.id}")
            print(f"   Status: {job.status}")
            print(f"   Model: {job.model}")
            if job.fine_tuned_model:
                print(f"   Result: {job.fine_tuned_model}")
        
        print(f"\n{'='*60}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
        check_status(job_id)
    else:
        print("No job ID provided. Showing all recent jobs:")
        list_all_jobs()
        print("\nUsage: python check_finetune_status.py [job_id]")
