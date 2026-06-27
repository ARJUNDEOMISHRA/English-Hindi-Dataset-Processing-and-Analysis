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

  ======================================================================
STEP 1: Loading model-generated translations from Excel
======================================================================
✓ Loaded 200 sentence pairs from assessment2_translations.xlsx
  Columns: ['Original English sentence', 'Model-generated Hindi translation']
  Valid sentence pairs after cleaning: 200

======================================================================
STEP 2: Loading IITB English-Hindi Corpus for reference translations
======================================================================
  Loading dataset from Hugging Face (this may take a moment)...
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
✓ Dataset loaded: 1,659,083 sentence pairs
  Building reference translation lookup index...
  Indexed 1,093,623 unique English sentences

======================================================================
STEP 3: Matching model translations with reference translations
======================================================================
  Total sentence pairs:   200
  Matched with reference: 25
  No reference found:     175

⚠ Only 25 sentences matched with references (target: 100)
  Proceeding with 25 matched sentences for evaluation

✓ Final evaluation set: 25 sentence pairs

======================================================================
STEP 4: Computing Translation Quality Metrics
======================================================================

── 4a: Corpus-Level Scores ──
  BLEU Score:  13.27
    ├── Precisions: ['32.3', '16.3', '9.6', '6.2']
    ├── BP:         1.0000
    └── Ratio:      904/599 = 1.5092
  CHRF Score:  39.85
  TER Score:   129.49

── 4b: Sentence-Level Scores ──
  BLEU  — Mean: 15.15, Median: 10.68, Min: 0.00, Max: 65.97
  CHRF  — Mean: 35.98, Median: 37.30, Min: 3.14, Max: 84.91
  TER   — Mean: 148.77, Median: 80.00, Min: 14.29, Max: 804.55

======================================================================
STEP 5: Translation Quality Classification
======================================================================
  Quality Distribution:
    Excellent :   1 (  4.0%) ██
    Good      :   2 (  8.0%) ████
    Fair      :   7 ( 28.0%) ██████████████
    Poor      :  15 ( 60.0%) ██████████████████████████████

======================================================================
STEP 6: Exporting results to Excel
======================================================================
✓ Excel file saved: /home/arjun-deo-mishra/Desktop/HINDI AND ENGLISH/assessment2_evaluation_results.xlsx
  Sheet 1: Sentence-Level Results (25 rows)
  Sheet 2: Corpus-Level Summary (3 metrics)
  Sheet 3: Quality Distribution (4 categories)

======================================================================
STEP 7: Generating text-based evaluation report
======================================================================
✓ Text report saved: /home/arjun-deo-mishra/Desktop/HINDI AND ENGLISH/assessment2_evaluation_report.txt

======================================================================
ASSESSMENT 2 — COMPLETED SUCCESSFULLY
======================================================================
  Sentences evaluated:   25
  Corpus BLEU:           13.27
  Corpus CHRF:           39.85
  Corpus TER:            129.49

  Output files:
    Excel: /home/arjun-deo-mishra/Desktop/HINDI AND ENGLISH/assessment2_evaluation_results.xlsx
    Text:  /home/arjun-deo-mishra/Desktop/HINDI AND ENGLISH/assessment2_evaluation_report.txt
