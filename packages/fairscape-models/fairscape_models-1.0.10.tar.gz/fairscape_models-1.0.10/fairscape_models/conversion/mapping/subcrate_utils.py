from typing import Any, Dict, List, Optional, Set
from fairscape_models.conversion.models.FairscapeDatasheet import CompositionDetails
from collections import Counter

def build_composition_details(converter_instance, source_entity_model) -> CompositionDetails:
    """
    Walk the subcrate graph once, normalize @type, and fill in counts,
    formats, access summaries, patterns, inputs, and domain summaries.
    """
    graph = converter_instance.source_crate.metadataGraph
    global_index = converter_instance.global_index
    
    details = CompositionDetails()
    
    # Collections for aggregation
    file_formats = []
    software_formats = []
    file_access_types = []
    software_access_types = []
    computation_patterns = []
    experiment_patterns = []
    cell_lines = {}
    species_counts = Counter()
    experiment_types_counts = Counter()
    
    # Single pass through the graph
    for item in graph:
        if item.guid == "ro-crate-metadata.json":
            continue
            
        # Skip subcrates
        if hasattr(item, 'ro_crate_metadata'):
            continue
            
        item_type = _normalize_type(item)
        
        if item_type == "Dataset":
            details.files_count += 1
            _process_dataset(item, file_formats, file_access_types)
            
        elif item_type == "Software":
            details.software_count += 1
            _process_software(item, software_formats, software_access_types)
            
        elif item_type == "Instrument":
            details.instruments_count += 1
            
        elif item_type == "Sample":
            details.samples_count += 1
            _process_sample(item, cell_lines, species_counts, global_index)
            
        elif item_type == "Experiment":
            details.experiments_count += 1
            pattern = _extract_experiment_pattern(item, global_index)
            if pattern:
                experiment_patterns.append(pattern)
            _process_experiment_type(item, experiment_types_counts)
            
        elif item_type == "Computation":
            details.computations_count += 1
            pattern = _extract_computation_pattern(item, global_index)
            if pattern:
                computation_patterns.append(pattern)
                
        elif item_type == "Schema":
            details.schemas_count += 1
            
        else:
            details.other_count += 1
    
    # Aggregate results
    details.file_formats = dict(Counter(file_formats))
    details.software_formats = dict(Counter(software_formats))
    details.file_access = dict(Counter(file_access_types))
    details.software_access = dict(Counter(software_access_types))
    details.computation_patterns = list(set(computation_patterns))
    details.experiment_patterns = list(set(experiment_patterns))
    details.cell_lines = list(cell_lines.values())
    details.species = [f"{species} ({count})" for species, count in species_counts.items()]
    details.experiment_types = [f"{exp_type} ({count})" for exp_type, count in experiment_types_counts.items()]
    
    # Calculate input datasets from computation patterns
    input_dataset_counts = _calculate_input_datasets(graph[1], global_index)
    details.input_datasets = input_dataset_counts
    details.input_datasets_count = sum(input_dataset_counts.values())
    details.inputs_count = details.samples_count + details.input_datasets_count
    
    return details


def _normalize_type(item) -> str:
    """Normalize the @type field to a simple string."""
    type_field = getattr(item, 'metadataType', None) or getattr(item, '@type', None)
    
    if not type_field:
        return "Other"
    
    if isinstance(type_field, list):
        type_str = " ".join(type_field)
    else:
        type_str = str(type_field)
    
    # Check for specific types
    if "Dataset" in type_str or "EVI:Dataset" in type_str or "https://w3id.org/EVI#Dataset" in type_str:
        return "Dataset"
    elif "Software" in type_str or "EVI:Software" in type_str or "https://w3id.org/EVI#Software" in type_str or "SoftwareSourceCode" in type_str:
        return "Software"
    elif "Instrument" in type_str or "https://w3id.org/EVI#Instrument" in type_str or "EVI:Instrument" in type_str:
        return "Instrument"
    elif "Sample" in type_str or "https://w3id.org/EVI#Sample" in type_str or "EVI:Sample" in type_str:
        return "Sample"
    elif "Experiment" in type_str or "https://w3id.org/EVI#Experiment" in type_str or "EVI:Experiment" in type_str:
        return "Experiment"
    elif "Computation" in type_str or "https://w3id.org/EVI#Computation" in type_str or "EVI:Computation" in type_str:
        return "Computation"
    elif "Schema" in type_str or "EVI:Schema" in type_str or "https://w3id.org/EVI#Schema" in type_str:
        return "Schema"
    else:
        return "Other"


def _process_dataset(item, formats: List[str], access_types: List[str]):
    """Process dataset item for format and access information."""
    format_val = getattr(item, 'fileFormat', 'unknown')
    formats.append(format_val)
    
    content_url = getattr(item, 'contentUrl', '')
    if not content_url:
        access_types.append("No link")
    elif content_url == "Embargoed":
        access_types.append("Embargoed")
    else:
        access_types.append("Available")


def _process_software(item, formats: List[str], access_types: List[str]):
    """Process software item for format and access information."""
    format_val = getattr(item, 'fileFormat', 'unknown')
    formats.append(format_val)
    
    content_url = getattr(item, 'contentUrl', '')
    if not content_url:
        access_types.append("No link")
    elif content_url == "Embargoed":
        access_types.append("Embargoed")
    else:
        access_types.append("Available")


def _process_sample(item, cell_lines: Dict[str, str], species_counts: Counter, global_index: Dict[str, Any]):
    """Process sample for cell line and species information."""
    # Check for cell line reference
    cell_line_ref = getattr(item, 'cellLineReference', None) or getattr(item, 'derivedFrom', None)
    if cell_line_ref:  
        if hasattr(cell_line_ref, 'guid'):
            ref_id = cell_line_ref.guid
        else:
            ref_id = cell_line_ref.get("@id","")
        cell_line_details = global_index.get(ref_id, {})
        if ref_id not in cell_lines:
            cell_lines[ref_id] = cell_line_details.get('name', ref_id)
            
    scientific_name = "Unknown"
    if cell_line_details.get("organism",{}).get("name",""):
        scientific_name = cell_line_details["organism"]["name"]

    species_counts[scientific_name] += 1


def _process_experiment_type(item, experiment_types_counts: Counter):
    """Extract and count experiment types."""
    exp_type = getattr(item, 'experimentType', 'Unknown')
    experiment_types_counts[exp_type] += 1


def _extract_experiment_pattern(item, global_index: Dict[str, Any]) -> Optional[str]:
    """Extract transformation pattern for experiments (Sample → outputs)."""
    output_formats = []
    
    generated = getattr(item, 'generated', [])
    if generated:
        if not isinstance(generated, list):
            generated = [generated]
            
        for dataset_ref in generated:
            dataset_id = _get_ref_id(dataset_ref)
            if dataset_id:
                format_val = _lookup_format(dataset_id, global_index)
                if format_val and format_val != "unknown":
                    output_formats.append(format_val)
    
    if output_formats:
        output_str = ", ".join(sorted(set(output_formats)))
        return f"Sample → {output_str}"
    
    return None


def _extract_computation_pattern(item, global_index: Dict[str, Any]) -> Optional[str]:
    """Extract transformation pattern for computations (inputs → outputs)."""
    input_formats = []
    output_formats = []
    # Get input datasets
    used_datasets = getattr(item, 'usedDataset', [])
    if used_datasets:
        if not isinstance(used_datasets, list):
            used_datasets = [used_datasets]
            
        for dataset_ref in used_datasets:
            dataset_id = _get_ref_id(dataset_ref)
            if dataset_id:
                format_val = _lookup_format(dataset_id, global_index)
                if format_val and format_val != "unknown":
                    input_formats.append(format_val)
    
    # Get output datasets
    generated = getattr(item, 'generated', [])
    if generated:
        if not isinstance(generated, list):
            generated = [generated]
            
        for dataset_ref in generated:
            dataset_id = _get_ref_id(dataset_ref)
            if dataset_id:
                format_val = _lookup_format(dataset_id, global_index)
                if format_val and format_val != "unknown":
                    output_formats.append(format_val)
    
    if input_formats and output_formats:
        input_str = ", ".join(sorted(set(input_formats)))
        output_str = ", ".join(sorted(set(output_formats)))
        return f"{input_str} → {output_str}"
    
    return None


def _get_ref_id(ref) -> Optional[str]:
    """Extract ID from a reference (dict with @id or guid, or string)."""
    if isinstance(ref, dict):
        return ref.get('@id') or ref.get('guid')
    elif isinstance(ref, str):
        return ref
    elif hasattr(ref, 'guid'):
        return ref.guid
    return None


def _lookup_format(dataset_id: str, global_index: Dict[str, Any]) -> str:
    """Lookup format for a dataset ID in the global index."""
    if dataset_id in global_index:
        entity_info = global_index[dataset_id]
        return entity_info.get('fileFormat', 'unknown')
    return 'unknown'


def _calculate_input_datasets(root_dataset, global_index: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate input dataset counts from EVI:inputs field.
    Looks up each input reference in the global index and aggregates by format.
    If an input has a rocrateName attribute, includes it in the format key.
    If an input is itself an RO-Crate, uses its outputs instead.
    """
    input_counts = Counter()
    
    evi_inputs = getattr(root_dataset, 'EVI:inputs', None) or getattr(root_dataset, 'https://w3id.org/EVI#inputs', None) or getattr(root_dataset, 'inputs', None)
    
    if not isinstance(evi_inputs, list):
        evi_inputs = [evi_inputs]
    
    for input_ref in evi_inputs:
        input_id = _get_ref_id(input_ref)
        if not input_id:
            continue
        
        if input_id in global_index:
            entity_info = global_index[input_id]
            
            entity_type = entity_info.get('@type', entity_info.get('metadataType', ''))
            is_rocrate = False
            if isinstance(entity_type, list):
                is_rocrate = any('ROCrate' in str(t) for t in entity_type)
            else:
                is_rocrate = 'ROCrate' in str(entity_type)
            
            if is_rocrate:
                outputs = entity_info.get('https://w3id.org/EVI#outputs', entity_info.get('EVI:outputs', entity_info.get('outputs', [])))
                if not isinstance(outputs, list):
                    outputs = [outputs] if outputs else []
                
                rocrate_name = entity_info.get('name', 'Unknown RO-Crate')
                
                for output_ref in outputs:
                    output_id = _get_ref_id(output_ref)
                    if output_id and output_id in global_index:
                        output_info = global_index[output_id]
                        format_val = output_info.get('fileFormat', 'unknown')
                        key = f"{rocrate_name} ({format_val})"
                        input_counts[key] += 1
            else:
                
                format_val = entity_info.get('fileFormat', 'unknown')
                if format_val == 'unknown':
                    format_val = 'Sample'
                    
                
                rocrate_name = entity_info.get('rocrateName', '')
                
                if rocrate_name and rocrate_name != root_dataset.name:
                    key = f"{rocrate_name} ({format_val})"
                else:
                    key = format_val
                
                input_counts[key] += 1
        else:
            input_counts['unknown'] += 1
    
    return dict(input_counts)