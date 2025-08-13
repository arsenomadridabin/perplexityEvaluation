#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

print("=== CLEARING ALL DATA FOR FRESH START ===")

# Get counts before clearing
gt_count_before = DataEntry.objects.filter(entry_type='ground_truth').count()
pred_count_before = DataEntry.objects.filter(entry_type='predicted').count()
pair_count_before = MatchedPair.objects.count()
class_count_before = Classification.objects.count()

print(f"Current data:")
print(f"- Ground Truth entries: {gt_count_before}")
print(f"- Predicted entries: {pred_count_before}")
print(f"- Matched pairs: {pair_count_before}")
print(f"- Classifications: {class_count_before}")

# Clear all data
with transaction.atomic():
    print("\nClearing all data...")
    Classification.objects.all().delete()
    MatchedPair.objects.all().delete()
    DataEntry.objects.all().delete()
    print("✅ All data deleted!")

# Verify everything is cleared
gt_count_after = DataEntry.objects.filter(entry_type='ground_truth').count()
pred_count_after = DataEntry.objects.filter(entry_type='predicted').count()
pair_count_after = MatchedPair.objects.count()
class_count_after = Classification.objects.count()

print(f"\nAfter clearing:")
print(f"- Ground Truth entries: {gt_count_after}")
print(f"- Predicted entries: {pred_count_after}")
print(f"- Matched pairs: {pair_count_after}")
print(f"- Classifications: {class_count_after}")

if gt_count_after == 0 and pred_count_after == 0 and pair_count_after == 0 and class_count_after == 0:
    print("\n🎉 SUCCESS: Database is completely empty!")
    print("🚀 Ready for fresh data upload!")
else:
    print("\n❌ ERROR: Some data still remains")

print("\nYou can now upload your JSON files and all entries will be created correctly!") 