# English-Hindi-Dataset-Processing-and-Analysis
======================================================================
STEP 1: Loading IITB English-Hindi Parallel Corpus from Hugging Face
======================================================================
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
✓ Dataset loaded successfully!
  Total sentence pairs available: 1,659,083

======================================================================
STEP 2: Extracting English and Hindi sentences into columns
======================================================================
✓ Extracted 1,659,083 sentence pairs
  Column A: English Sentences
  Column B: Hindi Sentences
✓ Dataset contains 1,659,083 rows (≥ 10,000 required)

======================================================================
STEP 3: Computing word counts and filtering (5 to 50 words)
======================================================================
  English word count range: 0 - 1917
  Hindi word count range:   0 - 1380

✓ Word count filter applied (5-50 words)
  Rows before filtering: 1,659,083
  Rows after filtering:  968,535
  Rows removed:          690,548

======================================================================
STEP 4: Computing word count difference and filtering (-10 to +10)
======================================================================
  Difference range: -44 to 45

✓ Difference filter applied (-10 to 10)
  Rows before filtering: 968,535
  Rows after filtering:  924,504
  Rows removed:          44,031
