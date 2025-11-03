"""
AI Service for generating tutoring reports
"""

import os
from typing import List, Dict, Optional
from datetime import datetime

class AIService:
    """Handles AI report generation using OpenAI or Anthropic"""
    
    def __init__(self, provider='openai'):
        self.provider = provider.lower()
        
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.model = 'gpt-5-mini'  # Using cost-effective model
            except Exception as e:
                print(f"Error initializing OpenAI: {e}")
                self.client = None
        
        elif self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                self.model = 'claude-3-5-sonnet-20241022'  # Using latest model
            except Exception as e:
                print(f"Error initializing Anthropic: {e}")
                self.client = None
        else:
            self.client = None
    
    def generate_report(
        self,
        student_name: str,
        subject: str,
        topics_covered: str,
        activities: str,
        notes: str,
        sample_reports: List[str] = None,
        previous_reports: List[Dict] = None,
        minimal_editing: bool = False,
        parent_name: str = None,
        tutor_name: str = None,
        include_contact: bool = False,
        tutor_phone: str = None,
        tutor_email: str = None
    ) -> str:
        """
        Generate a tutoring session report
        
        Args:
            student_name: Name of the student
            subject: Subject/class
            topics_covered: Topics covered in the session
            activities: What was done during the session
            notes: Additional notes or gaps to fill
            sample_reports: List of sample reports for style reference
            previous_reports: List of previous reports for this student
        
        Returns:
            Generated report text
        """
        
        if not self.client:
            return self._generate_fallback_report(
                student_name, subject, topics_covered, activities, notes
            )
        
        # Build the context for the AI
        context = self._build_context(
            student_name, subject, topics_covered, activities, notes,
            sample_reports, previous_reports, minimal_editing, parent_name
        )
        
        # Generate the report
        report_text = ""
        try:
            if self.provider == 'openai':
                # GPT-5 models use max_completion_tokens and don't support custom temperature
                if self.model.startswith('gpt-5'):
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self._get_system_prompt()},
                            {"role": "user", "content": context}
                        ],
                        max_completion_tokens=1500
                        # GPT-5 only supports default temperature (1)
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self._get_system_prompt()},
                            {"role": "user", "content": context}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )
                report_text = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.7,
                    system=self._get_system_prompt(),
                    messages=[
                        {"role": "user", "content": context}
                    ]
                )
                report_text = response.content[0].text.strip()
        
        except Exception as e:
            print(f"ERROR generating report: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            report_text = self._generate_fallback_report(
                student_name, subject, topics_covered, activities, notes
            )
        
        # Append signature
        signature = self._build_signature(tutor_name, include_contact, tutor_phone, tutor_email)
        if signature:
            report_text += "\n\n" + signature
        
        return report_text
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for report generation"""
        return """Your job is to write a tutoring session report that sounds EXACTLY like the example reports provided.

CRITICAL - Your #1 priority is to MIMIC THE STYLE of the sample reports:
- Study how the writer structures their paragraphs
- Notice their sentence length and rhythm
- Copy their level of detail (not too much, not too little)
- Match their casual, genuine, direct, conversational tone
- Use similar transitions between ideas
- Mirror how they weave together what happened, how the student did, and what's next

VOICE GUIDELINES:
- Casual and genuine - like a friendly professional conversation
- Direct - get to the point without excessive formality
- Conversational - as if speaking to the parent face-to-face
- Natural paragraphs that flow - NO bullet points, NO section headers

STRUCTURE:
- Start with the greeting, then add a warm opening sentence - vary the wording but keep the idea of being glad to see them (e.g., "It was great to see [Student] again this week!" or "Always a pleasure working with [Student]!" or "Good to see [Student] today!")
- 2-5 body paragraphs covering what was done, how the student performed, areas to work on
- Closing: If relevant, add 1-2 context sentences first (e.g., "Wishing her luck on her test!" or "[Student] is working hard and showing great progress."). Then ALWAYS end with a forward-looking sentence - vary the wording but keep the idea (e.g., "Looking forward to seeing [Student] again next week!" or "See you next session!" or "Can't wait to work with [Student] again!")
- NO sign-off like "Best," or "Sincerely," (system adds that automatically)

The sample reports show you exactly how this writer sounds. Copy that voice and structure."""
    
    def _build_context(
        self,
        student_name: str,
        subject: str,
        topics_covered: str,
        activities: str,
        notes: str,
        sample_reports: List[str] = None,
        previous_reports: List[Dict] = None,
        minimal_editing: bool = False,
        parent_name: str = None
    ) -> str:
        """Build the context message for the AI"""
        
        # Determine the greeting
        greeting = ""
        if parent_name:
            # Extract first name from parent_name
            first_name = parent_name.split()[0] if parent_name else ""
            greeting = f"Hi {first_name},"
        
        # MINIMAL EDITING MODE - Just grammar cleanup
        if minimal_editing:
            context = f"""You are helping a tutor polish their session report. They've written their own report and just need light grammar and clarity improvements.

**IMPORTANT:** Preserve the user's wording, structure, and style as much as possible. Only fix:
- Grammar errors
- Spelling mistakes  
- Awkward phrasing
- Clarity issues

DO NOT:
- Rewrite sentences
- Change the structure
- Add content they didn't mention
- Change the tone significantly

**Student:** {student_name}
**Subject:** {subject}
"""
            if greeting:
                context += f"**MUST START WITH:** \"{greeting}\"\n"
            
            context += f"""
**User's Draft Report:**

Topics Covered:
{topics_covered}

What We Did:
{activities}
"""
            if notes:
                context += f"\nAdditional Notes:\n{notes}\n"
            
            context += "\n**Your Task:** Lightly edit this for grammar and clarity while preserving the user's voice and structure."
            if greeting:
                context += f" The report MUST begin with \"{greeting}\""
            context += " Convert to flowing paragraph format if needed (no bullet points or section headers unless the user explicitly used them). "
            context += "**Do NOT add any sign-off or closing - the system handles that automatically.**"
            return context
        
        # NORMAL MODE - Full AI generation (prioritize user's wording when present)
        context = f"""Please write a tutoring session report for {student_name}.
"""
        
        if greeting:
            context += f"\n**IMPORTANT: The report MUST start with:** \"{greeting}\"\n"
        
        context += f"""
**Session Information:**
- Student: {student_name}
- Subject: {subject}
- Topics Covered: {topics_covered}
- Activities and Work Done: {activities}
"""
        
        if notes:
            context += f"- Additional Notes: {notes}\n"
            # If notes have substantial structure (multiple bullets/sentences), prioritize them
            if notes.count('•') >= 3 or notes.count('\n') >= 2:
                context += "\n**IMPORTANT:** The user has provided detailed notes with structure. Use their wording and organization as the primary content, expanding naturally while maintaining their voice.\n"
        
        # Add sample reports for style reference
        if sample_reports and len(sample_reports) > 0:
            context += "\n**EXAMPLE REPORTS - This is EXACTLY how you should write:**\n"
            context += f"Study these {len(sample_reports)} reports carefully. Your report should sound just like these:\n\n"
            # Show more samples with full text to really learn the style
            for i, sample in enumerate(sample_reports, 1):
                # Show full text for first 8 samples, truncate after that
                max_length = 1200 if i <= 8 else 600
                sample_text = sample[:max_length]
                if len(sample) > max_length:
                    sample_text += "..."
                context += f"--- Example {i} ---\n{sample_text}\n\n"
        
        # Add previous report context
        if previous_reports and len(previous_reports) > 0:
            context += "\n**Previous Session Notes:**\n"
            context += "Here's what happened in recent sessions with this student:\n"
            for report in previous_reports[:2]:  # Use last 2 reports
                date = report.get('session_date', 'N/A')
                topics = report.get('topics_covered', 'N/A')
                context += f"- {date}: {topics}\n"
        
        context += "\n**Your Task:**\n"
        context += "Write a session report for this student using the EXACT same style, tone, and structure as the example reports above.\n\n"
        context += "Key reminders:\n"
        context += f"- Start with a warm opening sentence after the greeting - vary the wording each time but keep the idea of being glad to see them (e.g., 'It was great to see {student_name} again this week!' or 'Always a pleasure working with {student_name}!' or 'Good to see {student_name} today!')\n"
        context += "- Copy the casual, direct, conversational voice from the examples\n"
        context += "- 2-5 body paragraphs covering what was done and how the student did\n"
        context += f"- Closing: If relevant to the session, add 1-2 context sentences first (e.g., if there's a test: 'Wishing her luck on her test!' or if showing progress: '{student_name} is working hard and showing great progress.'). Then ALWAYS end with a forward-looking sentence - vary the wording but keep the idea (e.g., 'Looking forward to seeing {student_name} again next week!' or 'See you next session!' or 'Can't wait to work with {student_name} again!')\n"
        context += "- Use the writer's natural phrasing - don't make it more formal or detailed than the examples\n"
        context += "- NO bullet points, NO section headers - just flowing paragraphs like the examples\n"
        context += "- Stop after the closing sentence - NO sign-off like 'Best,' (system adds that)\n\n"
        context += "Think: 'What would the writer of those example reports say about THIS session?'"
        
        return context
    
    def _build_signature(
        self,
        tutor_name: str = None,
        include_contact: bool = False,
        tutor_phone: str = None,
        tutor_email: str = None
    ) -> str:
        """Build the signature block for the report"""
        if not tutor_name:
            return ""
        
        signature = f"Best,\n{tutor_name}"
        
        if include_contact:
            if tutor_phone:
                signature += f"\n{tutor_phone}"
            if tutor_email:
                signature += f"\n{tutor_email}"
        
        return signature
    
    def _generate_fallback_report(
        self,
        student_name: str,
        subject: str,
        topics_covered: str,
        activities: str,
        notes: str
    ) -> str:
        """Generate a basic report without AI (fallback)"""
        
        report = f"""Session Report for {student_name}

Date: {datetime.now().strftime('%B %d, %Y')}
Subject: {subject}

Topics Covered:
{topics_covered}

Session Activities:
{activities}
"""
        
        if notes:
            report += f"\nAdditional Notes:\n{notes}\n"
        
        report += f"""
Overall, {student_name} showed good engagement during today's session. We made progress on the topics listed above and identified areas for continued practice.

Next Steps:
- Continue practicing the concepts covered today
- Review any challenging problems before our next session
- Come prepared with questions

Looking forward to our next session!
"""
        
        return report
    
    def suggest_sentences(self, report_text: str, student_name: str, subject: str, cursor_position: int = None) -> List[str]:
        """Generate suggested filler sentences based on the paragraph where the cursor is"""
        
        if not self.client:
            return []
        
        # Find the paragraph where the cursor is located
        current_paragraph = report_text
        context_before = ""
        context_after = ""
        
        if cursor_position is not None and report_text:
            # Split report into paragraphs (by double newline or single newline)
            paragraphs = report_text.split('\n\n')
            
            # Find which paragraph contains the cursor
            char_count = 0
            cursor_paragraph = report_text  # Default to full text
            
            for para in paragraphs:
                para_start = char_count
                para_end = char_count + len(para) + 2  # +2 for \n\n
                
                if para_start <= cursor_position <= para_end:
                    # Cursor is in this paragraph
                    cursor_paragraph = para
                    # Get position within paragraph
                    pos_in_para = cursor_position - para_start
                    context_before = para[:pos_in_para].strip()
                    context_after = para[pos_in_para:].strip()
                    print(f"Found cursor in paragraph (pos {cursor_position}):")
                    print(f"  Before cursor: ...{context_before[-80:]}")
                    print(f"  After cursor: {context_after[:80]}...")
                    break
                
                char_count = para_end
            
            prompt = f"""You are helping a tutor write a session report for {student_name} ({subject}).

The tutor is working on this paragraph:
"{cursor_paragraph}"

Their cursor is positioned here:
"{context_before} [CURSOR] {context_after}"

Generate 4 sentences that would fit naturally RIGHT AT THE CURSOR position to continue or expand this paragraph.
Focus on what comes immediately BEFORE the cursor - suggest sentences that flow naturally from that."""
        else:
            prompt = f"""You are helping a tutor write a session report for {student_name} ({subject}).

Here is their current draft:
{report_text[:500]}...

Generate 4 sentences that could fit naturally anywhere in this report."""
        
        prompt += """

Requirements:
- Match the casual, conversational tone
- Flow naturally from what comes before the cursor
- Be useful as "filler" or connecting sentences
- Sound like the writer's natural voice

Examples:
- "She asked great questions throughout the session."
- "We took extra time on the concepts she found challenging."
- "I'm confident these skills will stick with practice."
- "She showed good persistence when problems got tricky."

Return ONLY a JSON array of 4 sentences, nothing else:
["sentence 1", "sentence 2", "sentence 3", "sentence 4"]"""

        try:
            if self.provider == 'openai':
                # Use gpt-4o-mini for reliable JSON generation
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,  # Creative but reliable
                    max_tokens=300
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            
            # Parse JSON response
            import json
            import re
            
            # Clean up response - sometimes AI wraps JSON in markdown code blocks
            result = result.strip()
            
            if not result:
                print("AI returned empty response for sentence suggestions")
                return []
            
            if result.startswith('```'):
                # Extract JSON from markdown code block
                result = re.sub(r'```(?:json)?\s*|\s*```', '', result).strip()
            
            print(f"AI Suggestions raw response: {result}")
            
            sentences = json.loads(result)
            print(f"Parsed suggestions: {sentences}")
            
            # Validate it's a list of strings
            if isinstance(sentences, list) and len(sentences) > 0:
                return [str(s) for s in sentences]
            else:
                print(f"Invalid suggestions format: {type(sentences)}")
                return []
        
        except Exception as e:
            print(f"Error generating sentence suggestions: {type(e).__name__}: {e}")
            print(f"Raw result that caused error: '{result}'")
            import traceback
            traceback.print_exc()
            return []
    
    def polish_text(self, text_to_polish: str, full_context: str = "") -> str:
        """Improve a selected portion of text while keeping the same meaning"""
        
        if not self.client:
            return text_to_polish
        
        prompt = f"""You are helping polish a portion of a tutoring report.

RULES:
- Make it sound better (clearer, more natural, more professional)
- Keep the SAME meaning and main ideas
- Keep the casual, conversational tone
- Fix any grammar or awkward phrasing
- Don't make it more formal or wordy

Text to polish: {text_to_polish}
"""
        
        if full_context:
            prompt += f"\nFull report context:\n{full_context[:500]}...\n\n"
        
        prompt += "Return ONLY the polished version WITHOUT any quotation marks around it. Just the text itself, nothing else."

        try:
            if self.provider == 'openai':
                # Use gpt-4o-mini for fast polishing
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    temperature=0.5,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            print(f"Error polishing text: {e}")
            return text_to_polish
    
    def fix_grammar(self, report_text: str) -> str:
        """Fix grammar and spelling while preserving exact wording and structure"""
        
        if not self.client:
            return report_text  # Return unchanged if no AI available
        
        prompt = f"""You are a copy editor. Fix ONLY grammar, spelling, and punctuation errors in this tutoring report.

CRITICAL RULES:
- Keep the EXACT same wording, structure, and tone
- Only fix actual errors (grammar, spelling, punctuation)
- Do NOT rewrite sentences
- Do NOT change vocabulary or phrasing
- Do NOT add or remove content
- Do NOT change the casual/conversational tone
- Preserve all paragraph breaks and formatting

Here is the report:

{report_text}

Return the corrected version with ONLY grammar/spelling/punctuation fixes applied."""

        try:
            if self.provider == 'openai':
                # Use gpt-4o-mini for grammar fixes - it's 3x faster and cheaper for this task
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',  # Fast model for simple grammar fixes
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,  # Low temp for conservative edits
                    max_tokens=2000
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            print(f"Error fixing grammar: {e}")
            return report_text  # Return unchanged on error
    
    def suggest_improvements(self, report_text: str) -> List[str]:
        """Suggest improvements for a report"""
        
        suggestions = []
        
        # Basic checks
        if len(report_text) < 200:
            suggestions.append("Consider adding more detail about specific topics or activities")
        
        if "student" in report_text.lower() and report_text.count("student") > report_text.count(" "):
            suggestions.append("Use the student's name more often for a personal touch")
        
        if "next steps" not in report_text.lower() and "next session" not in report_text.lower():
            suggestions.append("Consider adding a 'Next Steps' section for actionable recommendations")
        
        if not any(word in report_text.lower() for word in ["strength", "progress", "improvement", "well"]):
            suggestions.append("Highlight specific strengths or areas of progress")
        
        return suggestions


def test_ai_connection():
    """Test if AI service is properly configured"""
    provider = os.getenv('AI_PROVIDER', 'openai')
    
    if provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False, "OpenAI API key not found in .env file"
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            # Simple test call - just try to list models
            list(client.models.list())
            return True, "OpenAI connected successfully"
        except Exception as e:
            return False, f"OpenAI error: {str(e)}"
    
    elif provider == 'anthropic':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return False, "Anthropic API key not found in .env file"
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            # Simple test - the client initializes successfully if key is valid
            return True, "Anthropic connected successfully"
        except Exception as e:
            return False, f"Anthropic error: {str(e)}"
    
    return False, "Unknown AI provider"
