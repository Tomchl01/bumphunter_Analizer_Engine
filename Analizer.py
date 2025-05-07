import pandas as pd
import numpy as np
import json
from datetime import datetime
import os
import traceback
import webbrowser
from pathlib import Path
import base64
import zlib

# Configuration
class Config:
    # Input/output paths - Update these to match your file locations
    INPUT_FILE = "CashGamesSessions.csv"
    TEMPLATE_FILE = "template.html"  # Path to your HTML template file
    OUTPUT_DIR = "output"
    OUTPUT_REPORT = "bumphunter_report.html"
    
    # Analysis parameters
    TIME_THRESHOLD = 15  # Maximum time gap to consider suspicious (seconds)


def main():
    """Main function to run the bumphunter analysis."""
    print("Starting bumphunter analysis...")
    config = Config()
    
    # Load the CSV file
    input_file = config.INPUT_FILE
    df = pd.read_csv(input_file)
    
    # Convert startSession and endSession to datetime
    df['startSession'] = pd.to_datetime(df['startSession'], errors='coerce')
    df['endSession'] = pd.to_datetime(df['endSession'], errors='coerce')
    
    # Perform analysis
    suspicious_joins = detect_suspicious_joins(df, config.TIME_THRESHOLD)
    bumphunter_profiles, target_profiles = profile_users(df, suspicious_joins)
    original_data = prepare_original_data(df)
    
    # Combine data for the report
    combined_data = {
        'suspiciousJoins': suspicious_joins,
        'bumphunterProfiles': bumphunter_profiles,
        'targetProfiles': target_profiles,
        'originalData': original_data
    }
    
    # Load the HTML template
    with open(config.TEMPLATE_FILE, 'r', encoding='utf-8') as template_file:
        template = template_file.read()
    
    # Generate the HTML report
    output_path = str(Path(config.OUTPUT_DIR) / config.OUTPUT_REPORT)
    generate_html_report(combined_data, template, output_path)
    print(f"Report generated: {output_path}")


def prepare_original_data(df):
    """
    Prepare the original data for inclusion in the report.
    
    Args:
        df: DataFrame containing the session data
        
    Returns:
        List of dictionaries with the original data
    """
    data_records = []
    
    # Convert DataFrame to list of dicts
    for _, row in df.iterrows():
        record = {
            'tableId': str(row.get('tableId', '')),
            'tableName': str(row.get('tableName', f"Table {row.get('tableId', '')}")),
            'username': str(row.get('username', '')),
            'startSession': row.get('startSession', '').isoformat() if pd.notnull(row.get('startSession', '')) else '',
            'endSession': row.get('endSession', '').isoformat() if pd.notnull(row.get('endSession', '')) else '',
            'gameType': str(row.get('gameType', '')),
            'limitType': str(row.get('limitType', '')),
            'smallBlind': float(row.get('smallBlind', 0)) if pd.notnull(row.get('smallBlind', 0)) else 0,
            'bigBlind': float(row.get('bigBlind', 0)) if pd.notnull(row.get('bigBlind', 0)) else 0
        }
        
        # Add any additional columns that might be in the dataframe
        for col in df.columns:
            if col not in record:
                record[col] = str(row.get(col, '')) if pd.notnull(row.get(col, '')) else ''
        
        data_records.append(record)
    
    return data_records


def detect_suspicious_joins(df, time_threshold):
    """
    Detect suspicious joins where a player joins a table shortly after another player.
    
    Args:
        df: DataFrame containing the session data
        time_threshold: Maximum time difference (in seconds) to consider suspicious
        
    Returns:
        List of suspicious joins
    """
    # Sort sessions by tableId and startSession time
    sorted_df = df.sort_values(['tableId', 'startSession'])
    
    # Initialize list to store suspicious joins
    suspicious_joins = []
    
    # Group by tableId
    for table_id, table_group in sorted_df.groupby('tableId'):
        # Convert to list of dictionaries for easier processing
        table_sessions = table_group.to_dict('records')
        
        # Check for suspicious joins within each table
        for i in range(1, len(table_sessions)):
            current_session = table_sessions[i]
            previous_session = table_sessions[i-1]
            
            # Calculate time difference in seconds
            time_diff = (current_session['startSession'] - previous_session['startSession']).total_seconds()
            
            # If join time is within threshold
            if time_diff <= time_threshold:
                suspicious_joins.append({
                    'tableId': str(table_id),
                    'tableName': str(current_session.get('tableName', f"Table {table_id}")),
                    'joiner': str(current_session['username']),
                    'join_time': current_session['startSession'].isoformat(),
                    'preceding_player': str(previous_session['username']),
                    'time_gap_sec': float(time_diff),
                    'smallBlind': float(current_session.get('smallBlind', 0)) if pd.notnull(current_session.get('smallBlind', 0)) else 0,
                    'bigBlind': float(current_session.get('bigBlind', 0)) if pd.notnull(current_session.get('bigBlind', 0)) else 0,
                    'gameType': str(current_session.get('gameType', '')),
                    'limitType': str(current_session.get('limitType', ''))
                })
    
    return suspicious_joins


def profile_users(df, suspicious_joins):
    """
    Profile users to detect potential bumphunters and targets.
    
    Args:
        df: DataFrame containing the session data
        suspicious_joins: List of suspicious joins
        
    Returns:
        Tuple of (bumphunter_profiles, target_profiles)
    """
    # Count total sessions per user
    user_session_counts = df['username'].value_counts().to_dict()
    
    # Initialize dictionaries for profiles
    bumphunter_profiles = {}
    target_profiles = {}
    
    # Initialize all users
    all_users = set(df['username'].unique())
    for username in all_users:
        bumphunter_profiles[username] = {
            'username': str(username),
            'join_after_count': 0,
            'join_after_percentage': 0,
            'targets': [],
            'most_common_target': None,
            'most_common_target_count': 0,
            'target_consistency': 0,
            'total_sessions': int(user_session_counts.get(username, 0)),
            'score': 0
        }
        
        target_profiles[username] = {
            'username': str(username),
            'joined_after_count': 0,
            'joined_after_percentage': 0,
            'hunters': [],
            'most_common_hunter': None,
            'most_common_hunter_count': 0,
            'hunter_consistency': 0,
            'total_sessions': int(user_session_counts.get(username, 0))
        }
    
    # Track targets and hunters
    target_counter = {}
    hunter_counter = {}
    
    # Process suspicious joins
    for join in suspicious_joins:
        joiner = join['joiner']
        target = join['preceding_player']
        
        # Initialize counters if needed
        if joiner not in target_counter:
            target_counter[joiner] = {}
        if target not in hunter_counter:
            hunter_counter[target] = {}
        
        # Update counters
        if target not in target_counter[joiner]:
            target_counter[joiner][target] = 0
        target_counter[joiner][target] += 1
        
        if joiner not in hunter_counter[target]:
            hunter_counter[target][joiner] = 0
        hunter_counter[target][joiner] += 1
        
        # Update bumphunter profile
        if joiner in bumphunter_profiles:
            bumphunter_profiles[joiner]['join_after_count'] += 1
        
        # Update target profile
        if target in target_profiles:
            target_profiles[target]['joined_after_count'] += 1
    
    # Process target counts and find most common targets
    for username, targets in target_counter.items():
        if username in bumphunter_profiles:
            # Save targets list for user analysis 
            bumphunter_profiles[username]['targets'] = [
                {"target": target, "count": count} 
                for target, count in targets.items()
            ]
            
            # Find most common target
            if targets:
                most_common_target, count = max(targets.items(), key=lambda x: x[1])
                bumphunter_profiles[username]['most_common_target'] = most_common_target
                bumphunter_profiles[username]['most_common_target_count'] = count
    
    # Process hunter counts and find most common hunters
    for username, hunters in hunter_counter.items():
        if username in target_profiles:
            # Save hunters list for user analysis
            target_profiles[username]['hunters'] = [
                {"hunter": hunter, "count": count} 
                for hunter, count in hunters.items()
            ]
            
            # Find most common hunter
            if hunters:
                most_common_hunter, count = max(hunters.items(), key=lambda x: x[1])
                target_profiles[username]['most_common_hunter'] = most_common_hunter
                target_profiles[username]['most_common_hunter_count'] = count
    
    # Calculate percentages and target consistency
    for username, profile in bumphunter_profiles.items():
        # Calculate join percentage
        if profile['total_sessions'] > 0:
            profile['join_after_percentage'] = round(
                (profile['join_after_count'] / profile['total_sessions']) * 100
            )
        
        # Calculate target consistency
        if profile['join_after_count'] > 0 and profile['most_common_target_count'] is not None:
            profile['target_consistency'] = round(
                (profile['most_common_target_count'] / profile['join_after_count']) * 100
            )
        
        # Calculate bumphunter score
        if profile['join_after_count'] > 0:
            # Join count - more joins = higher score
            join_count_factor = min(1, profile['join_after_count'] / 10) * 40  # Max 40 points
            
            # Join percentage - higher percentage = higher score
            join_percentage_factor = min(1, profile['join_after_percentage'] / 50) * 30  # Max 30 points
            
            # Target consistency - higher consistency = higher score
            consistency_factor = min(1, profile['target_consistency'] / 100) * 30  # Max 30 points
            
            # Combine factors for final score (0-100)
            profile['score'] = round(join_count_factor + join_percentage_factor + consistency_factor)
    
    # Calculate hunter consistency for targets
    for username, profile in target_profiles.items():
        # Calculate joined percentage
        if profile['total_sessions'] > 0:
            profile['joined_after_percentage'] = round(
                (profile['joined_after_count'] / profile['total_sessions']) * 100
            )
        
        # Calculate hunter consistency
        if profile['joined_after_count'] > 0 and profile['most_common_hunter_count'] is not None:
            profile['hunter_consistency'] = round(
                (profile['most_common_hunter_count'] / profile['joined_after_count']) * 100
            )
    
    # Convert dictionaries to lists
    bumphunter_list = list(bumphunter_profiles.values())
    target_list = list(target_profiles.values())
    
    # Sort bumphunters by score and targets by joined_after_count
    bumphunter_list.sort(key=lambda x: x['score'], reverse=True)
    target_list.sort(key=lambda x: x['joined_after_count'], reverse=True)
    
    return bumphunter_list, target_list


def compress_data(data):
    """Compress JSON data to base64 string."""
    # Convert data to JSON string
    json_str = json.dumps(data)
    
    # Check size before compression
    original_size = len(json_str.encode('utf-8'))
    if original_size > 100_000_000:  # 100MB
        print(f"Warning: Large dataset ({original_size / 1_000_000:.1f}MB) may cause browser performance issues")
    
    # Compress the JSON string
    compressed = zlib.compress(json_str.encode('utf-8'))
    compressed_size = len(compressed)
    
    # Log compression ratio
    ratio = (1 - compressed_size / original_size) * 100
    print(f"Compressed data: {compressed_size / 1_000_000:.1f}MB ({ratio:.1f}% reduction)")
    
    # Convert to base64 for embedding in HTML
    return base64.b64encode(compressed).decode('utf-8')


def generate_html_report(data, template, output_path):
    """Generate an HTML report using the template and the data."""
    # Compress the data
    compressed_data = compress_data(data)
    
    # Create initialization script with compressed data
    init_script = f"""
    <script>
        // Initialize with compressed data
        window.addEventListener('DOMContentLoaded', function() {{
            console.log("Decompressing data...");
            const compressedData = "{compressed_data}";
            
            // Decompress and load the data
            try {{
                const decoded = atob(compressedData);
                const charData = decoded.split('').map(x => x.charCodeAt(0));
                const binData = new Uint8Array(charData);
                const data = JSON.parse(pako.inflate(binData, {{ to: 'string' }}));
                console.log("Data decompressed successfully");
                loadData(data);
            }} catch (error) {{
                console.error("Error decompressing data:", error);
            }}
        }});
    </script>
    </body>
    """
    
    # Replace the placeholder and add initialization script
    filled_template = template.replace('</body>', init_script)
    
    # Write the modified template to the output file
    with open(output_path, 'w', encoding='utf-8') as html_file:
        html_file.write(filled_template)
    
    return output_path


if __name__ == "__main__":
    main()