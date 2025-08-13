from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from .models import DataEntry, MatchedPair, Classification, EvaluationSession
from .forms import JSONFileUploadForm, EvaluationSessionForm, ClassificationForm

# Helper functions for automatic comparison
def is_numeric(value):
    """Check if a value is numeric"""
    if value is None or value == 'NA':
        return False
    
    # Handle ranges like "600-700"
    if isinstance(value, str) and '-' in value and not value.startswith('-'):
        parts = value.split('-')
        if len(parts) == 2:
            try:
                float(parts[0].strip())
                float(parts[1].strip())
                return True
            except ValueError:
                pass
    
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def parse_range(value):
    """Parse a range value like '600-700' and return (min, max)"""
    if isinstance(value, str) and '-' in value and not value.startswith('-'):
        parts = value.split('-')
        if len(parts) == 2:
            try:
                return (float(parts[0].strip()), float(parts[1].strip()))
            except ValueError:
                pass
    return None

def calculate_range_overlap(range1, range2):
    """Calculate overlap percentage between two ranges"""
    if not range1 or not range2:
        return 0
    
    min1, max1 = range1
    min2, max2 = range2
    
    overlap_start = max(min1, min2)
    overlap_end = min(max1, max2)
    
    if overlap_start >= overlap_end:
        return 0
    
    overlap_length = overlap_end - overlap_start
    range1_length = max1 - min1
    range2_length = max2 - min2
    
    # Calculate overlap percentage based on the smaller range
    smaller_range = min(range1_length, range2_length)
    if smaller_range == 0:
        return 0
    
    return (overlap_length / smaller_range) * 100

def within_tolerance(gt_value, pred_value, tolerance_percent=5):
    """Check if values are within tolerance or range overlap"""
    if gt_value == pred_value:
        return True
    
    # Handle NA cases
    if gt_value == 'NA' or pred_value == 'NA':
        return False
    
    # Check if both are numeric
    if is_numeric(gt_value) and is_numeric(pred_value):
        # Handle ranges
        gt_range = parse_range(gt_value)
        pred_range = parse_range(pred_value)
        
        if gt_range and pred_range:
            # Both are ranges - check 80% overlap
            overlap = calculate_range_overlap(gt_range, pred_range)
            return overlap >= 80
        
        elif gt_range:
            # GT is range, pred is single value
            try:
                pred_float = float(pred_value)
                return gt_range[0] <= pred_float <= gt_range[1]
            except ValueError:
                return False
        
        elif pred_range:
            # Pred is range, GT is single value
            try:
                gt_float = float(gt_value)
                return pred_range[0] <= gt_float <= pred_range[1]
            except ValueError:
                return False
        
        else:
            # Both are single numeric values - check ±5% tolerance
            try:
                gt_float = float(gt_value)
                pred_float = float(pred_value)
                diff = abs(gt_float - pred_float)
                return diff <= (gt_float * tolerance_percent / 100)
            except ValueError:
                return False
    
    return False

def perform_automatic_comparison(pair, property_name):
    """Perform automatic comparison and return classification"""
    gt_value = pair.ground_truth.get_property_value(property_name)
    pred_value = pair.predicted.get_property_value(property_name)
    
    # Handle NA cases - these are always clear
    gt_is_na = gt_value == 'NA' or gt_value is None
    pred_is_na = pred_value == 'NA' or pred_value is None
    
    if gt_is_na and pred_is_na:
        return 'TN'  # True Negative
    if gt_is_na and not pred_is_na:
        return 'FP'  # False Positive
    if not gt_is_na and pred_is_na:
        return 'FN'  # False Negative
    
    # For string-based properties (polymer_system, force_field), only classify exact matches
    if property_name in ['polymer_system', 'force_field']:
        if gt_value == pred_value:
            return 'TP'  # True Positive - exact match
        else:
            return None  # Ambiguous - needs human judgment
    
    # For numeric properties, check tolerance
    if within_tolerance(gt_value, pred_value):
        return 'TP'  # True Positive
    else:
        return 'FN'  # False Negative

def create_automatic_classifications(pair):
    """Create automatic classifications for all properties of a pair"""
    properties = [
        'polymer_system',
        'force_field',
        'Density (g/cm³)',
        'Glass Transition Temperature (K)',
        'Radius of Gyration (nm)',
        'Young\'s Modulus (GPa)',
        'Diffusion Coefficient (m²/s)',
        'Viscosity (Pa s)'
    ]
    
    for prop in properties:
        # Only create if classification doesn't exist
        if not Classification.objects.filter(matched_pair=pair, property_name=prop).exists():
            classification = perform_automatic_comparison(pair, prop)
            if classification:  # Only create if we got a valid classification
                Classification.objects.create(
                    matched_pair=pair,
                    property_name=prop,
                    classification=classification
                )

def index(request):
    """Home page with data upload and session management"""
    if request.method == 'POST':
        form = JSONFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check if user wants to replace existing data
                    replace_existing = form.cleaned_data.get('replace_existing', False)
                    
                    if replace_existing:
                        # Clear existing data and related objects
                        Classification.objects.all().delete()
                        MatchedPair.objects.all().delete()
                        DataEntry.objects.all().delete()
                        messages.info(request, 'Replaced all existing data.')
                    else:
                        messages.info(request, 'Updating existing data entries.')
                    
                    # Load ground truth data
                    gt_data = form.cleaned_data['ground_truth_file']
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
                    
                    # Load predicted data
                    pred_data = form.cleaned_data['predicted_file']
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
                
                messages.success(request, f'Successfully loaded {len(gt_data)} ground truth and {len(pred_data)} predicted entries.')
                return redirect('matching')
                
            except Exception as e:
                messages.error(request, f'Error loading data: {str(e)}')
    else:
        form = JSONFileUploadForm()
    
    # Get existing sessions
    sessions = EvaluationSession.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'sessions': sessions,
        'gt_count': DataEntry.objects.filter(entry_type='ground_truth').count(),
        'pred_count': DataEntry.objects.filter(entry_type='predicted').count(),
    }
    return render(request, 'evaluation_app/index.html', context)

def matching(request):
    """Manual pair matching interface"""
    # Get all matched pairs to identify which entries are already matched
    matched_pairs = MatchedPair.objects.all().order_by('-created_at')
    
    # Get IDs of entries that are already matched
    matched_gt_ids = set(matched_pairs.values_list('ground_truth_id', flat=True))
    matched_pred_ids = set(matched_pairs.values_list('predicted_id', flat=True))
    
    # Only show unmatched entries that are not marked as "no match"
    ground_truth_entries = DataEntry.objects.filter(
        entry_type='ground_truth',
        marked_no_match=False
    ).exclude(
        id__in=matched_gt_ids
    ).order_by('polymer_system', 'force_field')
    
    predicted_entries = DataEntry.objects.filter(
        entry_type='predicted',
        marked_no_match=False
    ).exclude(
        id__in=matched_pred_ids
    ).order_by('polymer_system', 'force_field')
    
    context = {
        'ground_truth_entries': ground_truth_entries,
        'predicted_entries': predicted_entries,
        'matched_pairs': matched_pairs,
        'matched_gt_ids': matched_gt_ids,
        'matched_pred_ids': matched_pred_ids,
    }
    return render(request, 'evaluation_app/matching.html', context)

@require_http_methods(["POST"])
def create_pair(request):
    """AJAX endpoint to create a matched pair"""
    try:
        data = json.loads(request.body)
        gt_id = data.get('ground_truth_id')
        pred_id = data.get('predicted_id')
        
        if not gt_id or not pred_id:
            return JsonResponse({'error': 'Missing ground truth or predicted ID'}, status=400)
        
        ground_truth = get_object_or_404(DataEntry, id=gt_id, entry_type='ground_truth')
        predicted = get_object_or_404(DataEntry, id=pred_id, entry_type='predicted')
        
        # Check if pair already exists
        if MatchedPair.objects.filter(ground_truth=ground_truth, predicted=predicted).exists():
            return JsonResponse({'error': 'Pair already exists'}, status=400)
        
        pair = MatchedPair.objects.create(ground_truth=ground_truth, predicted=predicted)
        
        # Automatically create classifications for this pair
        create_automatic_classifications(pair)
        
        return JsonResponse({
            'success': True,
            'pair_id': pair.id,
            'message': f'Created pair: {ground_truth.polymer_system} ↔ {predicted.polymer_system}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def delete_pair(request):
    """AJAX endpoint to delete a matched pair"""
    try:
        data = json.loads(request.body)
        pair_id = data.get('pair_id')
        
        if not pair_id:
            return JsonResponse({'error': 'Missing pair ID'}, status=400)
        
        pair = get_object_or_404(MatchedPair, id=pair_id)
        pair.delete()
        
        return JsonResponse({'success': True, 'message': 'Pair deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def delete_entry(request):
    """AJAX endpoint to delete a data entry"""
    try:
        data = json.loads(request.body)
        entry_id = data.get('entry_id')
        
        if not entry_id:
            return JsonResponse({'error': 'Missing entry ID'}, status=400)
        
        entry = get_object_or_404(DataEntry, id=entry_id)
        
        # Check if this entry is part of any matched pairs
        if entry.entry_type == 'ground_truth':
            related_pairs = MatchedPair.objects.filter(ground_truth=entry)
        else:
            related_pairs = MatchedPair.objects.filter(predicted=entry)
        
        if related_pairs.exists():
            # Delete related classifications and pairs
            for pair in related_pairs:
                Classification.objects.filter(matched_pair=pair).delete()
            related_pairs.delete()
        
        # Delete the entry
        entry.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Deleted {entry.entry_type} entry: {entry.polymer_system}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def mark_no_match(request):
    """AJAX endpoint to mark an entry as 'no match'"""
    try:
        data = json.loads(request.body)
        entry_id = data.get('entry_id')
        
        if not entry_id:
            return JsonResponse({'error': 'Missing entry ID'}, status=400)
        
        entry = get_object_or_404(DataEntry, id=entry_id)
        entry.marked_no_match = True
        entry.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Marked {entry.entry_type} entry as "no match": {entry.polymer_system}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def clear_all_data(request):
    """AJAX endpoint to clear all data"""
    try:
        with transaction.atomic():
            # Delete all data in the correct order to avoid foreign key constraints
            Classification.objects.all().delete()
            MatchedPair.objects.all().delete()
            DataEntry.objects.all().delete()
            
        return JsonResponse({
            'success': True,
            'message': 'All data cleared successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def evaluation(request):
    """Evaluation interface for classifying TP/FP/TN/FN with automatic comparison"""
    matched_pairs = MatchedPair.objects.all().order_by('-created_at')
    
    if not matched_pairs.exists():
        messages.warning(request, 'No matched pairs found. Please create pairs first.')
        return redirect('matching')
    
    # Automatically create classifications for any pairs that don't have them
    for pair in matched_pairs:
        create_automatic_classifications(pair)
    
    # Get properties list
    properties = [
        'polymer_system',
        'force_field',
        'Density (g/cm³)',
        'Glass Transition Temperature (K)',
        'Radius of Gyration (nm)',
        'Young\'s Modulus (GPa)',
        'Diffusion Coefficient (m²/s)',
        'Viscosity (Pa s)'
    ]
    
    # Get existing classifications
    classifications = {}
    for pair in matched_pairs:
        classifications[pair.id] = {}
        for prop in properties:
            try:
                classification = Classification.objects.get(matched_pair=pair, property_name=prop)
                classifications[pair.id][prop] = classification.classification
            except Classification.DoesNotExist:
                classifications[pair.id][prop] = None
    
    context = {
        'matched_pairs': matched_pairs,
        'properties': properties,
        'classifications': classifications,
    }
    return render(request, 'evaluation_app/evaluation.html', context)

@require_http_methods(["POST"])
def save_classification(request):
    """AJAX endpoint to save a classification"""
    try:
        data = json.loads(request.body)
        pair_id = data.get('pair_id')
        property_name = data.get('property_name')
        classification = data.get('classification')
        
        if not all([pair_id, property_name, classification]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        if classification not in ['TP', 'FP', 'TN', 'FN']:
            return JsonResponse({'error': 'Invalid classification'}, status=400)
        
        pair = get_object_or_404(MatchedPair, id=pair_id)
        
        # Update or create classification
        classification_obj, created = Classification.objects.update_or_create(
            matched_pair=pair,
            property_name=property_name,
            defaults={'classification': classification}
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Saved {classification} for {property_name}',
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def statistics(request):
    """Statistics and metrics page"""
    matched_pairs = MatchedPair.objects.all()
    classifications = Classification.objects.all()
    
    # Calculate statistics
    stats = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}
    for classification in classifications:
        stats[classification.classification] += 1
    
    total = sum(stats.values())
    precision = stats['TP'] / (stats['TP'] + stats['FP']) if (stats['TP'] + stats['FP']) > 0 else 0
    recall = stats['TP'] / (stats['TP'] + stats['FN']) if (stats['TP'] + stats['FN']) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (stats['TP'] + stats['TN']) / total if total > 0 else 0
    
    context = {
        'stats': stats,
        'total': total,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy,
        'matched_pairs_count': matched_pairs.count(),
    }
    return render(request, 'evaluation_app/statistics.html', context)

def export_results(request):
    """Export results as JSON"""
    matched_pairs = MatchedPair.objects.all()
    classifications = Classification.objects.all()
    
    results = {
        'summary': {
            'total_pairs': matched_pairs.count(),
            'total_classifications': classifications.count(),
            'statistics': {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}
        },
        'detailed_results': []
    }
    
    # Calculate statistics
    for classification in classifications:
        results['summary']['statistics'][classification.classification] += 1
    
    # Detailed results
    for pair in matched_pairs:
        pair_data = {
            'pair_id': pair.id,
            'ground_truth': {
                'polymer_system': pair.ground_truth.polymer_system,
                'force_field': pair.ground_truth.force_field,
                'properties': {
                    'polymer_system': pair.ground_truth.polymer_system,
                    'force_field': pair.ground_truth.force_field,
                    'Density (g/cm³)': pair.ground_truth.density,
                    'Glass Transition Temperature (K)': pair.ground_truth.glass_transition_temp,
                    'Radius of Gyration (nm)': pair.ground_truth.radius_of_gyration,
                    'Young\'s Modulus (GPa)': pair.ground_truth.youngs_modulus,
                    'Diffusion Coefficient (m²/s)': pair.ground_truth.diffusion_coefficient,
                    'Viscosity (Pa s)': pair.ground_truth.viscosity,
                }
            },
            'prediction': {
                'polymer_system': pair.predicted.polymer_system,
                'force_field': pair.predicted.force_field,
                'properties': {
                    'polymer_system': pair.predicted.polymer_system,
                    'force_field': pair.predicted.force_field,
                    'Density (g/cm³)': pair.predicted.density,
                    'Glass Transition Temperature (K)': pair.predicted.glass_transition_temp,
                    'Radius of Gyration (nm)': pair.predicted.radius_of_gyration,
                    'Young\'s Modulus (GPa)': pair.predicted.youngs_modulus,
                    'Diffusion Coefficient (m²/s)': pair.predicted.diffusion_coefficient,
                    'Viscosity (Pa s)': pair.predicted.viscosity,
                }
            },
            'classifications': {}
        }
        
        # Add classifications for this pair
        for classification in pair.classifications.all():
            pair_data['classifications'][classification.property_name] = classification.classification
        
        results['detailed_results'].append(pair_data)
    
    response = HttpResponse(
        json.dumps(results, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="evaluation_results.json"'
    return response
