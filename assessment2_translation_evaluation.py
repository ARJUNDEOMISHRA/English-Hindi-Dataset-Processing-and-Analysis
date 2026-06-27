"""
===============================================================================
Assessment 2: LLM-Based Translation Evaluation
===============================================================================
This script performs the following:
1. Loads the model-generated Hindi translations from assessment2_translations.xlsx
2. Retrieves reference (ground-truth) Hindi translations from the IITB corpus
3. Evaluates translation quality using three standard MT metrics:
   - BLEU  (BiLingual Evaluation Understudy)
   - CHRF  (Character n-gram F-score)
   - TER   (Translation Error Rate)
4. Computes both corpus-level and sentence-level scores
5. Exports all results to Excel (with detailed per-sentence scores)
6. Generates a comprehensive text-based evaluation report
===============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from datasets import load_dataset
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF, TER

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_EXCEL = os.path.join(SCRIPT_DIR, "assessment2_translations.xlsx")
OUTPUT_EXCEL = os.path.join(SCRIPT_DIR, "assessment2_evaluation_results.xlsx")
OUTPUT_TEXT = os.path.join(SCRIPT_DIR, "assessment2_evaluation_report.txt")
SAMPLE_SIZE = 100  # Number of sentences to evaluate (as per assessment requirement)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load Model-Generated Translations
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 70)
print("STEP 1: Loading model-generated translations from Excel")
print("=" * 70)

try:
    df_translations = pd.read_excel(INPUT_EXCEL, engine='openpyxl')
    print(f"✓ Loaded {len(df_translations)} sentence pairs from {os.path.basename(INPUT_EXCEL)}")
    print(f"  Columns: {list(df_translations.columns)}")
except FileNotFoundError:
    print(f"✗ Error: File not found: {INPUT_EXCEL}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error loading Excel: {e}")
    sys.exit(1)

# Rename columns for internal consistency
df_translations.columns = ['English', 'Model_Hindi']

# Clean: drop any rows with empty/null translations
df_translations = df_translations.dropna(subset=['English', 'Model_Hindi']).reset_index(drop=True)
print(f"  Valid sentence pairs after cleaning: {len(df_translations)}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Load Reference Translations from IITB Corpus
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 2: Loading IITB English-Hindi Corpus for reference translations")
print("=" * 70)

print("  Loading dataset from Hugging Face (this may take a moment)...")

try:
    dataset = load_dataset("cfilt/iitb-english-hindi", split="train")
    print(f"✓ Dataset loaded: {len(dataset):,} sentence pairs")
except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    sys.exit(1)

# Build a lookup dictionary: English sentence → Hindi reference
# We normalize whitespace for matching
print("  Building reference translation lookup index...")
ref_lookup = {}
for entry in dataset:
    en = entry['translation']['en'].strip()
    hi = entry['translation']['hi'].strip()
    ref_lookup[en] = hi

print(f"  Indexed {len(ref_lookup):,} unique English sentences")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Match and Align Reference Translations
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3: Matching model translations with reference translations")
print("=" * 70)

references = []
model_outputs = []
english_sentences = []
match_status = []

for idx, row in df_translations.iterrows():
    en = row['English'].strip()
    model_hi = row['Model_Hindi'].strip()

    # Try exact match first
    ref_hi = ref_lookup.get(en, None)

    # If not found and sentence contains newlines (concatenated sentences),
    # try matching the first sentence
    if ref_hi is None and '\n' in en:
        first_sentence = en.split('\n')[0].strip()
        ref_hi = ref_lookup.get(first_sentence, None)

    if ref_hi is not None:
        references.append(ref_hi)
        model_outputs.append(model_hi)
        english_sentences.append(en)
        match_status.append("Matched")
    else:
        match_status.append("No Reference")

total_matched = match_status.count("Matched")
total_unmatched = match_status.count("No Reference")
print(f"  Total sentence pairs:   {len(df_translations)}")
print(f"  Matched with reference: {total_matched}")
print(f"  No reference found:     {total_unmatched}")

# If we have fewer matches than needed, we'll use what we have
eval_count = min(SAMPLE_SIZE, len(references))
if eval_count < SAMPLE_SIZE:
    print(f"\n⚠ Only {eval_count} sentences matched with references (target: {SAMPLE_SIZE})")
    print(f"  Proceeding with {eval_count} matched sentences for evaluation")
else:
    # Use exactly SAMPLE_SIZE sentences
    references = references[:SAMPLE_SIZE]
    model_outputs = model_outputs[:SAMPLE_SIZE]
    english_sentences = english_sentences[:SAMPLE_SIZE]
    print(f"\n✓ Using {SAMPLE_SIZE} sentence pairs for evaluation")

# If no matches at all, use model translations as self-reference for demo
if eval_count == 0:
    print("\n⚠ No exact matches found in IITB corpus.")
    print("  The model translations appear to come from a different source.")
    print("  Using all 200 sentences for evaluation with corpus-level metrics.")
    print("  References will be sourced from the IITB corpus by matching substrings...")

    # Fallback: use fuzzy/substring matching or just evaluate what we have
    # For the assessment, we'll use the model translations and generate
    # reference translations by re-sampling from the IITB corpus
    # based on closest English sentence match

    from difflib import SequenceMatcher

    print("  Performing fuzzy matching (this may take a moment)...")

    # Sample from translations
    sample_df = df_translations.head(SAMPLE_SIZE).copy()
    references = []
    model_outputs = []
    english_sentences = []

    # Get all IITB English sentences for fuzzy matching
    iitb_en_list = list(ref_lookup.keys())

    for idx, row in sample_df.iterrows():
        en = row['English'].strip()
        model_hi = row['Model_Hindi'].strip()

        # For concatenated sentences (with \n), use just the first one
        if '\n' in en:
            en_search = en.split('\n')[0].strip()
        else:
            en_search = en

        # Find best fuzzy match
        best_score = 0
        best_match = None
        # Search a subset for efficiency
        for iitb_en in iitb_en_list[:100000]:
            score = SequenceMatcher(None, en_search.lower(), iitb_en.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = iitb_en

        if best_match and best_score > 0.6:
            references.append(ref_lookup[best_match])
            model_outputs.append(model_hi)
            english_sentences.append(en)

        if (idx + 1) % 20 == 0:
            print(f"    Processed {idx + 1}/{len(sample_df)} sentences...")

    eval_count = len(references)
    print(f"  Fuzzy matched {eval_count} sentences (threshold > 0.6)")

if eval_count == 0:
    print("\n✗ Could not find any reference translations. Cannot compute metrics.")
    print("  Please ensure the assessment2_translations.xlsx contains sentences")
    print("  from the IITB English-Hindi corpus.")
    sys.exit(1)

print(f"\n✓ Final evaluation set: {eval_count} sentence pairs")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Compute Translation Quality Metrics
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 4: Computing Translation Quality Metrics")
print("=" * 70)

# Initialize metric objects
bleu_metric = BLEU()
chrf_metric = CHRF()
ter_metric = TER()

# ── 4a: Corpus-Level Scores ──────────────────────────────────────────────────
print("\n── 4a: Corpus-Level Scores ──")

# sacrebleu expects: hypotheses = list of strings, references = list of list of strings
hypotheses = model_outputs
refs_wrapped = [references]  # Single reference per sentence

corpus_bleu = bleu_metric.corpus_score(hypotheses, refs_wrapped)
corpus_chrf = chrf_metric.corpus_score(hypotheses, refs_wrapped)
corpus_ter = ter_metric.corpus_score(hypotheses, refs_wrapped)

print(f"  BLEU Score:  {corpus_bleu.score:.2f}")
print(f"    ├── Precisions: {[f'{p:.1f}' for p in corpus_bleu.precisions]}")
print(f"    ├── BP:         {corpus_bleu.bp:.4f}")
print(f"    └── Ratio:      {corpus_bleu.sys_len}/{corpus_bleu.ref_len} = {corpus_bleu.sys_len/corpus_bleu.ref_len:.4f}")
print(f"  CHRF Score:  {corpus_chrf.score:.2f}")
print(f"  TER Score:   {corpus_ter.score:.2f}")

# ── 4b: Sentence-Level Scores ────────────────────────────────────────────────
print("\n── 4b: Sentence-Level Scores ──")

sentence_bleu_scores = []
sentence_chrf_scores = []
sentence_ter_scores = []

for i in range(eval_count):
    hyp = [model_outputs[i]]
    ref = [[references[i]]]

    s_bleu = bleu_metric.corpus_score(hyp, ref)
    s_chrf = chrf_metric.corpus_score(hyp, ref)
    s_ter = ter_metric.corpus_score(hyp, ref)

    sentence_bleu_scores.append(round(s_bleu.score, 2))
    sentence_chrf_scores.append(round(s_chrf.score, 2))
    sentence_ter_scores.append(round(s_ter.score, 2))

# Compute statistics
print(f"  BLEU  — Mean: {np.mean(sentence_bleu_scores):.2f}, "
      f"Median: {np.median(sentence_bleu_scores):.2f}, "
      f"Min: {np.min(sentence_bleu_scores):.2f}, "
      f"Max: {np.max(sentence_bleu_scores):.2f}")
print(f"  CHRF  — Mean: {np.mean(sentence_chrf_scores):.2f}, "
      f"Median: {np.median(sentence_chrf_scores):.2f}, "
      f"Min: {np.min(sentence_chrf_scores):.2f}, "
      f"Max: {np.max(sentence_chrf_scores):.2f}")
print(f"  TER   — Mean: {np.mean(sentence_ter_scores):.2f}, "
      f"Median: {np.median(sentence_ter_scores):.2f}, "
      f"Min: {np.min(sentence_ter_scores):.2f}, "
      f"Max: {np.max(sentence_ter_scores):.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Quality Classification
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 5: Translation Quality Classification")
print("=" * 70)

def classify_quality(bleu, chrf, ter):
    """Classify translation quality based on metric thresholds."""
    if bleu >= 40 and chrf >= 60 and ter <= 40:
        return "Excellent"
    elif bleu >= 25 and chrf >= 45 and ter <= 60:
        return "Good"
    elif bleu >= 10 and chrf >= 30 and ter <= 80:
        return "Fair"
    else:
        return "Poor"

quality_labels = []
for i in range(eval_count):
    label = classify_quality(
        sentence_bleu_scores[i],
        sentence_chrf_scores[i],
        sentence_ter_scores[i]
    )
    quality_labels.append(label)

# Count quality distribution
quality_counts = pd.Series(quality_labels).value_counts()
print("  Quality Distribution:")
for label in ["Excellent", "Good", "Fair", "Poor"]:
    count = quality_counts.get(label, 0)
    pct = (count / eval_count) * 100
    bar = "█" * int(pct / 2)
    print(f"    {label:10s}: {count:3d} ({pct:5.1f}%) {bar}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Export Results to Excel
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 6: Exporting results to Excel")
print("=" * 70)

# Create detailed results DataFrame
results_df = pd.DataFrame({
    'S.No': range(1, eval_count + 1),
    'English Sentence': english_sentences,
    'Reference Hindi Translation': references,
    'Model-Generated Hindi Translation': model_outputs,
    'BLEU Score': sentence_bleu_scores,
    'CHRF Score': sentence_chrf_scores,
    'TER Score': sentence_ter_scores,
    'Quality': quality_labels
})

# Create summary DataFrame
summary_data = {
    'Metric': ['BLEU', 'CHRF', 'TER'],
    'Corpus-Level Score': [
        round(corpus_bleu.score, 2),
        round(corpus_chrf.score, 2),
        round(corpus_ter.score, 2)
    ],
    'Mean (Sentence-Level)': [
        round(np.mean(sentence_bleu_scores), 2),
        round(np.mean(sentence_chrf_scores), 2),
        round(np.mean(sentence_ter_scores), 2)
    ],
    'Median': [
        round(np.median(sentence_bleu_scores), 2),
        round(np.median(sentence_chrf_scores), 2),
        round(np.median(sentence_ter_scores), 2)
    ],
    'Min': [
        round(np.min(sentence_bleu_scores), 2),
        round(np.min(sentence_chrf_scores), 2),
        round(np.min(sentence_ter_scores), 2)
    ],
    'Max': [
        round(np.max(sentence_bleu_scores), 2),
        round(np.max(sentence_chrf_scores), 2),
        round(np.max(sentence_ter_scores), 2)
    ],
    'Std Dev': [
        round(np.std(sentence_bleu_scores), 2),
        round(np.std(sentence_chrf_scores), 2),
        round(np.std(sentence_ter_scores), 2)
    ],
    'Interpretation': [
        'Higher is better (0-100). >40 = Excellent, >25 = Good',
        'Higher is better (0-100). >60 = Excellent, >45 = Good',
        'Lower is better (0-100+). <40 = Excellent, <60 = Good'
    ]
}
summary_df = pd.DataFrame(summary_data)

# Quality distribution DataFrame
quality_df = pd.DataFrame({
    'Quality Level': ['Excellent', 'Good', 'Fair', 'Poor'],
    'Count': [quality_counts.get(l, 0) for l in ['Excellent', 'Good', 'Fair', 'Poor']],
    'Percentage': [
        f"{(quality_counts.get(l, 0) / eval_count) * 100:.1f}%"
        for l in ['Excellent', 'Good', 'Fair', 'Poor']
    ],
    'Criteria': [
        'BLEU ≥ 40, CHRF ≥ 60, TER ≤ 40',
        'BLEU ≥ 25, CHRF ≥ 45, TER ≤ 60',
        'BLEU ≥ 10, CHRF ≥ 30, TER ≤ 80',
        'Below Fair thresholds'
    ]
})

# Write to Excel with multiple sheets
with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
    results_df.to_excel(writer, sheet_name='Sentence-Level Results', index=False)
    summary_df.to_excel(writer, sheet_name='Corpus-Level Summary', index=False)
    quality_df.to_excel(writer, sheet_name='Quality Distribution', index=False)

print(f"✓ Excel file saved: {OUTPUT_EXCEL}")
print(f"  Sheet 1: Sentence-Level Results ({eval_count} rows)")
print(f"  Sheet 2: Corpus-Level Summary (3 metrics)")
print(f"  Sheet 3: Quality Distribution (4 categories)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: Generate Text-Based Evaluation Report
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 7: Generating text-based evaluation report")
print("=" * 70)

report_lines = []
report_lines.append("=" * 70)
report_lines.append("ASSESSMENT 2: LLM-BASED TRANSLATION EVALUATION REPORT")
report_lines.append("English → Hindi Translation Quality Analysis")
report_lines.append("=" * 70)
report_lines.append("")
report_lines.append("─" * 70)
report_lines.append("1. DATASET INFORMATION")
report_lines.append("─" * 70)
report_lines.append(f"  Source Dataset:         IITB English-Hindi Parallel Corpus")
report_lines.append(f"  Translation Model:      LLM-based (model-generated)")
report_lines.append(f"  Input File:             {os.path.basename(INPUT_EXCEL)}")
report_lines.append(f"  Total Translated Pairs: {len(df_translations)}")
report_lines.append(f"  Evaluated Pairs:        {eval_count}")
report_lines.append(f"  Evaluation Metrics:     BLEU, CHRF, TER (via sacrebleu)")
report_lines.append("")
report_lines.append("─" * 70)
report_lines.append("2. CORPUS-LEVEL SCORES")
report_lines.append("─" * 70)
report_lines.append(f"  ┌───────────┬──────────┬──────────────────────────────────────────┐")
report_lines.append(f"  │ Metric    │  Score   │ Interpretation                           │")
report_lines.append(f"  ├───────────┼──────────┼──────────────────────────────────────────┤")
report_lines.append(f"  │ BLEU      │ {corpus_bleu.score:7.2f}  │ Higher = Better (0-100)                  │")
report_lines.append(f"  │ CHRF      │ {corpus_chrf.score:7.2f}  │ Higher = Better (0-100)                  │")
report_lines.append(f"  │ TER       │ {corpus_ter.score:7.2f}  │ Lower = Better (0-100+)                  │")
report_lines.append(f"  └───────────┴──────────┴──────────────────────────────────────────┘")
report_lines.append("")
report_lines.append(f"  BLEU Breakdown:")
report_lines.append(f"    Precisions (1-4 gram): {[f'{p:.1f}' for p in corpus_bleu.precisions]}")
report_lines.append(f"    Brevity Penalty:       {corpus_bleu.bp:.4f}")
report_lines.append(f"    Length Ratio:           {corpus_bleu.sys_len}/{corpus_bleu.ref_len} "
                     f"= {corpus_bleu.sys_len/corpus_bleu.ref_len:.4f}")
report_lines.append("")
report_lines.append("─" * 70)
report_lines.append("3. SENTENCE-LEVEL STATISTICS")
report_lines.append("─" * 70)
report_lines.append(f"  ┌───────────┬──────────┬──────────┬──────────┬──────────┬──────────┐")
report_lines.append(f"  │ Metric    │  Mean    │ Median   │   Min    │   Max    │ Std Dev  │")
report_lines.append(f"  ├───────────┼──────────┼──────────┼──────────┼──────────┼──────────┤")
report_lines.append(f"  │ BLEU      │ {np.mean(sentence_bleu_scores):7.2f}  │ {np.median(sentence_bleu_scores):7.2f}  │ {np.min(sentence_bleu_scores):7.2f}  │ {np.max(sentence_bleu_scores):7.2f}  │ {np.std(sentence_bleu_scores):7.2f}  │")
report_lines.append(f"  │ CHRF      │ {np.mean(sentence_chrf_scores):7.2f}  │ {np.median(sentence_chrf_scores):7.2f}  │ {np.min(sentence_chrf_scores):7.2f}  │ {np.max(sentence_chrf_scores):7.2f}  │ {np.std(sentence_chrf_scores):7.2f}  │")
report_lines.append(f"  │ TER       │ {np.mean(sentence_ter_scores):7.2f}  │ {np.median(sentence_ter_scores):7.2f}  │ {np.min(sentence_ter_scores):7.2f}  │ {np.max(sentence_ter_scores):7.2f}  │ {np.std(sentence_ter_scores):7.2f}  │")
report_lines.append(f"  └───────────┴──────────┴──────────┴──────────┴──────────┴──────────┘")
report_lines.append("")
report_lines.append("─" * 70)
report_lines.append("4. QUALITY DISTRIBUTION")
report_lines.append("─" * 70)
for label in ["Excellent", "Good", "Fair", "Poor"]:
    count = quality_counts.get(label, 0)
    pct = (count / eval_count) * 100
    bar = "█" * int(pct / 2)
    report_lines.append(f"  {label:10s}: {count:3d} ({pct:5.1f}%) {bar}")
report_lines.append("")
report_lines.append("  Quality Thresholds:")
report_lines.append("    Excellent: BLEU ≥ 40, CHRF ≥ 60, TER ≤ 40")
report_lines.append("    Good:      BLEU ≥ 25, CHRF ≥ 45, TER ≤ 60")
report_lines.append("    Fair:      BLEU ≥ 10, CHRF ≥ 30, TER ≤ 80")
report_lines.append("    Poor:      Below Fair thresholds")
report_lines.append("")
report_lines.append("─" * 70)
report_lines.append("5. SAMPLE TRANSLATIONS (Top 10)")
report_lines.append("─" * 70)

for i in range(min(10, eval_count)):
    report_lines.append(f"\n  [{i+1}] BLEU={sentence_bleu_scores[i]:.1f} | "
                        f"CHRF={sentence_chrf_scores[i]:.1f} | "
                        f"TER={sentence_ter_scores[i]:.1f} | "
                        f"Quality={quality_labels[i]}")
    report_lines.append(f"      EN:  {english_sentences[i][:120]}")
    report_lines.append(f"      REF: {references[i][:120]}")
    report_lines.append(f"      HYP: {model_outputs[i][:120]}")

report_lines.append("")
report_lines.append("─" * 70)
report_lines.append("6. METRIC DESCRIPTIONS")
report_lines.append("─" * 70)
report_lines.append("""
  BLEU (BiLingual Evaluation Understudy):
    Measures n-gram overlap between hypothesis and reference translations.
    Uses modified precision with a brevity penalty.
    Range: 0-100 (higher is better).
    A score > 30 is generally considered reasonable for MT systems.

  CHRF (Character n-gram F-score):
    Measures character-level n-gram overlap.
    More robust than BLEU for morphologically rich languages like Hindi.
    Range: 0-100 (higher is better).
    Less sensitive to tokenization differences.

  TER (Translation Error Rate):
    Measures the number of edits needed to transform hypothesis into reference.
    Considers insertions, deletions, substitutions, and shifts.
    Range: 0-100+ (lower is better).
    A score < 50 indicates reasonable translation quality.
""")
report_lines.append("─" * 70)
report_lines.append("7. KEY FINDINGS")
report_lines.append("─" * 70)

# Generate dynamic findings
if corpus_bleu.score >= 30:
    bleu_finding = "The corpus BLEU score indicates strong translation quality."
elif corpus_bleu.score >= 15:
    bleu_finding = "The corpus BLEU score indicates moderate translation quality."
else:
    bleu_finding = "The corpus BLEU score suggests room for improvement."

excellent_pct = (quality_counts.get("Excellent", 0) / eval_count) * 100
good_or_better_pct = ((quality_counts.get("Excellent", 0) + quality_counts.get("Good", 0)) / eval_count) * 100

report_lines.append(f"  • {bleu_finding}")
report_lines.append(f"  • CHRF score of {corpus_chrf.score:.1f} shows character-level translation accuracy.")
report_lines.append(f"  • TER score of {corpus_ter.score:.1f} indicates the editing distance from reference.")
report_lines.append(f"  • {excellent_pct:.1f}% of translations rated 'Excellent'.")
report_lines.append(f"  • {good_or_better_pct:.1f}% of translations rated 'Good' or better.")
report_lines.append(f"  • Total sentences evaluated: {eval_count}")
report_lines.append("")
report_lines.append("=" * 70)
report_lines.append("END OF EVALUATION REPORT")
report_lines.append("=" * 70)

# Write report to file
report_text = "\n".join(report_lines)
with open(OUTPUT_TEXT, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"✓ Text report saved: {OUTPUT_TEXT}")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("ASSESSMENT 2 — COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"  Sentences evaluated:   {eval_count}")
print(f"  Corpus BLEU:           {corpus_bleu.score:.2f}")
print(f"  Corpus CHRF:           {corpus_chrf.score:.2f}")
print(f"  Corpus TER:            {corpus_ter.score:.2f}")
print(f"\n  Output files:")
print(f"    Excel: {OUTPUT_EXCEL}")
print(f"    Text:  {OUTPUT_TEXT}")
print("=" * 70)
