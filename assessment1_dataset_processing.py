"""
===============================================================================
Assessment 1: English–Hindi Dataset Processing and Analysis
===============================================================================
This script performs the following:
1. Clones/loads the IITB English-Hindi Parallel Corpus from Hugging Face
2. Extracts English and Hindi sentences into a structured format
3. Computes word counts for each sentence
4. Filters sentences with word counts between 5 and 50 (both languages)
5. Filters sentence pairs with word count difference between -10 and +10
6. Exports the cleaned dataset to Excel format
===============================================================================
"""

import os
import sys
import pandas as pd
from datasets import load_dataset

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_EXCEL = os.path.join(OUTPUT_DIR, "assignment1_cleaned.xlsx")
MIN_WORD_COUNT = 5        # Minimum words per sentence (inclusive)
MAX_WORD_COUNT = 50       # Maximum words per sentence (inclusive)
MIN_DIFF = -10            # Minimum word count difference (inclusive)
MAX_DIFF = 10             # Maximum word count difference (inclusive)
MIN_ROWS = 10000          # Minimum number of rows required

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Load the Dataset from Hugging Face
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 70)
print("STEP 1: Loading IITB English-Hindi Parallel Corpus from Hugging Face")
print("=" * 70)

try:
    # Load the IITB English-Hindi Parallel Corpus
    # This is one of the most widely-used EN-HI benchmark datasets
    dataset = load_dataset("cfilt/iitb-english-hindi", split="train")
    print(f"✓ Dataset loaded successfully!")
    print(f"  Total sentence pairs available: {len(dataset):,}")
except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Extract English and Hindi Sentences
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 2: Extracting English and Hindi sentences into columns")
print("=" * 70)

# Extract sentences from the dataset
english_sentences = []
hindi_sentences = []

for entry in dataset:
    en = entry['translation']['en']
    hi = entry['translation']['hi']
    english_sentences.append(en)
    hindi_sentences.append(hi)

# Create initial DataFrame
df = pd.DataFrame({
    'English Sentences': english_sentences,
    'Hindi Sentences': hindi_sentences
})

print(f"✓ Extracted {len(df):,} sentence pairs")
print(f"  Column A: English Sentences")
print(f"  Column B: Hindi Sentences")

# Verify minimum row count
if len(df) >= MIN_ROWS:
    print(f"✓ Dataset contains {len(df):,} rows (≥ {MIN_ROWS:,} required)")
else:
    print(f"⚠ Dataset contains only {len(df):,} rows (< {MIN_ROWS:,} required)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Word Count Analysis
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3: Computing word counts and filtering (5 to 50 words)")
print("=" * 70)

# Compute word counts for English and Hindi
# For English: split by whitespace
# For Hindi: split by whitespace (Devanagari script words are space-separated)
df['Word Count (English)'] = df['English Sentences'].apply(lambda x: len(str(x).split()))
df['Word Count (Hindi)'] = df['Hindi Sentences'].apply(lambda x: len(str(x).split()))

print(f"  English word count range: {df['Word Count (English)'].min()} - {df['Word Count (English)'].max()}")
print(f"  Hindi word count range:   {df['Word Count (Hindi)'].min()} - {df['Word Count (Hindi)'].max()}")

# Filter: Keep only sentences where BOTH English AND Hindi word counts
# fall within the range [5, 50]
rows_before = len(df)
df_filtered = df[
    (df['Word Count (English)'] >= MIN_WORD_COUNT) &
    (df['Word Count (English)'] <= MAX_WORD_COUNT) &
    (df['Word Count (Hindi)'] >= MIN_WORD_COUNT) &
    (df['Word Count (Hindi)'] <= MAX_WORD_COUNT)
].copy()

rows_after = len(df_filtered)
rows_removed = rows_before - rows_after

print(f"\n✓ Word count filter applied ({MIN_WORD_COUNT}-{MAX_WORD_COUNT} words)")
print(f"  Rows before filtering: {rows_before:,}")
print(f"  Rows after filtering:  {rows_after:,}")
print(f"  Rows removed:          {rows_removed:,}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Word Count Difference Calculation
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 4: Computing word count difference and filtering (-10 to +10)")
print("=" * 70)

# Calculate difference: English word count - Hindi word count
df_filtered['Difference (EN - HI)'] = (
    df_filtered['Word Count (English)'] - df_filtered['Word Count (Hindi)']
)

print(f"  Difference range: {df_filtered['Difference (EN - HI)'].min()} to {df_filtered['Difference (EN - HI)'].max()}")

# Filter: Keep only pairs where the difference is within [-10, +10]
rows_before_diff = len(df_filtered)
df_final = df_filtered[
    (df_filtered['Difference (EN - HI)'] >= MIN_DIFF) &
    (df_filtered['Difference (EN - HI)'] <= MAX_DIFF)
].copy()

rows_after_diff = len(df_final)
rows_removed_diff = rows_before_diff - rows_after_diff

print(f"\n✓ Difference filter applied ({MIN_DIFF} to {MAX_DIFF})")
print(f"  Rows before filtering: {rows_before_diff:,}")
print(f"  Rows after filtering:  {rows_after_diff:,}")
print(f"  Rows removed:          {rows_removed_diff:,}")

# Reset index for clean output
df_final.reset_index(drop=True, inplace=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Export to Excel
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 5: Exporting cleaned dataset to Excel")
print("=" * 70)

# Reorder columns for the final output
df_final = df_final[[
    'English Sentences',
    'Hindi Sentences',
    'Word Count (English)',
    'Word Count (Hindi)',
    'Difference (EN - HI)'
]]

# Save to Excel
df_final.to_excel(OUTPUT_EXCEL, index=False, engine='openpyxl')

print(f"✓ Excel file saved: {OUTPUT_EXCEL}")
print(f"  Total rows in final dataset: {len(df_final):,}")
print(f"  Columns: {list(df_final.columns)}")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print(f"  Original dataset size:          {len(english_sentences):,}")
print(f"  After word count filter (5-50): {rows_after:,}")
print(f"  After difference filter (±10):  {len(df_final):,}")
print(f"\n  Word Count (English):")
print(f"    Mean:   {df_final['Word Count (English)'].mean():.2f}")
print(f"    Median: {df_final['Word Count (English)'].median():.1f}")
print(f"    Min:    {df_final['Word Count (English)'].min()}")
print(f"    Max:    {df_final['Word Count (English)'].max()}")
print(f"\n  Word Count (Hindi):")
print(f"    Mean:   {df_final['Word Count (Hindi)'].mean():.2f}")
print(f"    Median: {df_final['Word Count (Hindi)'].median():.1f}")
print(f"    Min:    {df_final['Word Count (Hindi)'].min()}")
print(f"    Max:    {df_final['Word Count (Hindi)'].max()}")
print(f"\n  Difference (EN - HI):")
print(f"    Mean:   {df_final['Difference (EN - HI)'].mean():.2f}")
print(f"    Median: {df_final['Difference (EN - HI)'].median():.1f}")
print(f"    Min:    {df_final['Difference (EN - HI)'].min()}")
print(f"    Max:    {df_final['Difference (EN - HI)'].max()}")

# Preview first 5 rows
print("\n" + "=" * 70)
print("PREVIEW: First 5 rows of the cleaned dataset")
print("=" * 70)
print(df_final.head().to_string(index=False))

print("\n✓ Assessment 1 completed successfully!")
print(f"✓ Output file: {OUTPUT_EXCEL}")
