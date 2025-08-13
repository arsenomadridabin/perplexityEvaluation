#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

def clear_database():
    """Clear all data from the database"""
    print("Clearing database...")
    with transaction.atomic():
        Classification.objects.all().delete()
        MatchedPair.objects.all().delete()
        DataEntry.objects.all().delete()
    print("Database cleared!")

def check_data():
    """Check what data is in the database"""
    total_gt = DataEntry.objects.filter(entry_type='ground_truth').count()
    total_pred = DataEntry.objects.filter(entry_type='predicted').count()
    
    print(f"\n=== DATABASE STATUS ===")
    print(f"Total Ground Truth entries: {total_gt}")
    print(f"Total Predicted entries: {total_pred}")
    
    if total_gt > 0:
        print(f"\n=== GROUND TRUTH ENTRIES ===")
        gt_entries = DataEntry.objects.filter(entry_type='ground_truth')
        for entry in gt_entries:
            print(f"- ID: {entry.id}, System: {entry.polymer_system}, Force Field: {entry.force_field}, No Match: {entry.marked_no_match}")
    
    if total_pred > 0:
        print(f"\n=== PREDICTED ENTRIES ===")
        pred_entries = DataEntry.objects.filter(entry_type='predicted')
        for entry in pred_entries:
            print(f"- ID: {entry.id}, System: {entry.polymer_system}, Force Field: {entry.force_field}, No Match: {entry.marked_no_match}")
    
    # Check what would be visible on matching page
    matched_pairs = MatchedPair.objects.all()
    matched_gt_ids = set(matched_pairs.values_list('ground_truth_id', flat=True))
    matched_pred_ids = set(matched_pairs.values_list('predicted_id', flat=True))
    
    visible_gt = DataEntry.objects.filter(
        entry_type='ground_truth',
        marked_no_match=False
    ).exclude(
        id__in=matched_gt_ids
    ).count()
    
    visible_pred = DataEntry.objects.filter(
        entry_type='predicted',
        marked_no_match=False
    ).exclude(
        id__in=matched_pred_ids
    ).count()
    
    print(f"\n=== MATCHING PAGE VISIBILITY ===")
    print(f"Visible Ground Truth entries: {visible_gt}")
    print(f"Visible Predicted entries: {visible_pred}")
    print(f"Matched pairs: {matched_pairs.count()}")
    print(f"No match entries: {DataEntry.objects.filter(marked_no_match=True).count()}")

if __name__ == "__main__":
    clear_database()
    check_data() 