import copy
import re
from typing import Dict, List, Tuple

from ...bib.bibtexparser import Library
from ...main import PythonRunBib, PythonWriters
from .search_writers import WriteInitialResult, WriteSeparateResult


def search_keywords_core(keywords_list_list: List[List[str]], library: Library, field: str) -> Tuple[Library, Library]:
    """Search keywords in `field` such as `title` or `abstract` or `keywords`."""
    search_library = []
    no_search_library = []

    for entry in library.entries:
        flag = False
        content = entry[field] if field in entry else ""
        if content:
            content = re.sub("{", "", content)
            content = re.sub("}", "", content)

            # All keywords from keyword_list_list[0] should be found in bib
            flag = all([re.search(keyword, content, flags=re.I) for keyword in keywords_list_list[0]])
            if flag and (len(keywords_list_list) == 2):
                # Any keywords from keyword_list_list[1] found in bib will results in False flag.
                flag = not any([re.search(keyword, content, flags=re.I) for keyword in keywords_list_list[1]])

        if flag:
            search_library.append(entry)
        else:
            no_search_library.append(entry)

    return Library(search_library), Library(no_search_library)


class SearchInitialResult(object):
    """Search initial result.

    Args:
        options: dict

    Attributes:
        options: dict

        print_on_screen (bool = False): print on screen
        deepcopy_library_for_every_field (bool = False): deepcopy library for every field
    """

    def __init__(self, options: dict) -> None:
        self.options = options

        self.print_on_screen: bool = options.get("print_on_screen", False)
        self.deepcopy_library_for_every_field = options.get("deepcopy_library_for_every_field", False)

        self._python_bib = PythonRunBib(options)

        _options = {}
        _options["empty_entry_cite_keys"] = True
        _options.update(self.options)
        self._python_writer = PythonWriters(_options)

    def main(
        self,
        search_field_list: List[str],
        path_initial: str,
        library: Library,
        keywords_type: str,
        keywords_list_list: List[List[str]],
        combine_keywords: str,
        output_prefix: str,
        path_separate: str,
    ) -> Tuple[List[str], Dict[str, List[List[str]]], Dict[str, int], Library]:
        """Search."""
        error_pandoc_md_md, field_data_dict, no_search_library = [], {}, library
        field_number_dict: Dict[str, int] = {}

        for field in search_field_list:
            if len(no_search_library.entries) == 0:
                continue

            # Search
            search_library, no_search_library = search_keywords_core(keywords_list_list, no_search_library, field)
            field_number_dict.update({field: len(search_library.entries)})

            # Deepcopy library for every field
            if self.deepcopy_library_for_every_field:
                no_search_library = copy.deepcopy(library)

            # Operate on the search library (deepcopy)
            libraries = self._python_bib.parse_to_multi_standard_library(copy.deepcopy(search_library))
            library_for_abbr, library_for_zotero, library_for_save = libraries

            if self.print_on_screen:
                print("".join(self._python_writer.write_to_str(library_for_zotero)))
                continue
            if not (library_for_abbr.entries and library_for_zotero.entries and library_for_save.entries):
                continue

            # Initially write tex, bib, and md files
            data_temp, temp_error_pandoc_md_md = WriteInitialResult(copy.deepcopy(self.options)).main(
                path_initial,
                output_prefix,
                field,
                keywords_type,
                combine_keywords,
                library_for_abbr,
                library_for_zotero,
                library_for_save,
            )

            # Separatelly write with the method 'a' for '_basic', '_beauty', '_complex'
            WriteSeparateResult().main(copy.deepcopy(data_temp), field, keywords_type, combine_keywords, path_separate)

            # Save for combined results
            field_data_dict.update({field: copy.deepcopy(data_temp)})
            error_pandoc_md_md.extend(temp_error_pandoc_md_md)

        return error_pandoc_md_md, field_data_dict, field_number_dict, no_search_library
