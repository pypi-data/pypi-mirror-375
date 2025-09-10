import os
import csv
import traceback
import logging
import pandas as pd
from chardet import detect
from io import BytesIO, StringIO
from .config import MAX_FILE_SIZE
from .data_types import get_descriptive_type

# Get metadata logger
logger = logging.getLogger('metadata')

def read_metadata(file_path: str = None, file_bytes: bytes = None) -> dict:
    """Read file metadata (Excel or CSV) and return in MCP-compatible format.
    Args:
        file_path: Absolute path to data file (optional)
        file_bytes: File content as bytes (optional)
    Returns:
        dict: Structured metadata including:
            For Excel:
                - file_info: {type: "excel", sheet_count, sheet_names}
                - data: {sheets: [{sheet_name, rows, columns}]}
            For CSV:
                - file_info: {type: "csv", encoding, delimiter}
                - data: {rows, columns}
            Common:
                - status: SUCCESS/ERROR
                - columns contain:
                    - name, type, examples
                    - stats: null_count, unique_count
                    - warnings, suggested_operations
    """
    try:
        # Detect file type
        file_ext = None
        file_size = None
        encoding = None
        if file_bytes is not None:
            # Try Excel first
            try:
                pd.ExcelFile(BytesIO(file_bytes))
                file_ext = '.xlsx'
            except Exception:
                file_ext = '.csv'
            file_size = len(file_bytes)
        elif file_path is not None:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
        else:
            return {"status": "ERROR", "error": "NO_INPUT", "message": "No file_path or file_bytes provided"}

        if file_size is not None and file_size > MAX_FILE_SIZE:
            return {
                "status": "ERROR",
                "error": "FILE_TOO_LARGE",
                "max_size": f"{MAX_FILE_SIZE / 1024 / 1024}MB",
                "actual_size": f"{file_size / 1024 / 1024:.1f}MB"
            }

        if file_ext == '.csv':
            logger.info("Processing CSV file")
            if file_bytes is not None:
                raw_data = file_bytes[:10000]
                encoding = detect(raw_data)['encoding']
                csv_str = file_bytes.decode(encoding)
                reader = csv.reader(StringIO(csv_str))
                first_line = next(reader)
                if first_line and first_line[0].startswith('sep='):
                    header = next(reader)
                else:
                    header = first_line
                lines = []
                for i, row in enumerate(reader):
                    if i >= 100:
                        break
                    lines.append(row)
                df = pd.DataFrame(lines, columns=header)
            else:
                if not os.path.exists(file_path):
                    return {"status": "ERROR", "error": "FILE_NOT_FOUND", "path": file_path}
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)
                    encoding = detect(raw_data)['encoding']
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.reader(f)
                    first_line = next(reader)
                    if first_line and first_line[0].startswith('sep='):
                        header = next(reader)
                    else:
                        header = first_line
                    lines = []
                    for i, row in enumerate(reader):
                        if i >= 100:
                            break
                        lines.append(row)
                df = pd.DataFrame(lines, columns=header)
            for col in df.columns:
                if pd.api.types.is_object_dtype(df[col]):
                    df[col] = df[col].astype('category')
                elif pd.api.types.is_float_dtype(df[col]):
                    df[col] = df[col].astype('float32')
            table_meta = process_sheet(df)
            return {
                "status": "SUCCESS",
                "file_info": {
                    "type": "csv",
                    "size": f"{file_size / 1024:.1f}KB" if file_size else None,
                    "encoding": encoding,
                    "delimiter": ","
                },
                "data": {
                    "rows": table_meta['rows'],
                    "columns": table_meta['columns']
                }
            }
        else:
            logger.info("Processing Excel file")
            sheets_metadata = []
            if file_bytes is not None:
                with pd.ExcelFile(BytesIO(file_bytes)) as excel_file:
                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = excel_file.parse(
                                sheet_name,
                                nrows=100,
                                dtype={'object': 'category', 'float64': 'float32'}
                            )
                            sheet_meta = process_sheet(df)
                            sheet_meta['sheet_name'] = sheet_name
                            sheets_metadata.append(sheet_meta)
                            del df
                        except Exception as e:
                            logging.error(f"Error processing sheet {sheet_name}: {str(e)}")
                            continue
            else:
                if not os.path.exists(file_path):
                    return {"status": "ERROR", "error": "FILE_NOT_FOUND", "path": file_path}
                with pd.ExcelFile(file_path) as excel_file:
                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = excel_file.parse(
                                sheet_name,
                                nrows=100,
                                dtype={'object': 'category', 'float64': 'float32'}
                            )
                            sheet_meta = process_sheet(df)
                            sheet_meta['sheet_name'] = sheet_name
                            sheets_metadata.append(sheet_meta)
                            del df
                        except Exception as e:
                            logging.error(f"Error processing sheet {sheet_name}: {str(e)}")
                            continue
            return {
                "status": "SUCCESS",
                "file_info": {
                    "type": "excel",
                    "size": f"{file_size / 1024:.1f}KB" if file_size else None,
                    "sheet_count": len(sheets_metadata),
                    "sheet_names": [s['sheet_name'] for s in sheets_metadata]
                },
                "data": {
                    "sheets": [
                        {
                            "name": sheet['sheet_name'],
                            "rows": sheet['rows'],
                            "columns": [
                                {
                                    "name": col['name'],
                                    "type": col['type'],
                                    "examples": col['examples'],
                                    "stats": {
                                        "null_count": col['stats']['null_count'],
                                        "unique_count": col['stats']['unique_count']
                                    }
                                }
                                for col in sheet['columns']
                            ]
                        }
                        for sheet in sheets_metadata
                    ]
                }
            }
    except Exception as e:
        error_info = {
            "status": "ERROR",
            "error_type": type(e).__name__,
            "message": str(e),
            "solution": [
                "Check if the file is being used by another program",
                "Try saving the file as UTF-8 encoded CSV",
                "Contact the administrator to check MCP file access permissions"
            ],
            "traceback": traceback.format_exc()
        }
        logger.error(f"Metadata processing failed: {error_info['error_type']}")
        logger.debug(f"Error details: {error_info['message']}")
        logger.debug(f"Full traceback:\n{error_info['traceback']}")
        return error_info
    finally:
        # Log final memory stats
        try:
            import psutil
            process = psutil.Process()
            memory_logger = logging.getLogger('memory_usage')
            current_mem = process.memory_info().rss / 1024 / 1024
            memory_logger.info(f"Final memory usage: {current_mem:.1f}MB")
            logger.info("Metadata processing complete")
        except Exception as e:
            logger.warning(f"Failed to log memory stats: {e}")

def process_sheet(df: pd.DataFrame) -> dict:
    """Process a single sheet with memory optimizations"""
    import gc
    import logging
    import psutil
    
    memory_logger = logging.getLogger('memory_usage')
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024
    memory_logger.debug(f"Memory usage before processing sheet: {mem_before:.1f}MB")
    
    # Convert to optimal dtypes
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            if df[col].nunique() / len(df) < 0.5:  # Good candidate for category
                df[col] = df[col].astype('category')
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype('float32')
    
    """Process a single sheet and return enhanced metadata for query generation."""
    columns_metadata = []
    for col in df.columns:
        # Skip empty column names
        if not str(col).strip():
            continue
            
        series = df[col]
        col_type = get_descriptive_type(series)
        
        # Safely get examples
        try:
            examples = series.dropna().iloc[:3].tolist()
        except AttributeError:
            examples = []
        
        col_meta = {
            "name": str(col).strip(),
            "type": col_type,
            "examples": examples,
            "stats": {
                "null_count": series.isnull().sum(),
                "unique_count": series.nunique(),
                "is_numeric": pd.api.types.is_numeric_dtype(series),
                "is_temporal": pd.api.types.is_datetime64_any_dtype(series),
                "is_categorical": series.nunique() < 20 and pd.api.types.is_string_dtype(series)
            },
            "warnings": [],
            "suggested_operations": []
        }
        
        # Enhanced numeric stats
        if pd.api.types.is_numeric_dtype(series):
            col_meta["stats"].update({
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "percentiles": {
                    "25": float(series.quantile(0.25)),
                    "50": float(series.quantile(0.5)),
                    "75": float(series.quantile(0.75))
                }
            })
            col_meta["suggested_operations"].extend([
                "normalize", "scale", "log_transform", "binning"
            ])
        
        # Enhanced string stats
        if pd.api.types.is_string_dtype(series):
            col_meta["stats"].update({
                "max_length": int(series.str.len().max()),
                "distinct_values": series.dropna().unique().tolist()[:10],
                "value_counts": series.value_counts().head(5).to_dict()
            })
            col_meta["suggested_operations"].extend([
                "one_hot_encode", "label_encode", "text_processing",
                "string_cleaning", "regex_extract"
            ])
        
        # Enhanced datetime stats
        if pd.api.types.is_datetime64_any_dtype(series):
            col_meta["stats"].update({
                "min_date": str(series.min()),
                "max_date": str(series.max()),
                "time_span": str(series.max() - series.min())
            })
            col_meta["suggested_operations"].extend([
                "extract_year", "extract_month", "time_delta",
                "day_of_week", "time_binning"
            ])
        
        # Enhanced warnings
        null_count = series.isnull().sum()
        unique_count = series.nunique()
        
        if null_count > 0:
            null_pct = null_count / len(series) * 100
            col_meta["warnings"].append(f"{null_count} null values ({null_pct:.1f}%)")
        if unique_count == 1:
            col_meta["warnings"].append("Single value column")
        elif unique_count < 5:
            col_meta["warnings"].append(f"Low cardinality (only {unique_count} values)")
        if pd.api.types.is_numeric_dtype(series):
            if series.abs().max() > 1e6:
                col_meta["warnings"].append("Large values - consider scaling")
            if series.skew() > 2:
                col_meta["warnings"].append("Highly skewed distribution")
        
        columns_metadata.append(col_meta)
    
    # Force cleanup of temporary objects
    gc.collect()
    mem_after = process.memory_info().rss / 1024 / 1024
    memory_logger.debug(f"Memory usage after processing sheet: {mem_after:.1f}MB")
    memory_logger.debug(f"Memory change during sheet processing: {mem_after - mem_before:.1f}MB")
    
    return {
        "rows": len(df),
        "cols": len(df.columns),
        "columns": [
            {
                "name": col['name'],
                "type": col['type'],
                "examples": col['examples'],
                "stats": {
                    "null_count": col['stats']['null_count'],
                    "unique_count": col['stats']['unique_count']
                }
            }
            for col in columns_metadata
        ]
    }
