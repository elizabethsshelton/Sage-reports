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
                
                # Use fine-tuned model if available, otherwise fall back to base
                self.finetuned_model = os.getenv('FINETUNED_MODEL_ID')
                if self.finetuned_model:
                    self.model = self.finetuned_model
                    print(f"✨ Using fine-tuned model: {self.finetuned_model}")
                else:
                    self.model = 'gpt-4o-mini'  # Base model fallback
                    print("Using base model: gpt-4o-mini")
            except Exception as e:
                print(f"Error initializing OpenAI: {e}")
                self.client = None
        
        elif self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                self.model = 'claude-sonnet-4-20250514'  # Using latest working model
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
        tutor_email: str = None,
        ai_instructions: str = ''
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
        
        # Add AI instructions if provided
        if ai_instructions:
            context += f"\n\n**ADDITIONAL INSTRUCTIONS FOR THIS REPORT:**\n{ai_instructions}\n\nIMPORTANT: Follow these additional instructions carefully."
        
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

PUNCTUATION RULES:
- Use regular hyphens (-) NOT em dashes (—)
- Keep punctuation simple and natural

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
        
        # Extract first name from student name (before any space)
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

**Student:** {student_first_name} (ALWAYS use ONLY the first name throughout the report)
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
                context += f"\n**TUTOR'S ADDITIONAL NOTES (USE ALL OF THIS):**\n{notes}\n"
                context += "\n🔴 Make sure ALL content from these notes is included in the final report.\n"
            
            context += "\n**Your Task:** Lightly edit this for grammar and clarity while preserving the user's voice and structure. Ensure ALL the content from the notes above is incorporated."
            if greeting:
                context += f" The report MUST begin with \"{greeting}\""
            context += " Convert to flowing paragraph format if needed (no bullet points or section headers unless the user explicitly used them). "
            context += "**Do NOT add any sign-off or closing - the system handles that automatically.**"
            return context
        
        # NORMAL MODE - Full AI generation (prioritize user's wording when present)
        context = f"""Please write a tutoring session report for {student_first_name}.

**CRITICAL: Always refer to the student as "{student_first_name}" (first name only) throughout the entire report. Never use their full name.**
"""
        
        if greeting:
            context += f"\n**IMPORTANT: The report MUST start with:** \"{greeting}\"\n"
        
        context += f"""
**Session Information:**
- Student: {student_first_name}
- Subject: {subject}
- Topics Covered: {topics_covered}
- Activities and Work Done: {activities}
"""
        
        if notes:
            context += f"\n**TUTOR'S NOTES (CRITICAL - USE ALL OF THIS CONTENT):**\n{notes}\n"
            context += "\n🔴 **CRITICAL INSTRUCTION:** The tutor has provided detailed notes above. You MUST include ALL the information from these notes in the report. Do not skip or summarize any points - every detail matters. Expand on these notes naturally in the report style, but ensure EVERY point is covered.\n"
        
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
        context += f"- 🔴 MOST IMPORTANT: Include ALL content from the tutor's notes - don't skip anything!\n"
        context += f"- ALWAYS use only the first name \"{student_first_name}\" - NEVER use the full name\n"
        context += f"- Start with a warm opening sentence after the greeting - vary the wording each time but keep the idea of being glad to see them (e.g., 'It was great to see {student_first_name} again this week!' or 'Always a pleasure working with {student_first_name}!' or 'Good to see {student_first_name} today!')\n"
        context += "- Copy the casual, direct, conversational voice from the examples\n"
        context += "- 2-5 body paragraphs covering what was done and how the student did (include EVERYTHING from the notes)\n"
        context += f"- Closing: If relevant to the session, add 1-2 context sentences first (e.g., if there's a test: 'Wishing her luck on her test!' or if showing progress: '{student_first_name} is working hard and showing great progress.'). Then ALWAYS end with a forward-looking sentence - vary the wording but keep the idea (e.g., 'Looking forward to seeing {student_first_name} again next week!' or 'See you next session!' or 'Can't wait to work with {student_first_name} again!')\n"
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

**Current full report context:**
{report_text[:600]}...

**The tutor started typing this sentence:**
"{partial_sentence}"

**Task:** Generate 4 DIFFERENT ways to COMPLETE this sentence (not new sentences, but endings for the sentence they started).

Generate 4 sentence COMPLETIONS that:
- Continue naturally from the partial sentence above
- Match the tutor's writing style
- Are light, casual, and conversational
- Each completion should finish the thought in a different way
- Start directly with the continuation (no repeating the partial sentence)

Example:
If partial sentence is "She really struggled with"
Good completions: ["the fraction problems.", "understanding the concept at first.", "the word problems, so we slowed down.", "the homework but got it by the end."]

Generate 4 completions for: "{partial_sentence}" """
            else:
                # Generate full standalone sentences
                prompt = f"""You are helping a tutor write a session report for {student_name} ({subject}).

**Current full report context:**
{report_text[:600]}...

**The paragraph being edited:**
"{cursor_paragraph}"

**Cursor position:**
"{context_before.strip()} [CURSOR] {context_after.strip()}"

Generate 4 sentences that would fit naturally RIGHT AT THE CURSOR position."""
        else:
            prompt = f"""You are helping a tutor write a session report for {student_name} ({subject}).

**Current draft:**
{report_text[:500]}...

Generate 4 sentences that could fit naturally in this report."""
        
        # Add style examples if previous reports available
        style_context = ""
        if previous_reports and len(previous_reports) > 0:
            style_context = "\n\n**WRITING STYLE REFERENCE - Study these examples to match the tutor's voice:**\n"
            for i, report in enumerate(previous_reports[:2], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                style_context += f"\n{clean_report[:500]}...\n"
        
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

**Task:** Generate 4 SHORT, STANDALONE sentences that:
1. Match the tutor's EXACT writing style (study the examples above)
2. Flow naturally from what comes immediately before the cursor
3. Are light, casual, and conversational (not overly formal)
4. Sound like this specific tutor wrote them, not generic tutor language
5. Each sentence should be COMPLETE and INDEPENDENT (can stand alone)
6. Keep each sentence SHORT - aim for 10-20 words each
7. Use regular hyphens (-) NOT em dashes (—)

**Format requirements:**
- Each item in the array must be ONE sentence only (ending with . ! or ?)
- NO multi-sentence paragraphs
- Each sentence should be insertable on its own

**Style notes:**
- Notice the tutor's sentence length and rhythm in the examples
- Match their level of detail and formality
- Keep it natural and genuine, not overly enthusiastic

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
        
        # Extract first name only
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
        
        # Show full example reports for style matching (2-3 complete reports)
        style_examples = ""
        if previous_reports:
            style_examples = "\n\n**FULL EXAMPLE REPORTS (study the writing style):**\n"
            for i, report in enumerate(previous_reports[:3], 1):
                # Remove signatures for cleaner examples
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                style_examples += f"\n--- Report {i} ---\n{clean_report[:800]}...\n"
        
        if sentence_type == 'opening':
            prompt = f"""You are helping a tutor write varied opening sentences for session reports about {student_first_name}.

**CRITICAL: ALWAYS use only the first name "{student_first_name}" - NEVER use a full name.**

Your goal is to match the tutor's EXACT writing style - their tone, rhythm, word choice, and personality.

**Opening sentences from past reports:**
{examples_text}
{style_examples}
{current_context}

**CRITICAL:** Each suggestion must be ONE sentence only (not multiple sentences).

**Task:** Generate 5 DIFFERENT opening sentences that:
1. Sound EXACTLY like this tutor wrote them (match their voice, not generic tutor-speak)
2. Are light, casual, and natural (like this tutor's style)
3. Vary in wording but maintain the same warm, welcoming feel
4. Fit naturally with what comes next in the report
5. Each must be ONE COMPLETE sentence (ending with . ! or ?)
6. Use the tutor's sentence patterns and rhythm
7. Use regular hyphens (-) NOT em dashes (—)

**Key style notes:**
- Study the examples to see how this specific tutor phrases things
- Notice their sentence length, word choices, and level of formality
- Don't be overly enthusiastic or formal - keep it genuine and conversational
- These should feel like natural variations, not templates with names swapped

**Format:** Each array item must be ONE sentence only.
Good: ["Great to see Sarah today!", "It was wonderful working with Sarah this week."]
Bad: ["Great to see Sarah today! We had a productive session."] ← Two sentences!

Return ONLY a JSON array of 5 SINGLE opening sentences:
["sentence 1", "sentence 2", "sentence 3", "sentence 4", "sentence 5"]"""
        else:  # closing
            prompt = f"""You are helping a tutor write varied closing sentences for session reports about {student_first_name}.

**CRITICAL: ALWAYS use only the first name "{student_first_name}" - NEVER use a full name.**

Your goal is to match the tutor's EXACT writing style - their tone, rhythm, word choice, and personality.

**Closing sentences from past reports:**
{examples_text}
{style_examples}
{current_context}

**CRITICAL:** Each suggestion must be ONE sentence only (not multiple sentences).

**Task:** Generate 5 DIFFERENT closing sentences that:
1. Sound EXACTLY like this tutor wrote them (match their voice, not generic tutor-speak)
2. Are light, casual, and natural (like this tutor's style)
3. Flow naturally from what comes before in the report
4. Are positive and forward-looking without being overly enthusiastic
5. Each must be ONE COMPLETE sentence (ending with . ! or ?)
6. Use the tutor's sentence patterns and rhythm
7. Use regular hyphens (-) NOT em dashes (—)

**Key style notes:**
- Study the examples to see how this specific tutor ends their reports
- Notice their sentence length, word choices, and level of formality
- Don't be overly enthusiastic or formal - keep it genuine and conversational
- These should feel like natural variations, not templates with names swapped
- Consider the context: if the report mentions an upcoming test or challenge, acknowledge it naturally

**Format:** Each array item must be ONE sentence only.
Good: ["Looking forward to next week!", "Can't wait to continue this work with Sarah."]
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
                    model=self.model,
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
            style_context = "\n\n**WRITING STYLE REFERENCE (study these examples to match the tutor's voice):**\n"
            for i, report in enumerate(previous_reports[:2], 1):
                import re
                clean_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', report).strip()
                style_context += f"\n--- Example {i} ---\n{clean_report[:600]}...\n"
        
        # Get context before and after the paragraph
        if paragraph in full_report:
            parts = full_report.split(paragraph)
            context_before = parts[0][-300:] if len(parts[0]) > 300 else parts[0]
            context_after = parts[1][:300] if len(parts) > 1 and len(parts[1]) > 300 else (parts[1] if len(parts) > 1 else "")
        else:
            context_before = ""
            context_after = ""
        
        prompt = f"""You are helping a tutor rewrite a paragraph from a session report about {student_name}.

**Your goal:** Completely REWRITE this paragraph in the tutor's style while keeping the same information and key points.

**The paragraph to rewrite:**
{paragraph}

**What comes BEFORE this paragraph:**
{context_before if context_before else "(Beginning of report)"}

**What comes AFTER this paragraph:**
{context_after if context_after else "(End of report)"}
{style_context}

**CRITICAL INSTRUCTIONS:**
1. Keep ALL the same information and key points from the original
2. Write it in the tutor's EXACT style (study the examples above)
3. Use completely DIFFERENT wording and sentence structure than the original
4. Make it flow naturally with what comes before and after
5. Match the tutor's:
   - Sentence length and rhythm
   - Level of detail and formality
   - Word choices and phrasing style
   - Casual, conversational tone
6. Use regular hyphens (-) NOT em dashes (—)
7. Return ONLY the rewritten paragraph, no quotes or explanation

**What to keep:**
- All facts, activities, topics, and observations
- The overall message and tone (positive/constructive/etc)
- The purpose of this paragraph in the report

**What to change:**
- Sentence structure and wording
- How ideas are ordered or connected
- The way concepts are expressed

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
    
    def polish_full_report(self, report_text: str) -> Dict:
        """Polish entire report using GPT-4o, tracking all changes made
        
        Returns:
            {
                'polished_text': str,
                'changes': [{'type': 'addition|deletion|modification', 'original': str, 'polished': str, 'context': str}]
            }
        """
        
        if not self.client:
            return {'polished_text': report_text, 'changes': []}
        
        prompt = f"""Please polish this report for me. Keep my wording but revise/improve as needed, as is appropriate for the context. Avoid em dashes.

IMPORTANT: After the polished report, list ALL the changes you made in this exact format:
---CHANGES---
- Changed "original phrase" to "new phrase" (reason)
- Fixed "original" to "new" (reason)
etc.

Report to polish:

{report_text}"""

        try:
            # Force OpenAI with GPT-4o for this feature
            from openai import OpenAI
            openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = openai_client.chat.completions.create(
                model='gpt-4o',  # Using most powerful model as requested
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,  # Increased for more creative improvements while staying controlled
                max_tokens=4000  # Allow for longer reports
            )
            
            full_response = response.choices[0].message.content.strip()
            
            # Split response into polished text and changes
            if '---CHANGES---' in full_response:
                parts = full_response.split('---CHANGES---')
                polished_text = parts[0].strip()
                changes_text = parts[1].strip() if len(parts) > 1 else ""
                
                # Parse changes into structured format
                changes = []
                for line in changes_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        # Extract change details
                        changes.append({
                            'description': line.lstrip('-').lstrip('•').strip()
                        })
            else:
                # If AI didn't follow format, just return the text
                polished_text = full_response
                changes = [{'description': 'Report polished (changes not detailed)'}]
            
            return {
                'polished_text': polished_text,
                'changes': changes
            }
        
        except Exception as e:
            print(f"Error polishing full report: {e}")
            return {
                'polished_text': report_text,
                'changes': [],
                'error': str(e)
            }
    
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
    
    def ask_about_text(
        self,
        selected_text: str,
        question: str,
        full_report: str,
        student_name: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """Answer questions about selected text from a report"""
        if not self.client:
            return "AI service not available"
        
        # Build conversation context
        system_prompt = f"""You are a helpful AI assistant. You are chatting with a tutor who is writing a report for a parent about their tutoring session with {student_name}.

The tutor has selected a portion of their report and wants to ask you about it. Be helpful, supportive, and provide clear feedback or suggestions.

Your goal is to have a natural, helpful conversation with the tutor about their writing. Be supportive and provide clear, actionable advice or insights based on their questions."""
        
        user_prompt = f"""**Selected text from report:**
"{selected_text}"

**Full report context:**
{full_report[:500]}...

**Tutor's question:**
{question}"""
        
        try:
            if self.provider == 'openai':
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history
                if conversation_history:
                    for chat_item in conversation_history:
                        messages.append({"role": "user", "content": chat_item['question']})
                        messages.append({"role": "assistant", "content": chat_item['answer']})
                
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=messages,
                    temperature=0.8,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                messages = []
                
                # Add conversation history
                if conversation_history:
                    for chat_item in conversation_history:
                        messages.append({"role": "user", "content": chat_item['question']})
                        messages.append({"role": "assistant", "content": chat_item['answer']})
                
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    temperature=0.8,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            print(f"Error in ask_about_text: {e}")
            return "Sorry, I encountered an error. Please try again."
    
    def get_synonyms(self, word: str, context: str) -> List[str]:
        """Get contextual synonyms for a word"""
        if not self.client:
            return []
        
        prompt = f"""Provide 5-7 contextual synonyms or alternative phrasings for the word "{word}" as used in this context:

"{context}"

Consider:
- The tone should be professional but warm (tutoring report context)
- Synonyms should fit naturally in the sentence
- Include both single-word and short phrase alternatives if appropriate

Return ONLY a JSON array of synonyms:
["synonym1", "synonym2", "synonym3", ...]"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=150
                )
                result = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            
            # Parse JSON response
            import json
            synonyms = json.loads(result)
            return synonyms if isinstance(synonyms, list) else []
        
        except Exception as e:
            print(f"Error getting synonyms: {e}")
            return []
    
    def review_report(self, report_text: str, student_name: str) -> List[Dict]:
        """Review a report and provide improvement suggestions"""
        if not self.client:
            return []
        
        prompt = f"""You are reviewing a tutoring session report about {student_name}. Analyze the report and identify specific phrases or sentences that could be improved.

**Report:**
{report_text}

For each issue you find, provide:
1. The specific text that needs improvement (exact quote from report)
2. What the issue is (clarity, tone, grammar, redundancy, etc.)
3. 2-3 alternative suggestions that maintain the writer's voice

Focus on:
- Clarity and conciseness
- Professional but warm tone
- Grammar and punctuation
- Redundant phrasing
- Vague statements that could be more specific

Return ONLY a JSON array of suggestions in this exact format:
[
  {{
    "original": "exact text from report",
    "issue": "brief description of the issue",
    "suggestions": ["alternative 1", "alternative 2"],
    "start_index": 0,
    "end_index": 20
  }}
]

If the report is already excellent, return an empty array: []"""
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=1000
                )
                result = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.5,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            
            # Parse JSON response
            import json
            # Clean up markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
                result = result.strip()
            
            suggestions = json.loads(result)
            
            # Find actual positions in text for each suggestion
            for suggestion in suggestions:
                original_text = suggestion.get('original', '')
                if original_text in report_text:
                    start_idx = report_text.find(original_text)
                    suggestion['start_index'] = start_idx
                    suggestion['end_index'] = start_idx + len(original_text)
            
            return suggestions if isinstance(suggestions, list) else []
        
        except Exception as e:
            print(f"Error reviewing report: {e}")
            return []
    
    def analyze_notes_for_gaps(
        self,
        student_name: str,
        subject: str,
        topics_covered: str,
        activities: str,
        notes: str
    ) -> Dict:
        """
        Analyze session notes to identify missing information that would enhance the report.
        Only returns questions if there are actual gaps - returns empty if notes are complete.
        
        Returns:
            {
                'has_gaps': bool,
                'questions': [{'id': str, 'question': str, 'reason': str}]
            }
        """
        
        if not self.client:
            return {'has_gaps': False, 'questions': []}
        
        prompt = f"""Analyze these tutoring session notes to determine if any CRITICAL information is missing that would significantly improve the report quality.

Student: {student_name}
Subject: {subject or 'Not specified'}
Topics Covered: {topics_covered or 'Not specified'}
Activities: {activities or 'Not specified'}
Session Notes: {notes or 'Not specified'}

IMPORTANT RULES:
1. ONLY flag something as missing if it's truly important for a parent to know
2. DO NOT ask about information that's already present (even if vague)
3. DO NOT ask for unnecessary details
4. Focus on: major struggles/breakthroughs, specific mistakes, performance assessment, next steps
5. Maximum 3 questions, ideally 1-2

Return a JSON object in this EXACT format:
{{
  "has_gaps": true/false,
  "questions": [
    {{
      "id": "q1",
      "question": "Specific question here?",
      "reason": "Why this matters for the report"
    }}
  ]
}}

If the notes are reasonably complete (have topics, some detail about performance), return:
{{
  "has_gaps": false,
  "questions": []
}}"""

        try:
            if self.provider == 'openai':
                # Use base gpt-4o-mini for analysis (fast and cheap)
                response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500
                )
                result = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            
            # Parse JSON response
            import json
            # Clean up markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
                result = result.strip()
            
            analysis = json.loads(result)
            
            # Validate structure
            if not isinstance(analysis, dict):
                return {'has_gaps': False, 'questions': []}
            
            return {
                'has_gaps': analysis.get('has_gaps', False),
                'questions': analysis.get('questions', [])
            }
        
        except Exception as e:
            print(f"Error analyzing notes for gaps: {e}")
            # If analysis fails, don't block report generation
            return {'has_gaps': False, 'questions': []}


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
