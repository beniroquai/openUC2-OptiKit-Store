#!/usr/bin/env python3
"""
Script to analyze UC2 setup JSON files and create a CSV database.

This script scans all JSON files in the ./setups folder and extracts:
- Setup metadata (name, uc2_verified, collection, author, github_link)  
- Component usage counts by filename

Output: CSV file with setup information and component analysis
"""

import json
import pandas as pd
import os
from pathlib import Path
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(filepath):
    """
    Load and parse a JSON file safely.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        dict or None: Parsed JSON data or None if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return None

def extract_setup_metadata(data, filename):
    """
    Extract metadata from setup JSON data.
    
    Args:
        data (dict): Parsed JSON data
        filename (str): Name of the JSON file
        
    Returns:
        dict: Extracted metadata
    """
    metadata = {
        'filename': filename,
        'name': data.get('name', ''),
        'uc2_verified': data.get('uc2_verified', False),
        'collection': data.get('collection', ''),
        'author': data.get('author', ''),
        'github_link': data.get('github_link', ''),
        'description': data.get('description', ''),
        'category': data.get('category', ''),
        'version': data.get('version', ''),
        'createdAt': data.get('createdAt', ''),
        'total_components': 0
    }
    
    return metadata

def count_components_by_file(uc2_components):
    """
    Count UC2 components by their file names.
    
    Args:
        uc2_components (list): List of UC2 component dictionaries
        
    Returns:
        dict: Counter of component files
    """
    if not uc2_components:
        return {}
    
    # Extract file names from components
    component_files = []
    for component in uc2_components:
        if isinstance(component, dict) and 'file' in component:
            # Clean up file path to get just the filename
            file_path = component['file']
            if file_path:
                # Extract filename from path (handle Windows and Unix paths)
                filename = os.path.basename(file_path)
                component_files.append(filename)
    
    return dict(Counter(component_files))

def analyze_setups_folder(setups_folder='./setups'):
    """
    Analyze all JSON files in the setups folder.
    
    Args:
        setups_folder (str): Path to setups folder
        
    Returns:
        tuple: (setup_data_list, all_component_files)
    """
    setups_path = Path(setups_folder)
    
    if not setups_path.exists():
        logger.error(f"Setups folder not found: {setups_folder}")
        return [], set()
    
    json_files = list(setups_path.glob('*.json'))
    logger.info(f"Found {len(json_files)} JSON files in {setups_folder}")
    
    setup_data_list = []
    all_component_files = set()
    
    for json_file in json_files:
        logger.info(f"Processing: {json_file.name}")
        
        # Load JSON data
        data = load_json_file(json_file)
        if data is None:
            continue
        
        # Extract setup metadata
        setup_metadata = extract_setup_metadata(data, json_file.name)
        
        # Get UC2 components
        uc2_components = data.get('uc2_components', [])
        setup_metadata['total_components'] = len(uc2_components)
        
        # Count components by file
        component_counts = count_components_by_file(uc2_components)
        
        # Keep track of all component files across all setups
        all_component_files.update(component_counts.keys())
        
        # Add component counts to setup metadata
        setup_metadata['component_counts'] = component_counts
        setup_data_list.append(setup_metadata)
    
    logger.info(f"Successfully processed {len(setup_data_list)} setup files")
    logger.info(f"Found {len(all_component_files)} unique component files")
    
    return setup_data_list, all_component_files

def create_csv_database(setup_data_list, all_component_files, output_file='setups_analysis.csv'):
    """
    Create CSV database from setup analysis data.
    
    Args:
        setup_data_list (list): List of setup metadata dictionaries
        all_component_files (set): Set of all unique component files
        output_file (str): Output CSV filename
    """
    if not setup_data_list:
        logger.error("No setup data to process")
        return
    
    # Prepare data for DataFrame
    rows = []
    
    for setup in setup_data_list:
        row = {
            'filename': setup['filename'],
            'name': setup['name'],
            'uc2_verified': setup['uc2_verified'],
            'collection': setup['collection'],
            'author': setup['author'],
            'github_link': setup['github_link'],
            'description': setup['description'],
            'category': setup['category'],
            'version': setup['version'],
            'createdAt': setup['createdAt'],
            'total_components': setup['total_components']
        }
        
        # Add component counts as separate columns
        component_counts = setup['component_counts']
        for component_file in sorted(all_component_files):
            # Use component filename as column name, replace special chars
            col_name = f"component_{component_file.replace('.', '_').replace(' ', '_').replace('-', '_')}"
            row[col_name] = component_counts.get(component_file, 0)
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Sort by filename for consistency
    df = df.sort_values('filename')
    
    # Save to CSV
    df.to_csv(output_file, index=False, sep=";", encoding='utf-8')
    logger.info(f"CSV database saved to: {output_file}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SETUP ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total setup files processed: {len(df)}")
    print(f"Total unique component files: {len(all_component_files)}")
    print(f"Average components per setup: {df['total_components'].mean():.1f}")
    print(f"Max components in a setup: {df['total_components'].max()}")
    print(f"Min components in a setup: {df['total_components'].min()}")
    
    # Show verification status
    verified_count = df['uc2_verified'].sum()
    print(f"Verified setups: {verified_count}/{len(df)} ({verified_count/len(df)*100:.1f}%)")
    
    # Show top authors
    print("\nTop authors:")
    author_counts = df['author'].value_counts()
    for author, count in author_counts.head(5).items():
        if author:  # Skip empty authors
            print(f"  {author}: {count} setups")
    
    # Show top collections
    print("\nTop collections:")
    collection_counts = df['collection'].value_counts()
    for collection, count in collection_counts.head(5).items():
        if collection:  # Skip empty collections
            print(f"  {collection}: {count} setups")
    
    # Show most used components
    print("\nMost used component files (top 10):")
    component_cols = [col for col in df.columns if col.startswith('component_')]
    component_totals = df[component_cols].sum().sort_values(ascending=False)
    
    for i, (col, count) in enumerate(component_totals.head(10).items()):
        if count > 0:
            # Clean up column name for display
            component_name = col.replace('component_', '').replace('_', ' ')
            print(f"  {i+1}. {component_name}: used {count} times")
    
    print(f"\nDetailed results saved to: {output_file}")
    print("="*60)

def main():
    """Main function to run the setup analysis."""
    logger.info("Starting UC2 setup analysis...")
    
    # Analyze setups folder
    setup_data_list, all_component_files = analyze_setups_folder('./setups')
    
    if not setup_data_list:
        logger.error("No valid setup files found. Exiting.")
        return
    
    # Create CSV database
    create_csv_database(setup_data_list, all_component_files, 'setups_analysis.csv')
    
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main()
