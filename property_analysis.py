#!/usr/bin/env python
import os
import django
from django.db.models import Count, Q

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polymer_evaluation.settings')
django.setup()

from evaluation_app.models import Classification, MatchedPair, DataEntry

def calculate_metrics(tp, fp, tn, fn):
    """Calculate precision, recall, F1 score, and accuracy"""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0
    
    return {
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1_score, 4),
        'accuracy': round(accuracy, 4)
    }

def analyze_property_metrics():
    """Comprehensive property-wise analysis"""
    print("=" * 80)
    print("PROPERTY-WISE CLASSIFICATION ANALYSIS")
    print("=" * 80)
    
    # Check if we have any data
    total_classifications = Classification.objects.count()
    total_pairs = MatchedPair.objects.count()
    total_gt = DataEntry.objects.filter(entry_type='ground_truth').count()
    total_pred = DataEntry.objects.filter(entry_type='predicted').count()
    
    print(f"\nDATABASE OVERVIEW:")
    print(f"- Total Classifications: {total_classifications}")
    print(f"- Total Matched Pairs: {total_pairs}")
    print(f"- Ground Truth Entries: {total_gt}")
    print(f"- Predicted Entries: {total_pred}")
    
    if total_classifications == 0:
        print("\n❌ No classifications found in database!")
        print("Please create some matched pairs and classifications first.")
        return
    
    print("\n" + "=" * 80)
    print("PROPERTY-WISE BREAKDOWN")
    print("=" * 80)
    
    # Get property-wise metrics
    property_metrics = Classification.objects.values('property_name').annotate(
        tp_count=Count('classification', filter=Q(classification='TP')),
        fp_count=Count('classification', filter=Q(classification='FP')),
        tn_count=Count('classification', filter=Q(classification='TN')),
        fn_count=Count('classification', filter=Q(classification='FN')),
        total_count=Count('classification')
    ).order_by('property_name')
    
    # Calculate overall totals
    overall_tp = 0
    overall_fp = 0
    overall_tn = 0
    overall_fn = 0
    
    # Process each property
    for metric in property_metrics:
        property_name = metric['property_name']
        tp = metric['tp_count']
        fp = metric['fp_count']
        tn = metric['tn_count']
        fn = metric['fn_count']
        total = metric['total_count']
        
        # Add to overall totals
        overall_tp += tp
        overall_fp += fp
        overall_tn += tn
        overall_fn += fn
        
        # Calculate metrics
        metrics = calculate_metrics(tp, fp, tn, fn)
        
        print(f"\n🔍 {property_name}")
        print("-" * 50)
        print(f"Counts:")
        print(f"  TP: {tp:3d} | FP: {fp:3d} | TN: {tn:3d} | FN: {fn:3d} | Total: {total:3d}")
        print(f"Metrics:")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1_score']:.4f}")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        
        # Add some interpretation
        if metrics['f1_score'] >= 0.8:
            performance = "🟢 Excellent"
        elif metrics['f1_score'] >= 0.6:
            performance = "🟡 Good"
        elif metrics['f1_score'] >= 0.4:
            performance = "🟠 Fair"
        else:
            performance = "🔴 Poor"
        
        print(f"Performance: {performance}")
    
    # Overall metrics
    print("\n" + "=" * 80)
    print("OVERALL METRICS (ALL PROPERTIES COMBINED)")
    print("=" * 80)
    
    overall_metrics = calculate_metrics(overall_tp, overall_fp, overall_tn, overall_fn)
    overall_total = overall_tp + overall_fp + overall_tn + overall_fn
    
    print(f"Total Counts:")
    print(f"  TP: {overall_tp:3d} | FP: {overall_fp:3d} | TN: {overall_tn:3d} | FN: {overall_fn:3d} | Total: {overall_total:3d}")
    print(f"Overall Metrics:")
    print(f"  Precision: {overall_metrics['precision']:.4f}")
    print(f"  Recall:    {overall_metrics['recall']:.4f}")
    print(f"  F1 Score:  {overall_metrics['f1_score']:.4f}")
    print(f"  Accuracy:  {overall_metrics['accuracy']:.4f}")
    
    # Classification distribution
    print("\n" + "=" * 80)
    print("CLASSIFICATION DISTRIBUTION")
    print("=" * 80)
    
    classification_dist = Classification.objects.values('classification').annotate(
        count=Count('id')
    ).order_by('classification')
    
    for cls in classification_dist:
        percentage = (cls['count'] / total_classifications) * 100
        print(f"{cls['classification']}: {cls['count']:3d} ({percentage:5.1f}%)")
    
    # Property distribution
    print("\n" + "=" * 80)
    print("PROPERTY DISTRIBUTION")
    print("=" * 80)
    
    property_dist = Classification.objects.values('property_name').annotate(
        count=Count('id')
    ).order_by('property_name')
    
    for prop in property_dist:
        percentage = (prop['count'] / total_classifications) * 100
        print(f"{prop['property_name']}: {prop['count']:3d} ({percentage:5.1f}%)")
    
    # Detailed breakdown by property and classification
    print("\n" + "=" * 80)
    print("DETAILED BREAKDOWN BY PROPERTY AND CLASSIFICATION")
    print("=" * 80)
    
    detailed_breakdown = Classification.objects.values('property_name', 'classification').annotate(
        count=Count('id')
    ).order_by('property_name', 'classification')
    
    current_property = None
    for item in detailed_breakdown:
        if current_property != item['property_name']:
            current_property = item['property_name']
            print(f"\n{current_property}:")
        
        print(f"  {item['classification']}: {item['count']:3d}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

def export_results():
    """Export results to a structured format"""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    # Get all the data
    property_metrics = Classification.objects.values('property_name').annotate(
        tp_count=Count('classification', filter=Q(classification='TP')),
        fp_count=Count('classification', filter=Q(classification='FP')),
        tn_count=Count('classification', filter=Q(classification='TN')),
        fn_count=Count('classification', filter=Q(classification='FN')),
        total_count=Count('classification')
    ).order_by('property_name')
    
    results = {
        'summary': {
            'total_classifications': Classification.objects.count(),
            'total_pairs': MatchedPair.objects.count(),
            'total_gt_entries': DataEntry.objects.filter(entry_type='ground_truth').count(),
            'total_pred_entries': DataEntry.objects.filter(entry_type='predicted').count(),
        },
        'property_metrics': {}
    }
    
    # Calculate overall totals
    overall_tp = 0
    overall_fp = 0
    overall_tn = 0
    overall_fn = 0
    
    for metric in property_metrics:
        property_name = metric['property_name']
        tp = metric['tp_count']
        fp = metric['fp_count']
        tn = metric['tn_count']
        fn = metric['fn_count']
        total = metric['total_count']
        
        # Add to overall totals
        overall_tp += tp
        overall_fp += fp
        overall_tn += tn
        overall_fn += fn
        
        # Calculate metrics
        metrics = calculate_metrics(tp, fp, tn, fn)
        
        results['property_metrics'][property_name] = {
            'counts': {
                'TP': tp,
                'FP': fp,
                'TN': tn,
                'FN': fn,
                'Total': total
            },
            'metrics': metrics
        }
    
    # Add overall metrics
    overall_metrics = calculate_metrics(overall_tp, overall_fp, overall_tn, overall_fn)
    results['overall_metrics'] = {
        'counts': {
            'TP': overall_tp,
            'FP': overall_fp,
            'TN': overall_tn,
            'FN': overall_fn,
            'Total': overall_tp + overall_fp + overall_tn + overall_fn
        },
        'metrics': overall_metrics
    }
    
    print("Results exported successfully!")
    print("You can access the 'results' variable for further processing.")
    
    return results

if __name__ == "__main__":
    # Run the analysis
    analyze_property_metrics()
    
    # Export results
    results = export_results()
    
    # Print a summary
    print(f"\n📋 SUMMARY:")
    print(f"Analyzed {results['summary']['total_classifications']} classifications")
    print(f"Across {len(results['property_metrics'])} properties")
    print(f"From {results['summary']['total_pairs']} matched pairs")
    
    # Show best performing property
    if results['property_metrics']:
        best_property = max(results['property_metrics'].items(), 
                           key=lambda x: x[1]['metrics']['f1_score'])
        print(f"Best performing property: {best_property[0]} (F1: {best_property[1]['metrics']['f1_score']:.4f})") 