#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

def simulate_upload():
    """Simulate the file upload process"""
    print("=== SIMULATING FILE UPLOAD ===")
    
    # Load ground truth data
    with open('ground_truth.json', 'r') as f:
        gt_data = json.load(f)
    
    # Load predicted data
    with open('predicted.json', 'r') as f:
        pred_data = json.load(f)
    
    print(f"Ground Truth JSON has {len(gt_data)} entries")
    print(f"Predicted JSON has {len(pred_data)} entries")
    
    # Simulate the upload process
    with transaction.atomic():
        # Load ground truth data
        for item in gt_data:
            DataEntry.objects.update_or_create(
                entry_type='ground_truth',
                polymer_system=item['polymer_system'],
                force_field=item['force_field'],
                defaults={
                    'density': item.get('Density (g/cm³)', 'NA'),
                    'glass_transition_temp': item.get('Glass Transition Temperature (K)', 'NA'),
                    'radius_of_gyration': item.get('Radius of Gyration (nm)', 'NA'),
                    'youngs_modulus': item.get('Young\'s Modulus (GPa)', 'NA'),
                    'diffusion_coefficient': item.get('Diffusion Coefficient (m²/s)', 'NA'),
                    'viscosity': item.get('Viscosity (Pa s)', 'NA'),
                }
            )
        
        # Load predicted data
        for item in pred_data:
            DataEntry.objects.update_or_create(
                entry_type='predicted',
                polymer_system=item['polymer_system'],
                force_field=item['force_field'],
                defaults={
                    'density': item.get('Density (g/cm³)', 'NA'),
                    'glass_transition_temp': item.get('Glass Transition Temperature (K)', 'NA'),
                    'radius_of_gyration': item.get('Radius of Gyration (nm)', 'NA'),
                    'youngs_modulus': item.get('Young\'s Modulus (GPa)', 'NA'),
                    'diffusion_coefficient': item.get('Diffusion Coefficient (m²/s)', 'NA'),
                    'viscosity': item.get('Viscosity (Pa s)', 'NA'),
                }
            )
    
    print("Upload simulation completed!")

def check_data():
    """Check what data is in the database"""
    total_gt = DataEntry.objects.filter(entry_type='ground_truth').count()
    total_pred = DataEntry.objects.filter(entry_type='predicted').count()
    
    print(f"\n=== DATABASE STATUS AFTER UPLOAD ===")
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
    simulate_upload()
    check_data() 