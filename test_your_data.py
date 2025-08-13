#!/usr/bin/env python
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import DataEntry, MatchedPair, Classification
from django.db import transaction

def test_your_data():
    """Test with your actual data"""
    print("=== TESTING YOUR ACTUAL DATA ===")
    
    # Clear database first
    with transaction.atomic():
        Classification.objects.all().delete()
        MatchedPair.objects.all().delete()
        DataEntry.objects.all().delete()
    print("Database cleared")
    
    # Your actual data
    your_data = [
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
            "force_field": "Martini",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "1.777",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 20-mer",
            "force_field": "IBI",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "1.701",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 20-mer",
            "force_field": "CHARMM36",
            "Density (g/cm³)": "1.370",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "NA",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 40-mer",
            "force_field": "CHARMM36",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "NA",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 40-mer",
            "force_field": "Martini",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "NA",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 40-mer",
            "force_field": "IBI",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "NA",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        },
        {
            "polymer_system": "Amylose 100-mer",
            "force_field": "IBI",
            "Density (g/cm³)": "NA",
            "Glass Transition Temperature (K)": "NA",
            "Radius of Gyration (nm)": "NA",
            "Young's Modulus (GPa)": "NA",
            "Diffusion Coefficient (m²/s)": "NA",
            "Viscosity (Pa s)": "NA"
        }
    ]
    
    print(f"Your data has {len(your_data)} entries")
    
    # Test with the new create() method
    print("\n=== TESTING WITH create() METHOD (FIXED) ===")
    with transaction.atomic():
        DataEntry.objects.all().delete()
        
        for item in your_data:
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
    
    count_created = DataEntry.objects.filter(entry_type='ground_truth').count()
    print(f"Entries created: {count_created}")
    
    # Show all created entries
    print("\n=== ALL CREATED ENTRIES ===")
    entries = DataEntry.objects.filter(entry_type='ground_truth').order_by('polymer_system', 'force_field')
    for i, entry in enumerate(entries, 1):
        print(f"{i}. {entry.polymer_system} ({entry.force_field})")
        print(f"   Density: {entry.density}, Glass Transition: {entry.glass_transition_temp}, Radius: {entry.radius_of_gyration}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Expected entries: {len(your_data)}")
    print(f"Actually created: {count_created}")
    
    if count_created == len(your_data):
        print("✅ SUCCESS: All 8 entries created correctly!")
    else:
        print(f"❌ ISSUE: Only {count_created} out of {len(your_data)} entries created")

if __name__ == "__main__":
    test_your_data() 