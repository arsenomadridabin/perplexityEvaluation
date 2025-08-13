#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

def test_no_unique_constraint():
    """Test that the unique_together constraint has been removed"""
    print("=== TESTING NO UNIQUE CONSTRAINT ===")
    
    # Clear database first
    with transaction.atomic():
        Classification.objects.all().delete()
        MatchedPair.objects.all().delete()
        DataEntry.objects.all().delete()
    print("Database cleared")
    
    # Test creating duplicate entries (should work now)
    print("\nTesting duplicate entry creation...")
    
    # Create first entry
    entry1 = DataEntry.objects.create(
        entry_type='ground_truth',
        polymer_system='Kapton',
        force_field='OPLS-AA',
        density='1.2',
        glass_transition_temp='600'
    )
    print(f"Created entry 1: {entry1}")
    
    # Create duplicate entry (should work now)
    entry2 = DataEntry.objects.create(
        entry_type='ground_truth',
        polymer_system='Kapton',
        force_field='OPLS-AA',
        density='1.3',
        glass_transition_temp='650'
    )
    print(f"Created entry 2: {entry2}")
    
    # Create another duplicate
    entry3 = DataEntry.objects.create(
        entry_type='ground_truth',
        polymer_system='Kapton',
        force_field='OPLS-AA',
        density='1.4',
        glass_transition_temp='700'
    )
    print(f"Created entry 3: {entry3}")
    
    # Check total count
    total_entries = DataEntry.objects.filter(
        entry_type='ground_truth',
        polymer_system='Kapton',
        force_field='OPLS-AA'
    ).count()
    
    print(f"\nTotal entries with same polymer_system and force_field: {total_entries}")
    
    if total_entries == 3:
        print("✅ SUCCESS: Unique constraint has been removed!")
        print("✅ All entries can now be created without restrictions")
    else:
        print("❌ FAILED: Unique constraint still exists")
    
    # Test with actual JSON data
    print("\n=== TESTING WITH ACTUAL JSON DATA ===")
    
    # Load ground truth data
    with open('ground_truth.json', 'r') as f:
        gt_data = json.load(f)
    
    # Load predicted data
    with open('predicted.json', 'r') as f:
        pred_data = json.load(f)
    
    print(f"Ground Truth JSON: {len(gt_data)} entries")
    print(f"Predicted JSON: {len(pred_data)} entries")
    
    # Create all entries
    with transaction.atomic():
        # Clear existing entries
        DataEntry.objects.all().delete()
        
        # Create ground truth entries
        for item in gt_data:
            DataEntry.objects.create(
                entry_type='ground_truth',
                polymer_system=item['polymer_system'],
                force_field=item['force_field'],
                density=item.get('Density (g/cm³)', 'NA'),
                glass_transition_temp=item.get('Glass Transition Temperature (K)', 'NA'),
                radius_of_gyration=item.get('Radius of Gyration (nm)', 'NA'),
                youngs_modulus=item.get('Young\'s Modulus (GPa)', 'NA'),
                diffusion_coefficient=item.get('Diffusion Coefficient (m²/s)', 'NA'),
                viscosity=item.get('Viscosity (Pa s)', 'NA'),
            )
        
        # Create predicted entries
        for item in pred_data:
            DataEntry.objects.create(
                entry_type='predicted',
                polymer_system=item['polymer_system'],
                force_field=item['force_field'],
                density=item.get('Density (g/cm³)', 'NA'),
                glass_transition_temp=item.get('Glass Transition Temperature (K)', 'NA'),
                radius_of_gyration=item.get('Radius of Gyration (nm)', 'NA'),
                youngs_modulus=item.get('Young\'s Modulus (GPa)', 'NA'),
                diffusion_coefficient=item.get('Diffusion Coefficient (m²/s)', 'NA'),
                viscosity=item.get('Viscosity (Pa s)', 'NA'),
            )
    
    # Check results
    total_gt = DataEntry.objects.filter(entry_type='ground_truth').count()
    total_pred = DataEntry.objects.filter(entry_type='predicted').count()
    
    print(f"\n=== RESULTS ===")
    print(f"Expected Ground Truth: {len(gt_data)}")
    print(f"Actual Ground Truth: {total_gt}")
    print(f"Expected Predicted: {len(pred_data)}")
    print(f"Actual Predicted: {total_pred}")
    
    if total_gt == len(gt_data) and total_pred == len(pred_data):
        print("✅ PERFECT MATCH: All entries created successfully!")
    else:
        print("❌ MISMATCH: Some entries were not created")

if __name__ == "__main__":
    test_no_unique_constraint() 