from django.db import models
import json
from django.core.exceptions import ValidationError

class DataEntry(models.Model):
    """Model to store ground truth and predicted data entries"""
    ENTRY_TYPE_CHOICES = [
        ('ground_truth', 'Ground Truth'),
        ('predicted', 'Predicted'),
    ]
    
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    polymer_system = models.CharField(max_length=200)
    force_field = models.CharField(max_length=100)
    
    # Property fields
    density = models.CharField(max_length=50, blank=True, null=True)
    glass_transition_temp = models.CharField(max_length=50, blank=True, null=True)
    radius_of_gyration = models.CharField(max_length=50, blank=True, null=True)
    youngs_modulus = models.CharField(max_length=50, blank=True, null=True)
    diffusion_coefficient = models.CharField(max_length=50, blank=True, null=True)
    viscosity = models.CharField(max_length=50, blank=True, null=True)
    
    # Track if entry has been marked as "no match"
    marked_no_match = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Removed unique_together constraint to allow all entries
        verbose_name_plural = "Data entries"
    
    def __str__(self):
        return f"{self.entry_type}: {self.polymer_system} - {self.force_field}"
    
    def get_property_value(self, property_name):
        """Get the value of a specific property"""
        property_mapping = {
            'polymer_system': self.polymer_system,
            'force_field': self.force_field,
            'Density (g/cm³)': self.density,
            'Glass Transition Temperature (K)': self.glass_transition_temp,
            'Radius of Gyration (nm)': self.radius_of_gyration,
            'Young\'s Modulus (GPa)': self.youngs_modulus,
            'Diffusion Coefficient (m²/s)': self.diffusion_coefficient,
            'Viscosity (Pa s)': self.viscosity,
        }
        return property_mapping.get(property_name, 'NA')
    
    @property
    def density_value(self):
        return self.density or 'NA'
    
    @property
    def glass_transition_temp_value(self):
        return self.glass_transition_temp or 'NA'
    
    @property
    def radius_of_gyration_value(self):
        return self.radius_of_gyration or 'NA'
    
    @property
    def youngs_modulus_value(self):
        return self.youngs_modulus or 'NA'
    
    @property
    def diffusion_coefficient_value(self):
        return self.diffusion_coefficient or 'NA'
    
    @property
    def viscosity_value(self):
        return self.viscosity or 'NA'

class MatchedPair(models.Model):
    """Model to store manually matched ground truth and predicted pairs"""
    ground_truth = models.ForeignKey(DataEntry, on_delete=models.CASCADE, related_name='gt_pairs')
    predicted = models.ForeignKey(DataEntry, on_delete=models.CASCADE, related_name='pred_pairs')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['ground_truth', 'predicted']
    
    def __str__(self):
        return f"GT: {self.ground_truth.polymer_system} - Pred: {self.predicted.polymer_system}"

class Classification(models.Model):
    """Model to store TP/FP/TN/FN classifications for each property"""
    CLASSIFICATION_CHOICES = [
        ('TP', 'True Positive'),
        ('FP', 'False Positive'),
        ('TN', 'True Negative'),
        ('FN', 'False Negative'),
    ]
    
    matched_pair = models.ForeignKey(MatchedPair, on_delete=models.CASCADE, related_name='classifications')
    property_name = models.CharField(max_length=100)
    classification = models.CharField(max_length=2, choices=CLASSIFICATION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['matched_pair', 'property_name']
    
    def __str__(self):
        return f"{self.matched_pair} - {self.property_name}: {self.classification}"

class EvaluationSession(models.Model):
    """Model to track evaluation sessions"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def get_statistics(self):
        """Get TP/FP/TN/FN statistics for this session"""
        classifications = Classification.objects.filter(matched_pair__in=self.matchedpair_set.all())
        stats = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}
        
        for classification in classifications:
            stats[classification.classification] += 1
        
        return stats
