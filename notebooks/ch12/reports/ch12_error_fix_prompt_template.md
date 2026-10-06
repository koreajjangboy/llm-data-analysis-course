# Minimal Context Error Fix Prompt Template

[Role]
You are an expert Python Data Engineer. Fix the code error based on the minimal context provided below without introducing security risks or data leakage.

[Context & Constraints]
1. Goal: {analysis_goal}
2. Minimal Data Schema: {schema_info}
3. Evidence/Metrics: {evidence_summary}
4. DO NOT use external network calls or unapproved libraries.

[Minimal Reproducible Code]
{minimal_code}

[Anonymized Error Log]
{anonymized_error_log}

[Instruction]
Provide only the corrected Python code snippet and a concise explanation of the fix.
