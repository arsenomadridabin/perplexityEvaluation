#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

print("Clearing all database data...")

with transaction.atomic():
    Classification.objects.all().delete()
    MatchedPair.objects.all().delete()
    DataEntry.objects.all().delete()

print("All data cleared!")

gt_count = DataEntry.objects.filter(entry_type='ground_truth').count()
pred_count = DataEntry.objects.filter(entry_type='predicted').count()
pair_count = MatchedPair.objects.count()
class_count = Classification.objects.count()

print(f"Remaining - GT: {gt_count}, Pred: {pred_count}, Pairs: {pair_count}, Classifications: {class_count}")

if gt_count == 0 and pred_count == 0 and pair_count == 0 and class_count == 0:
    print("✅ Database is completely empty!")
else:
    print("❌ Some data still remains") 