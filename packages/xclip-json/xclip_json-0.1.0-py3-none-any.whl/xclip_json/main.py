import subprocess
import json
import sys
import base64
from typing import Dict, Any

def get_targets(selection: str) -> list[str]:
    """
    Retrieves a list of available targets for a given X selection.
    
    Args:
        selection: The X selection to query (e.g., 'primary', 'secondary', 'clipboard').
        
    Returns:
        A list of strings, where each string is a clipboard target.
    """
    try:
        # Use the -selection flag to specify which selection to get targets from
        result = subprocess.run(
            ['xclip', '-o', '-t', 'TARGETS', '-selection', selection],
            capture_output=True,
            text=True,
            check=True
        )
        # The output is a string of targets separated by newlines
        targets = result.stdout.strip().split('\n')
        return [t.strip() for t in targets if t.strip()]
    except FileNotFoundError:
        print("Error: The 'xclip' command was not found. Please ensure it is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error calling xclip with selection '{selection}': {e}", file=sys.stderr)
        return []

def get_clipboard_data(selection: str, target: str) -> str | bytes | None:
    """
    Retrieves data for a specific clipboard target and selection.
    
    Args:
        selection: The X selection to retrieve data from.
        target: The specific clipboard target to retrieve.
        
    Returns:
        The clipboard data as a string, bytes, or None if retrieval fails.
    """
    try:
        # Heuristic to check if the target is a text or binary type
        is_text = any(s in target.lower() for s in ['string', 'text', 'uri'])
        
        result = subprocess.run(
            ['xclip', '-o', '-t', target, '-selection', selection],
            capture_output=True,
            check=True
        )
        
        # If it's a text type, decode it to a string.
        if is_text:
            return result.stdout.decode('utf-8', errors='replace')
        # Otherwise, return the raw bytes.
        else:
            return result.stdout
            
    except subprocess.CalledProcessError:
        # Handle cases where a target exists but cannot be retrieved
        return None
        
def main():
    """
    Dumps all X selections and their targets to a single machine-readable JSON object.
    """
    # Define the selections to query
    selections_to_dump = ['primary', 'secondary', 'clipboard']
    all_selections_data: Dict[str, Any] = {}
    
    for selection in selections_to_dump:
        # Get the list of all available targets for the current selection
        targets = get_targets(selection)
        
        clipboard_data: Dict[str, Any] = {}
        
        for target in targets:
            data = get_clipboard_data(selection, target)
            if data is not None:
                if isinstance(data, bytes):
                    # For binary data, store both the value and a flag
                    clipboard_data[target] = {
                        "value": base64.b64encode(data).decode('utf-8'),
                        "binary": True
                    }
                else:
                    # For text data, store the value as a simple string
                    clipboard_data[target] = data.strip('\x00')
        
        all_selections_data[selection.upper()] = clipboard_data
    
    # Create the final JSON structure and print it
    print(json.dumps(all_selections_data, indent=2))

if __name__ == "__main__":
    main()
