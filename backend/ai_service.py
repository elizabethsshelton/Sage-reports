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
                self.model = 'gpt-4o-mini'  # Using cost-effective model
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
    
    def organize_notes(
        self,
        notes: str,
        topics_covered: str = '',
        activities: str = ''
    ) -> str:
        """
        Organize session notes to optimize report flow and structure.
        Maintains the tutor's intended chronological/flow order but cleans up duplicates
        and moves misplaced items to their proper place in the sequence.
        """
        if not notes or not notes.strip():
            return notes
        
        # Combine all input for context
        combined_input = f"""Topics Covered: {topics_covered}\n\nActivities: {activities}\n\nNotes: {notes}"""
        
        system_prompt = """You are helping a tutor organize their session notes to optimize the flow and structure of the final report. The tutor usually writes notes in the general order they want the report to flow (chronologically or by sequence of events). Your job is to:

1. **Maintain the tutor's intended flow** - Keep the general order and sequence they wrote, as this reflects how they want the report to read
2. **Remove duplicates** - If the same point appears multiple times, keep it only once in the most appropriate place
3. **Move misplaced items** - If something mentioned later should have been mentioned earlier (based on chronology or logical flow), move it to the right place in the sequence
4. **Merge related fragments** - If the same topic is mentioned in multiple places, combine those fragments into one coherent point at the appropriate location
5. **Preserve all information** - Don't lose any details, just clean up the flow
6. **Maintain chronological order** - Ensure the sequence makes sense chronologically and flows smoothly
7. **Keep the tutor's wording** - Preserve their exact phrasing and voice, just optimize the order

The goal is to create notes that will result in a smooth, well-flowing report narrative - not to categorize content, but to ensure the report reads naturally from start to finish. Output the cleaned-up notes in the optimized order. Do NOT write a report - just reorganize the notes for better report flow."""
        
        user_prompt = f"""Please optimize these session notes for smooth report flow. Maintain the tutor's intended order but clean up duplicates and move any misplaced items to their proper place in the sequence:\n\n{combined_input}"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent organization
                    max_tokens=2000
                )
                organized = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                organized = response.content[0].text.strip()
            else:
                return notes  # Fallback to original if no provider
            
            return organized
        
        except Exception as e:
            print(f"Error organizing notes: {e}")
            # If organization fails, return original notes
            return notes
    
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
                    temperature=0.8,  # Slightly higher for more natural variation
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
        return """You are a tutor writing to a parent after a session. This isn't a formal report - it's a personal message, like you're texting or emailing a friend about their child. Write with a casual, conversational, caring tone.

You genuinely care about this student. You're not just going through the motions - you're invested in their success, you notice their progress, and you want the parent to know how they're doing. Your writing shows that you care about this kid as a person, not just as a student. You celebrate their wins, you acknowledge when they're trying hard, and you believe in them.

When you write, you sound like a real person talking to a friend. You use simple, everyday words - you say "worked on" not "delved into," "practiced" not "engaged with," "went over" not "explored." You write exactly the way you'd talk if you were telling the parent what happened in person - casual, warm, and genuine.

You write in flowing paragraphs, like you're having a conversation. No bullet points, no section headers, no formal structure. You just tell the parent what happened, how the student did, and what you noticed - naturally, the way it actually happened. It should feel like you're catching up with them, not filling out paperwork.

The example reports you'll see show you exactly how this tutor writes. Study them carefully - notice how casual and conversational they are, how caring and warm the tone is, the simple words they use, how they start, how they describe things, how they talk about the student, how they end. Write exactly like that. Match their casual voice, their caring style, their way of expressing genuine interest in the student.

One important detail: In the opening and closing sentences, use only the student's first name, not their full name.

Write as if you ARE this tutor, writing to the parent after today's session. Let the writing flow naturally from what actually happened. Don't sound formal or professional - sound casual, conversational, and genuinely caring, like you're telling a friend about their child."""
    
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
        
        # Extract first name from student_name for use in opening/closing
        student_first_name = student_name.split()[0] if student_name else student_name
        
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
                # Organize notes before using them
                organized_notes = self.organize_notes(notes, topics_covered, activities)
                context += f"\nAdditional Notes:\n{organized_notes}\n"
            
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
            # Organize notes before using them
            organized_notes = self.organize_notes(notes, topics_covered, activities)
            context += f"- Additional Notes: {organized_notes}\n"
            # If notes have substantial structure (multiple bullets/sentences), prioritize them
            if organized_notes.count('•') >= 3 or organized_notes.count('\n') >= 2:
                context += "\n**IMPORTANT:** The user has provided detailed notes with structure. Use their wording and organization as the primary content, expanding naturally while maintaining their voice.\n"
        
        # Add sample reports for style reference
        if sample_reports and len(sample_reports) > 0:
            context += f"\n**Here are {len(sample_reports)} example reports written by this tutor. Study them carefully - this is exactly how you write:**\n\n"
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
            context += f"\n**Context from recent sessions with {student_first_name}:**\n"
            for report in previous_reports[:2]:  # Use last 2 reports
                date = report.get('session_date', 'N/A')
                topics = report.get('topics_covered', 'N/A')
                context += f"- {date}: {topics}\n"
        
        context += f"\n**Now write the report for today's session.**\n\n"
        context += f"Write it exactly like the tutor in those examples would write it - casual, conversational, and genuinely caring. Use only {student_first_name}'s first name in the opening and closing sentences. Write like you're talking to a friend about their child - warm, natural, and showing that you really care about {student_first_name}. Stop after your closing sentence - no sign-off (the system adds that automatically)."
        
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
    
    def suggest_sentences(self, report_text: str, student_name: str, subject: str, cursor_position: int = None, previous_reports: List[str] = None) -> List[str]:
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
                    context_before = para[:pos_in_para]
                    context_after = para[pos_in_para:]
                    print(f"Found cursor in paragraph (pos {cursor_position}):")
                    print(f"  Before cursor: ...{context_before[-80:]}")
                    print(f"  After cursor: {context_after[:80]}...")
                    break
                
                char_count = para_end
            
            # DETECT MID-SENTENCE: Check if cursor is in the middle of a sentence
            # Look at text before cursor - if it doesn't end with . ! ? or is at start of sentence, we're mid-sentence
            text_before = context_before.rstrip()
            is_mid_sentence = False
            partial_sentence = ""
            
            if text_before:
                # Check last 100 chars for sentence boundary
                last_segment = text_before[-100:] if len(text_before) > 100 else text_before
                
                # Find last sentence-ending punctuation (no whitespace required)
                import re
                last_period_match = None
                for match in re.finditer(r'[.!?]', last_segment):
                    last_period_match = match
                
                if last_period_match:
                    # There's a sentence boundary - get text after it
                    partial_sentence = last_segment[last_period_match.end():].strip()
                    if partial_sentence:  # If there's text after the period, we're mid-sentence
                        is_mid_sentence = True
                    # else: cursor is at end of sentence or only whitespace after - NOT mid-sentence
                elif last_segment.strip():  # No period found and there's text = we're mid-sentence
                    is_mid_sentence = True
                    partial_sentence = last_segment.strip()
            
            print(f"Mid-sentence detection: {is_mid_sentence}")
            if is_mid_sentence:
                print(f"  Partial sentence: '{partial_sentence}'")
            
            if is_mid_sentence and partial_sentence:
                # Generate COMPLETIONS for the partial sentence
                prompt = f"""You are helping a tutor finish a sentence in a session report for {student_name} ({subject}). 

**CRITICAL:** This tutor writes in a very human, conversational way - like they're talking to a friend about their child. It's warm, genuine, and caring. It does NOT sound formal, professional, or corporate. It sounds like a real person.

**Current full report context:**
{report_text[:600]}...

**The tutor started typing this sentence:**
"{partial_sentence}"

**Task:** Generate 4 DIFFERENT ways to COMPLETE this sentence (not new sentences, but endings for the sentence they started).

Generate 4 sentence completions that:
- Continue naturally from the partial sentence above
- Sound VERY human and conversational - use simple, everyday words
- Show genuine care for the student
- Each completion should finish the thought in a different way
- Start directly with the continuation (no repeating the partial sentence)
- Sound like a real person talking, not a formal report

Example:
If partial sentence is "She really struggled with"
Good completions: ["the fraction problems.", "understanding the concept at first.", "the word problems, so we slowed down.", "the homework but got it by the end."]

Generate 4 completions for: "{partial_sentence}" """
            else:
                # Generate full standalone sentences
                prompt = f"""You are helping a tutor write a session report for {student_name} ({subject}). 

**CRITICAL:** This tutor writes in a very human, conversational way - like they're talking to a friend about their child. It's warm, genuine, and caring. It does NOT sound formal, professional, or corporate. It sounds like a real person.

**Current full report context:**
{report_text[:600]}...

**The paragraph being edited:**
"{cursor_paragraph}"

**Cursor position:**
"{context_before.strip()} [CURSOR] {context_after.strip()}"

Generate 4 sentences that would fit naturally RIGHT AT THE CURSOR position. Write them with a VERY human, conversational tone - like a real person talking. Use simple everyday words. Show genuine care for the student. Sound natural and genuine, not formal or polished."""
        else:
            prompt = f"""You are helping a tutor write a session report for {student_name} ({subject}). 

**CRITICAL:** This tutor writes in a very human, conversational way - like they're talking to a friend about their child. It's warm, genuine, and caring. It does NOT sound formal, professional, or corporate. It sounds like a real person.

**Current draft:**
{report_text[:500]}...

Generate 4 sentences that could fit naturally in this report. Write them with a VERY human, conversational tone - like a real person talking. Use simple everyday words. Show genuine care for the student. Sound natural and genuine, not formal or polished."""
        
        # Add style examples if previous reports available
        style_context = ""
        if previous_reports and len(previous_reports) > 0:
            style_context = "\n\n**CRITICAL: Here are example reports from this tutor - study them VERY carefully. This tutor writes in a very human, conversational way. It sounds like a real person talking to a friend, not a formal report. Notice their exact words, sentence structure, and tone. Match it exactly.**\n"
            for i, report in enumerate(previous_reports[:8], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                style_context += f"\n--- Example {i} ---\n{clean_report[:600]}...\n"
            style_context += "\n**Write exactly like the tutor in these examples - conversational, human, warm, genuine, caring. Use their exact style and voice.**\n"
        
        prompt += style_context
        
        if is_mid_sentence and partial_sentence:
            # Instructions for sentence COMPLETIONS
            prompt += """

**CRITICAL:** Generate 4 sentence COMPLETIONS (not full sentences).

**Format:** Return ONLY a JSON array of 4 completion phrases:
["completion 1", "completion 2", "completion 3", "completion 4"]

Each completion should:
- Start directly with the words that complete the sentence (no repeating the start)
- End with proper punctuation (. ! or ?)
- Be 5-15 words typically
- Match the tutor's natural voice
- Provide variety in how the thought is finished

Example response format:
["the homework problems.", "understanding the new concept at first.", "the tricky parts, but we worked through it together.", "staying focused today."]"""
        else:
            # Instructions for full standalone sentences
            prompt += """

**CRITICAL:** Generate 4 SEPARATE, INDIVIDUAL sentences (not a paragraph).

Write exactly like the tutor in those examples - VERY human, conversational, and genuinely caring. Sound like a real person talking to a friend, not writing a formal report. Use simple, everyday words - the kind you'd use in conversation. Show you care about the student. Each sentence should be COMPLETE and INDEPENDENT (can stand alone). Keep each sentence SHORT - aim for 10-20 words each. Use regular hyphens (-) NOT em dashes (—). Sound natural and genuine, not polished or professional.

**Format requirements:**
- Each item in the array must be ONE sentence only (ending with . ! or ?)
- NO multi-sentence paragraphs
- Each sentence should be insertable on its own

**Good examples:**
["She asked great questions throughout.", "I'm confident this will click with more practice.", "We took extra time on the tricky concepts.", "She's making steady progress each week."]

**Bad examples (DON'T DO THIS):**
["She asked great questions throughout. I'm confident this will click with more practice."]  ← Two sentences in one item!

Return ONLY a JSON array of 4 INDIVIDUAL sentences:
["sentence 1", "sentence 2", "sentence 3", "sentence 4"]"""

        try:
            if self.provider == 'openai':
                # Use gpt-4o-mini for reliable JSON generation
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,  # Lower for better style matching
                    max_tokens=400
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=400,
                    temperature=0.7,
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
                validated_sentences = []
                for s in sentences:
                    s_str = str(s).strip()
                    # Check if this suggestion contains multiple sentences
                    # Split on sentence boundaries and only take the first one
                    import re
                    parts = re.split(r'(?<=[.!?])\s+', s_str)
                    if parts:
                        # Only take the first sentence from each suggestion
                        first_sentence = parts[0].strip()
                        if first_sentence:
                            validated_sentences.append(first_sentence)
                
                print(f"Validated single sentences: {validated_sentences}")
                return validated_sentences[:4]  # Ensure max 4
            else:
                print(f"Invalid suggestions format: {type(sentences)}")
                return []
        
        except Exception as e:
            print(f"Error generating sentence suggestions: {type(e).__name__}: {e}")
            print(f"Raw result that caused error: '{result}'")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_sentence_for_ai(self, text: str, sentence_type: str) -> str:
        """Extract opening or closing sentence properly handling ., !, and ?"""
        import re
        if not text:
            return ""
        
        text = text.strip()
        
        # Remove greeting lines like "Hi Name," at the start
        if sentence_type == 'opening':
            lines = text.split('\n')
            # Skip greeting line if it starts with "Hi"
            if lines and lines[0].strip().startswith('Hi '):
                text = '\n'.join(lines[1:]).strip()
        
        # Remove signature at the end (Best, Name)
        if sentence_type == 'closing':
            text = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', text).strip()
        
        # Split on sentence boundaries (., !, ?)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:100] if len(text) > 100 else text
        
        if sentence_type == 'opening':
            # For opening, get ONLY the first sentence
            return sentences[0]
        else:  # closing
            # For closing, get ONLY the last sentence
            return sentences[-1]
    
    def suggest_opening_closing(self, student_name: str, previous_reports: List[str], sentence_type: str, current_report_text: str = "") -> List[str]:
        """Generate opening or closing sentence suggestions based on previous reports"""
        
        if not self.client:
            return []
        
        # Extract first name from student_name for use in opening/closing
        student_first_name = student_name.split()[0] if student_name else student_name
        
        # Extract opening/closing sentences from previous reports for examples
        examples = []
        for report in previous_reports[:8]:  # Use up to 8 most recent
            sentence = self._extract_sentence_for_ai(report, sentence_type)
            if sentence:
                examples.append(sentence)
        
        examples_text = "\n".join([f"- {ex}" for ex in examples]) if examples else "No previous examples"
        
        # Get context from current report for better matching
        current_context = ""
        if current_report_text:
            # For openings, show what comes after; for closings, show what comes before
            if sentence_type == 'opening':
                # Show first paragraph for context
                paragraphs = current_report_text.split('\n\n')
                if len(paragraphs) > 1:
                    current_context = f"\n\n**Context from current report (what comes after the opening):**\n{paragraphs[1][:300]}..."
            else:  # closing
                # Show last paragraph before the closing
                paragraphs = current_report_text.split('\n\n')
                if len(paragraphs) > 1:
                    current_context = f"\n\n**Context from current report (what comes before the closing):**\n{paragraphs[-2][:300] if len(paragraphs[-2]) > 0 else paragraphs[-3][:300]}..."
        
        # Show full example reports for style matching (more examples for better training)
        style_examples = ""
        if previous_reports:
            style_examples = "\n\n**CRITICAL: FULL EXAMPLE REPORTS - Study these VERY carefully. Notice how this tutor writes - it's conversational, human, warm, and genuine. Match their exact voice and style:**\n"
            for i, report in enumerate(previous_reports[:8], 1):
                # Remove signatures for cleaner examples
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                style_examples += f"\n--- Report {i} ---\n{clean_report[:800]}...\n"
            style_examples += "\n**Write exactly like the tutor in these examples - conversational, human, warm, genuine, caring. Use their exact style and voice.**\n"
        
        if sentence_type == 'opening':
            prompt = f"""You are helping a tutor write varied opening sentences for session reports about {student_name}. 

**CRITICAL:** This tutor writes in a very human, conversational way - like they're talking to a friend about their child. It's warm, genuine, and caring. It does NOT sound formal, professional, or corporate. It sounds like a real person.

**IMPORTANT:** Use ONLY the student's FIRST NAME ({student_first_name}) in the opening sentences, NOT the full name ({student_name}).

Write exactly like the tutor in those examples - VERY human, conversational, and genuinely caring. Sound like a real person talking to a friend. Use simple, everyday words - the kind you'd use in conversation. Show you care about {student_first_name}.

**Opening sentences from past reports:**
{examples_text}
{style_examples}
{current_context}

**CRITICAL:** Each suggestion must be ONE sentence only (not multiple sentences).

Generate 5 DIFFERENT opening sentences that sound exactly like this tutor wrote them - casual, natural, warm, and caring. Each must be ONE COMPLETE sentence (ending with . ! or ?). Use regular hyphens (-) NOT em dashes (—).

**Format:** Each array item must be ONE sentence only.
Good: ["Great to see {student_first_name} today!", "It was wonderful working with {student_first_name} this week."]
Bad: ["Great to see {student_first_name} today! We had a productive session."] ← Two sentences!

Return ONLY a JSON array of 5 SINGLE opening sentences:
["sentence 1", "sentence 2", "sentence 3", "sentence 4", "sentence 5"]"""
        else:  # closing
            prompt = f"""You are helping a tutor write varied closing sentences for session reports about {student_name}. 

**CRITICAL:** This tutor writes in a very human, conversational way - like they're talking to a friend about their child. It's warm, genuine, and caring. It does NOT sound formal, professional, or corporate. It sounds like a real person.

**IMPORTANT:** Use ONLY the student's FIRST NAME ({student_first_name}) in the closing sentences, NOT the full name ({student_name}).

Write exactly like the tutor in those examples - VERY human, conversational, and genuinely caring. Sound like a real person talking to a friend. Use simple, everyday words - the kind you'd use in conversation. Show you care about {student_first_name}.

**Closing sentences from past reports:**
{examples_text}
{style_examples}
{current_context}

**CRITICAL:** Each suggestion must be ONE sentence only (not multiple sentences).

Generate 5 DIFFERENT closing sentences that sound exactly like this tutor wrote them - casual, natural, positive, and forward-looking without being overly enthusiastic. Flow naturally from what comes before in the report. Each must be ONE COMPLETE sentence (ending with . ! or ?). Use regular hyphens (-) NOT em dashes (—).

**Format:** Each array item must be ONE sentence only.
Good: ["Looking forward to next week!", "Can't wait to continue this work with {student_first_name}."]
Bad: ["Looking forward to next week! Keep up the great work."] ← Two sentences!

Return ONLY a JSON array of 5 SINGLE closing sentences:
["sentence 1", "sentence 2", "sentence 3", "sentence 4", "sentence 5"]"""

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,  # Lower temp for better style matching
                    max_tokens=500
                )
                result = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            
            else:
                return []
            
            # Parse JSON response
            import json
            # Clean up the response
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.startswith('```'):
                result = result[3:]
            if result.endswith('```'):
                result = result[:-3]
            result = result.strip()
            
            sentences = json.loads(result)
            
            # Validate and return - ensure each is a single sentence
            if isinstance(sentences, list) and len(sentences) > 0:
                validated = []
                for s in sentences:
                    s_str = str(s).replace('{student_name}', student_name).replace('[name]', student_name).strip()
                    # Check if this contains multiple sentences - if so, only take the first
                    import re
                    parts = re.split(r'(?<=[.!?])\s+', s_str)
                    if parts:
                        first_sentence = parts[0].strip()
                        if first_sentence:
                            validated.append(first_sentence)
                return validated[:5]  # Max 5
            else:
                return []
        
        except Exception as e:
            print(f"Error generating opening/closing suggestions: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def redo_paragraph(
        self, 
        paragraph: str, 
        full_report: str, 
        student_name: str,
        previous_reports: List[str] = None
    ) -> str:
        """Completely rewrite a paragraph in the user's style while keeping the same content"""
        
        if not self.client:
            return paragraph
        
        # Build style context from previous reports
        style_context = ""
        if previous_reports and len(previous_reports) > 0:
            style_context = "\n\n**CRITICAL: WRITING STYLE REFERENCE - Study these examples VERY carefully. Notice how this tutor writes - it's conversational, human, warm, and genuine. Match their exact voice and style:**\n"
            for i, report in enumerate(previous_reports[:8], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                style_context += f"\n--- Example {i} ---\n{clean_report[:600]}...\n"
            style_context += "\n**Write exactly like the tutor in these examples - conversational, human, warm, genuine, caring. Use their exact style and voice.**\n"
        
        # Get context before and after the paragraph
        if paragraph in full_report:
            parts = full_report.split(paragraph)
            context_before = parts[0][-300:] if len(parts[0]) > 300 else parts[0]
            context_after = parts[1][:300] if len(parts) > 1 and len(parts[1]) > 300 else (parts[1] if len(parts) > 1 else "")
        else:
            context_before = ""
            context_after = ""
        
        prompt = f"""You are helping a tutor rewrite a paragraph from a session report about {student_name}. 

**CRITICAL:** This tutor writes in a very human, conversational way - like they're talking to a friend about their child. It's warm, genuine, and caring. It does NOT sound formal, professional, or corporate. It sounds like a real person.

**Your goal:** Completely REWRITE this paragraph in the tutor's style while keeping the same information and key points.

**The paragraph to rewrite:**
{paragraph}

**What comes BEFORE this paragraph:**
{context_before if context_before else "(Beginning of report)"}

**What comes AFTER this paragraph:**
{context_after if context_after else "(End of report)"}
{style_context}

Write it exactly like the tutor in those examples - VERY human, conversational, and genuinely caring. Sound like a real person talking to a friend, not writing a formal report. Use simple, everyday words - the kind you'd use in conversation. Show genuine care for the student. Keep ALL the same information and key points from the original, but use completely DIFFERENT wording and sentence structure. Make it flow naturally with what comes before and after. Use regular hyphens (-) NOT em dashes (—). Sound natural and genuine, not polished or professional.

Return ONLY the rewritten paragraph, nothing else."""

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,  # Higher for more creative rewrites
                    max_tokens=600
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=600,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            print(f"Error redoing paragraph: {e}")
            return paragraph
    
    def polish_text(self, text_to_polish: str, full_context: str = "", previous_reports: List[str] = None) -> str:
        """Improve a selected portion of text while keeping the same meaning"""
        
        if not self.client:
            return text_to_polish
        
        prompt = f"""You are helping polish a portion of a tutoring report. This tutor writes with a casual, conversational, caring tone - like they're talking to a friend about their child.

This is CRITICAL: The tutor's writing is very human and conversational. It sounds like a real person talking, not a formal report. It's warm, genuine, and caring. You must match this exact tone.

Make it sound better - clearer, more natural, more genuine, MORE HUMAN. Keep the SAME meaning and main ideas. Keep the casual, conversational, caring tone. Use simple, everyday words - the kind of words you'd use when talking to a friend. Fix any grammar or awkward phrasing, but don't make it more formal or wordy. Don't make it sound professional or polished in a corporate way - make it sound like a real person who genuinely cares.

Text to polish: {text_to_polish}
"""
        
        # Add style examples from previous reports
        if previous_reports and len(previous_reports) > 0:
            prompt += "\n\n**CRITICAL: Here are example reports from this tutor - study them carefully. Match their exact voice, tone, and way of expressing things:**\n"
            for i, report in enumerate(previous_reports[:5], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                prompt += f"\n--- Example {i} ---\n{clean_report[:600]}...\n"
            prompt += "\n**Notice how this tutor writes - it's conversational, human, warm, and genuine. Write exactly like that. Match their voice.**\n"
        
        if full_context:
            prompt += f"\nFull report context:\n{full_context[:500]}...\n\n"
        
        prompt += "Return ONLY the polished version WITHOUT any quotation marks around it. Just the text itself, nothing else. Make it sound more human and conversational, not more formal."

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
    
    def suggest_synonyms(self, word: str, context: str = "", previous_reports: List[str] = None) -> List[str]:
        """Suggest conversational synonyms for a word that match the tutor's style"""
        
        if not self.client or not word:
            return []
        
        # Clean the word - remove punctuation, lowercase
        import re
        clean_word = re.sub(r'[^\w\s]', '', word).lower().strip()
        
        if not clean_word or len(clean_word) < 2:
            return []
        
        prompt = f"""You are helping a tutor find a better word in a session report. This tutor writes in a very human, conversational way - like they're talking to a friend about their child.

**CRITICAL:** The tutor uses simple, everyday words. They do NOT use formal, academic, or corporate language. They sound like a real person talking.

**Word to find synonyms for:** "{clean_word}"

**Context (surrounding text):**
{context[:300] if context else "(No context provided)"}
"""
        
        # Add style examples from previous reports
        if previous_reports and len(previous_reports) > 0:
            prompt += "\n\n**Here are example reports from this tutor - notice the simple, conversational words they use:**\n"
            for i, report in enumerate(previous_reports[:5], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                prompt += f"\n--- Example {i} ---\n{clean_report[:400]}...\n"
            prompt += "\n**Suggest synonyms that match this tutor's conversational, human style - simple, everyday words.**\n"
        
        prompt += f"""

**Task:** Generate 5-8 simple, conversational synonyms for "{clean_word}" that:
- Are simple, everyday words (not formal or academic)
- Sound natural and human (like a real person talking)
- Fit the conversational tone of this tutor
- Would work well in the context provided
- Are appropriate for a tutoring report to a parent

**IMPORTANT:** 
- Prefer simple, common words over fancy or formal ones
- Think about how a real person would say this when talking to a friend
- Avoid words that sound too professional, academic, or corporate
- Make sure the synonyms actually work in the context

**Format:** Return ONLY a JSON array of synonyms:
["synonym1", "synonym2", "synonym3", "synonym4", "synonym5"]

Example for "struggled":
["had trouble with", "found it hard to", "had difficulty with", "was having a tough time with", "was finding challenging"]

Example for "excellent":
["great", "really good", "awesome", "fantastic", "wonderful"]

Return ONLY the JSON array, nothing else."""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=200
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            else:
                return []
            
            # Parse JSON response
            import json
            result = result.strip()
            
            if result.startswith('```'):
                result = re.sub(r'```(?:json)?\s*|\s*```', '', result).strip()
            
            synonyms = json.loads(result)
            
            # Validate it's a list of strings
            if isinstance(synonyms, list) and len(synonyms) > 0:
                # Filter out the original word and return unique synonyms
                filtered = [s for s in synonyms if s.lower() != clean_word]
                return list(dict.fromkeys(filtered))[:8]  # Remove duplicates, max 8
            else:
                return []
        
        except Exception as e:
            print(f"Error generating synonyms: {type(e).__name__}: {e}")
            return []
    
    def review_report_phrases(self, report_text: str, previous_reports: List[str] = None) -> List[dict]:
        """Review entire report and find phrases that need improvement with specific suggestions"""
        
        if not self.client or not report_text:
            return []
        
        prompt = f"""You are reviewing a tutoring session report that will be sent to a parent. This tutor writes in a very human, conversational way - like they're talking to a friend about their child.

**CRITICAL:** The tutor uses simple, everyday words. They do NOT use formal, academic, or corporate language. They sound like a real person talking.

**Your task:** Review the ENTIRE report and identify specific phrases, sentences, or words that have problems. For each problem, provide:
1. The exact text that needs changing (with surrounding context)
2. What's wrong with it (wordiness, too formal, too informal, doesn't make sense, inappropriate for parent, etc.)
3. 2-3 better alternatives that match the tutor's conversational, human style

**Types of problems to look for:**
- Too formal/wordy: "delved into", "engaged with", "explored", "utilized" → should be "worked on", "practiced", "used"
- Too informal/inappropriate: slang, overly casual language that's not appropriate for a parent
- Doesn't make sense: confusing phrasing, unclear meaning
- Wordiness: unnecessarily long phrases that could be simpler
- Tone mismatch: anything that doesn't sound like a real person talking to a friend
- Inappropriate for parent: anything that might confuse or concern a parent

**The report to review:**
{report_text}
"""
        
        # Add style examples from previous reports
        if previous_reports and len(previous_reports) > 0:
            prompt += "\n\n**Here are example reports from this tutor - notice their simple, conversational style:**\n"
            for i, report in enumerate(previous_reports[:5], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                prompt += f"\n--- Example {i} ---\n{clean_report[:600]}...\n"
            prompt += "\n**Match this tutor's conversational, human style when suggesting improvements.**\n"
        
        prompt += """

**CRITICAL INSTRUCTIONS:**
1. Find ALL problems in the report - be thorough
2. For each problem, identify the EXACT text that needs changing (quote it exactly)
3. Explain what's wrong (one sentence)
4. Provide 2-3 better alternatives that are simple, conversational, and human
5. Only flag things that genuinely need improvement - don't be overly picky

**Format:** Return a JSON array. Each item should have:
- "original": the exact text that needs changing (include enough context to find it uniquely)
- "issue": what's wrong (e.g., "too formal", "wordy", "doesn't make sense", "too informal")
- "suggestions": array of 2-3 better alternatives
- "start_index": character position where the problem text starts (approximate is fine)
- "end_index": character position where it ends

**Example response:**
[
  {
    "original": "We delved into the mathematical concepts",
    "issue": "too formal - 'delved into' sounds academic",
    "suggestions": ["worked on", "went over", "practiced"],
    "start_index": 45,
    "end_index": 78
  },
  {
    "original": "The student was struggling big time",
    "issue": "too informal - 'big time' is too casual for a parent",
    "suggestions": ["was really struggling", "was having a hard time", "was finding it difficult"],
    "start_index": 120,
    "end_index": 155
  }
]

Return ONLY the JSON array, nothing else. If there are no problems, return an empty array [].

**Important:** Be thorough but fair. Only flag genuine issues. Match the tutor's conversational style in your suggestions."""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,  # Lower temp for more consistent analysis
                    max_tokens=2000
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.5,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            else:
                return []
            
            # Parse JSON response
            import json
            import re
            
            result = result.strip()
            
            if result.startswith('```'):
                result = re.sub(r'```(?:json)?\s*|\s*```', '', result).strip()
            
            # Try to extract JSON if wrapped in text
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                result = json_match.group(0)
            
            suggestions = json.loads(result)
            
            # Validate and refine suggestions
            if isinstance(suggestions, list):
                validated = []
                used_positions = []  # Track used positions to avoid duplicates
                
                for sug in suggestions:
                    if isinstance(sug, dict) and 'original' in sug and 'suggestions' in sug:
                        # Try to find the exact position in the text
                        original_text = sug.get('original', '').strip()
                        if original_text:
                            # First, try to use provided indices if they seem valid
                            provided_start = sug.get('start_index')
                            provided_end = sug.get('end_index')
                            
                            if (provided_start is not None and provided_end is not None and 
                                provided_start >= 0 and provided_end > provided_start and 
                                provided_end <= len(report_text)):
                                # Verify the text at these indices matches
                                text_at_indices = report_text[provided_start:provided_end].strip()
                                # Allow some flexibility - check if the original text is contained in the text at indices
                                if original_text.lower() in text_at_indices.lower() or text_at_indices.lower() in original_text.lower():
                                    # Check if this position overlaps with already used positions
                                    overlaps = False
                                    for used_start, used_end in used_positions:
                                        if not (provided_end <= used_start or provided_start >= used_end):
                                            overlaps = True
                                            break
                                    
                                    if not overlaps:
                                        sug['start_index'] = provided_start
                                        sug['end_index'] = provided_end
                                        used_positions.append((provided_start, provided_end))
                                    else:
                                        # Position overlaps, try to find a different occurrence
                                        import re
                                        pattern = re.escape(original_text)
                                        matches = list(re.finditer(pattern, report_text, re.IGNORECASE))
                                        found = False
                                        for match in matches:
                                            # Check if this match doesn't overlap with used positions
                                            overlaps = False
                                            for used_start, used_end in used_positions:
                                                if not (match.end() <= used_start or match.start() >= used_end):
                                                    overlaps = True
                                                    break
                                            if not overlaps:
                                                sug['start_index'] = match.start()
                                                sug['end_index'] = match.end()
                                                used_positions.append((match.start(), match.end()))
                                                found = True
                                                break
                                        if not found:
                                            continue
                                else:
                                    # Indices don't match, try to find the text
                                    import re
                                    pattern = re.escape(original_text)
                                    matches = list(re.finditer(pattern, report_text, re.IGNORECASE))
                                    found = False
                                    for match in matches:
                                        # Check if this match doesn't overlap with used positions
                                        overlaps = False
                                        for used_start, used_end in used_positions:
                                            if not (match.end() <= used_start or match.start() >= used_end):
                                                overlaps = True
                                                break
                                        if not overlaps:
                                            sug['start_index'] = match.start()
                                            sug['end_index'] = match.end()
                                            used_positions.append((match.start(), match.end()))
                                            found = True
                                            break
                                    if not found:
                                        continue
                            else:
                                # No valid provided indices, search for the text
                                import re
                                pattern = re.escape(original_text)
                                matches = list(re.finditer(pattern, report_text, re.IGNORECASE))
                                found = False
                                for match in matches:
                                    # Check if this match doesn't overlap with used positions
                                    overlaps = False
                                    for used_start, used_end in used_positions:
                                        if not (match.end() <= used_start or match.start() >= used_end):
                                            overlaps = True
                                            break
                                    if not overlaps:
                                        sug['start_index'] = match.start()
                                        sug['end_index'] = match.end()
                                        used_positions.append((match.start(), match.end()))
                                        found = True
                                        break
                                if not found:
                                    continue
                        elif 'start_index' in sug and 'end_index' in sug:
                            # No original text but has indices - validate them
                            if (sug['start_index'] >= 0 and sug['end_index'] > sug['start_index'] and 
                                sug['end_index'] <= len(report_text)):
                                # Check for overlaps
                                overlaps = False
                                for used_start, used_end in used_positions:
                                    if not (sug['end_index'] <= used_start or sug['start_index'] >= used_end):
                                        overlaps = True
                                        break
                                if overlaps:
                                    continue
                                used_positions.append((sug['start_index'], sug['end_index']))
                            else:
                                continue
                        else:
                            # No text and no indices - skip
                            continue
                        
                        validated.append({
                            'original': sug.get('original', ''),
                            'issue': sug.get('issue', 'needs improvement'),
                            'suggestions': sug.get('suggestions', []),
                            'start_index': sug.get('start_index', 0),
                            'end_index': sug.get('end_index', 0)
                        })
                
                # Sort by start_index to ensure proper ordering
                validated.sort(key=lambda x: (x['start_index'], x['end_index']))
                return validated
            
            return []
        
        except Exception as e:
            print(f"Error reviewing report: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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
