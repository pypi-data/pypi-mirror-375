import copy
import math
import os
import re
from typing import Any, Dict, List, Union

from pyadvtools import (
    IterateCombineExtendDict,
    read_list,
    sort_int_str,
    standard_path,
    write_list,
)

from ..bib.bibtexparser import Block, Library
from ..main import PythonRunBib, PythonWriters
from ..tools.experiments_base import generate_readme


def format_entries_for_abbr_zotero_save(
    j_conf_abbr: str,
    path_output: str,
    original_data: Union[List[str], str, Library],
    combine_year_length: int = 1,
    default_year_list: List[str] = [],
    write_flag_bib: str = "w",
    check_bib_exist: bool = False,
    write_flag_readme: str = "w",
    check_md_exist: bool = False,
    options: Dict[str, Any] = {},
) -> None:
    """Format bibliography entries and organize them by year and type.

    Processes bibliography data and organizes it into separate files by entry type and year,
    generating both BibTeX files and README documentation.

    Parameters
    ----------
    j_conf_abbr : str
        Journal/conference abbreviation used for naming output files
    path_output : str
        Output directory path for processed files
    original_data : Union[List[str], str, Library]
        Input bibliography data in various formats (list of strings, file path, or Library object)
    combine_year_length : int, optional
        Number of years to combine in each output file, by default 1
    default_year_list : List[str], optional
        Specific years to process (if empty, processes all years), by default []
    write_flag_bib : str, optional
        Write mode for BibTeX files ("w" for write, "a" for append), by default "w"
    check_bib_exist : bool, optional
        Whether to check if BibTeX files exist before writing, by default False
    write_flag_readme : str, optional
        Write mode for README files ("w" for write, "a" for append), by default "w"
    check_md_exist : bool, optional
        Whether to check if README files exist before writing, by default False
    options : Dict[str, Any], optional
        Additional processing options, by default {}

    Returns
    -------
    None
    """
    path_output = standard_path(path_output)

    # Set up processing options
    _options = {}
    _options.update(options)
    _options["is_sort_entry_fields"] = True  # Force field sorting
    _options["is_sort_blocks"] = True  # Force block sorting
    _options["sort_entries_by_field_keys_reverse"] = False  # Sort in ascending order

    # Initialize helper classes
    _python_bib = PythonRunBib(_options)

    _options["empty_entry_cite_keys"] = True  # Allow empty citation keys
    _python_writer = PythonWriters(_options)

    # Organize entries by type, year, volume, number, and month
    entry_type_year_volume_number_month_entry_dict = _python_bib.parse_to_nested_entries_dict(original_data)

    # Process each entry type separately
    for entry_type in entry_type_year_volume_number_month_entry_dict:

        # Filter years if specified
        year_dict = entry_type_year_volume_number_month_entry_dict[entry_type]
        year_list = sort_int_str(list(year_dict.keys()))
        if default_year_list:
            year_list = [y for y in year_list if y in default_year_list]
        year_dict = {year: year_dict[year] for year in year_list}

        # Save bibliography files grouped by years
        path_write = os.path.join(path_output, entry_type.lower(), "bib")
        for i in range(math.ceil(len(year_list) / combine_year_length)):

            # Determine year range for this file
            start_year_index = i * combine_year_length
            end_year_index = min([(i + 1) * combine_year_length, len(year_list)])
            combine_year = year_list[start_year_index:end_year_index]

            # Create subset dictionary for these years
            new_year_dict = {year: year_dict[year] for year in combine_year}
            entries: List[Block] = IterateCombineExtendDict().dict_update(copy.deepcopy(new_year_dict))

            # Generate filename based on year range
            name = f"{j_conf_abbr}_{combine_year[0]}"
            if len(combine_year) > 1:
                name += f"_{combine_year[-1]}"
            name += ".bib"

            # Write the bibliography file
            _python_writer.write_to_file(entries, name, write_flag_bib, path_write, check_bib_exist)

        # Generate and save README documentation
        path_write = os.path.join(path_output, entry_type.lower())
        readme_md = generate_readme(j_conf_abbr, entry_type, year_dict)

        # Handle append mode for README
        if re.search("a", write_flag_readme):
            old_readme_md = [re.sub(r"[ ]+", "", line) for line in read_list("README.md", "r", path_write)]
            readme_md = readme_md[3:] if old_readme_md else readme_md
            readme_md = [line for line in readme_md if re.sub(r"[ ]+", "", line) not in old_readme_md]

        write_list(readme_md, "README.md", write_flag_readme, path_write, check_md_exist)


def generate_statistic_information(path_output: str) -> None:
    """Generate statistical information from bibliography files.

    Processes all BibTeX files in the directory tree and extracts key information
    (DOIs and URLs) into CSV files for analysis.

    Parameters
    ----------
    path_output : str
        Root directory containing BibTeX files to process

    Returns
    -------
    None
    """
    # Find all BibTeX files in the directory tree
    full_files = []
    for root, _, files in os.walk(path_output):
        full_files.extend([os.path.join(root, f) for f in files if f.endswith(".bib")])

    # Configure processing options
    _options = {
        "is_standardize_bib": False,  # Skip standardization, default is True
        "choose_abbr_zotero_save": "save",  # Use save format, default is "save"
        "function_common_again": False,  # Skip reprocessing, default is True
        "function_common_again_abbr": False,  # Skip abbreviation reprocessing, default is True
        "function_common_again_zotero": False,  # Skip Zotero reprocessing, default is True
        "function_common_again_save": False,  # Skip save format reprocessing, default is True
        "is_sort_entry_fields": False,  # Skip field sorting
        "is_sort_blocks": False,  # Skip block sorting
    }
    _python_bib = PythonRunBib(_options)

    # Process each BibTeX file
    for f in full_files:
        informations = []
        library = _python_bib.parse_to_single_standard_library(f)

        # Extract DOI or URL for each entry
        for entry in library.entries:
            flag = ""
            if not flag:
                flag = entry["doi"] if "doi" in entry else ""
            if not flag:
                flag = entry["url"] if "url" in entry else ""
            informations.append(flag + "\n")

        # Write information to CSV file
        csv_path = f.replace(".bib", ".csv").replace("/bib/", "/url/")
        write_list(informations, csv_path, "w", None, False)

    return None
