#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

def test_duplicate_entries():
    """Test handling of duplicate entries"""
    print("=== TESTING DUPLICATE ENTRIES ===")
    
    # Clear database first
    with transaction.atomic():
        Classification.objects.all().delete()
        MatchedPair.objects.all().delete()
        DataEntry.objects.all().delete()
    print("Database cleared")
    
    # Your test data with duplicates
    test_data = [
        {
            "polymer_system": "Amylose 20-mer",
            "force_field": "CHARMM36",
            "Density (g/cm³)": "1.240",
            "Glass Transition Temperature (K)": "586",
            "Radius of Gyration (nm)": "1.628",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 20-mer",
            "force_field": "CHARMM36",  # DUPLICATE!
            "Density (g/cm³)": "1.370",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "NA",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 20-mer",
            "force_field": "Martini",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "1.777",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        }
    ]
    
    print(f"Test data has {len(test_data)} entries")
    print("Entry 1 and 2 have same polymer_system and force_field (duplicate)")
    
    # Test with update_or_create (current method)
    print("\n=== TESTING WITH update_or_create (CURRENT METHOD) ===")
    with transaction.atomic():
        DataEntry.objects.all().delete()
        
        for item in test_data:
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
    
    count_update_or_create = DataEntry.objects.filter(entry_type='ground_truth').count()
    print(f"Entries created with update_or_create: {count_update_or_create}")
    
    # Show what was actually created
    entries = DataEntry.objects.filter(entry_type='ground_truth')
    for entry in entries:
        print(f"  - {entry.polymer_system} ({entry.force_field}): Density={entry.density}")
    
    # Test with create (should create all entries)
    print("\n=== TESTING WITH create (SHOULD CREATE ALL) ===")
    with transaction.atomic():
        DataEntry.objects.all().delete()
        
        for item in test_data:
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
    
    count_create = DataEntry.objects.filter(entry_type='ground_truth').count()
    print(f"Entries created with create: {count_create}")
    
    # Show what was actually created
    entries = DataEntry.objects.filter(entry_type='ground_truth')
    for entry in entries:
        print(f"  - {entry.polymer_system} ({entry.force_field}): Density={entry.density}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Expected entries: {len(test_data)}")
    print(f"update_or_create created: {count_update_or_create}")
    print(f"create created: {count_create}")
    
    if count_create == len(test_data):
        print("✅ create() method works correctly!")
    else:
        print("❌ create() method has issues")

if __name__ == "__main__":
    test_duplicate_entries() 