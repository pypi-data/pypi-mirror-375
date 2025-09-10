import logging
import os
from pandas_mcp_server.core.metadata import read_metadata
from pandas_mcp_server.server import setup_logging
import pprint

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

def test_file(file_path):
    """Test metadata extraction for a single file (path-based)"""
    print(f"\nTesting file (path): {file_path}")
    print("=" * 80)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    logger.info(f"Processing file: {file_path} ({file_size:.1f}MB)")
    print(f"File size: {file_size:.1f}MB")
    result = read_metadata(file_path=file_path)
    print("\nMetadata result status:", result.get('status'))
    if result.get('status') == 'ERROR':
        logger.error(f"Metadata extraction failed: {result.get('message', 'Unknown error')}")
        print("Error details:")
        pprint.pprint(result)
        return
    logger.info(f"Successfully processed file of type: {result.get('file_info', {}).get('type')}")
    print("\nFile info:")
    pprint.pprint(result.get('file_info'))
    if result.get('file_info', {}).get('type') == 'csv':
        columns = len(result['data']['columns'])
        print(f"\nColumns analyzed: {columns}")
        logger.info(f"CSV file processed with {columns} columns")
    else:
        sheets = len(result['data']['sheets'])
        print(f"\nSheets analyzed: {sheets}")
        for sheet in result['data']['sheets']:
            print(f"- {sheet['name']}: {len(sheet['columns'])} columns")
            logger.info(f"Sheet {sheet['name']} processed with {len(sheet['columns'])} columns")

def test_file_bytes(file_path):
    """Test metadata extraction from file bytes"""
    print(f"\nTesting file (bytes): {file_path}")
    print("=" * 80)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    result = read_metadata(file_bytes=file_bytes)
    print("\nMetadata result status:", result.get('status'))
    if result.get('status') == 'ERROR':
        logger.error(f"Metadata extraction failed: {result.get('message', 'Unknown error')}")
        print("Error details:")
        pprint.pprint(result)
        return
    logger.info(f"Successfully processed file of type: {result.get('file_info', {}).get('type')}")
    print("\nFile info:")
    pprint.pprint(result.get('file_info'))
    if result.get('file_info', {}).get('type') == 'csv':
        columns = len(result['data']['columns'])
        print(f"\nColumns analyzed: {columns}")
        logger.info(f"CSV file processed with {columns} columns")
    else:
        sheets = len(result['data']['sheets'])
        print(f"\nSheets analyzed: {sheets}")
        for sheet in result['data']['sheets']:
            print(f"- {sheet['name']}: {len(sheet['columns'])} columns")
            logger.info(f"Sheet {sheet['name']} processed with {len(sheet['columns'])} columns")

# Test files
files_to_test = [
    r"C:\Users\peter_kuik\Downloads\simple.xlsx",
]

logger.info("Starting metadata extraction tests")
for file_path in files_to_test:
    test_file(file_path)
for file_path in files_to_test:
    test_file_bytes(file_path)
logger.info("Metadata extraction tests completed")
