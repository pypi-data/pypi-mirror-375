import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pyadvtools import (
    write_list,
)

from ..bib.bibtexparser import BibtexFormat, Block, Library
from ..bib.core import ConvertLibrayToStr
from .basic_input import BasicInput
from .python_run_bib import PythonRunBib


class PythonWriters(BasicInput):
    """Python writers.

    Args:
        options (Dict[str, Any]): Options.

    Attributes:
        bib_for_abbr_name (str = "abbr.bib"): Bib for abbr name.
        bib_for_zotero_name (str = "zotero.bib"): Bib for zotero name.
        bib_for_save_name (str = "save.bib"): Bib for save name.
        choose_abbr_zotero_save (str = "save"): Choose "abbr", "zotero", or "save".
        display_google_connected_scite (List[str] = ["google", "connected", "scite"]): Choose multiple items.
    """

    def __init__(self, options: Dict[str, Any]) -> None:
        options["is_sort_entry_fields"] = options.get("is_sort_entry_fields", True)
        options["is_sort_blocks"] = options.get("is_sort_blocks", True)
        options["sort_entries_by_field_keys_reverse"] = options.get("sort_entries_by_field_keys_reverse", True)
        super().__init__(options)

        self.bib_for_abbr_name = options.get("bib_for_abbr_name", "abbr.bib")
        self.bib_for_zotero_name = options.get("bib_for_zotero_name", "zotero.bib")
        self.bib_for_save_name = options.get("bib_for_save_name", "save.bib")
        self.choose_abbr_zotero_save = options.get("choose_abbr_zotero_save", "save")

        self.display_google_connected_scite = options.get(
            "display_google_connected_scite", ["google", "connected", "scite"]
        )

        self.bibtex_format_indent = options.get("bibtex_format_indent", "  ")
        self.bibtex_format_trailing_comma = options.get("bibtex_format_trailing_comma", True)
        self.bibtex_format_block_separator = options.get("bibtex_format_block_separator", "")

        bibtex_format = BibtexFormat()
        bibtex_format.indent = self.bibtex_format_indent
        bibtex_format.block_separator = self.bibtex_format_block_separator
        bibtex_format.trailing_comma = self.bibtex_format_trailing_comma
        self.bibtex_format: Optional[BibtexFormat] = bibtex_format

        self._python_bib = PythonRunBib(self.options)

    def write_to_str(self, library: Union[Library, List[Block]]) -> List[str]:
        """Serialize a BibTeX database to a string.

        Args:
            library (Library | List[Block]): BibTeX database to serialize.
            bibtex_format (Optional[BibtexFormat] = None):

        """
        return ConvertLibrayToStr(self.options).generate_str(library, self.bibtex_format)

    def write_to_file(
        self,
        original_data: Union[Library, List[Block], List[str]],
        file_name: str,
        write_flag: str = "w",
        path_storage: Optional[str] = None,
        check: bool = True,
        delete_first_empty: bool = True,
        delete_last_empty: bool = True,
        compulsory: bool = False,
        delete_original_file: bool = False,
    ) -> None:
        """Write.

        Args:
            original_data (Union[Library, List[Block], List[str]]): data
            file_name (str): file name
            write_flag (str = "w"): write flag
            path_storage (Optional[str] = None): path storage
            check (bool = True): check
            delete_first_empty (bool = True): delete first empty
            delete_last_empty (bool = True): delete last empty
            compulsory (bool = False): compulsory
            delete_original_file (bool = False): delete original file
            bibtex_format (Optional[BibtexFormat] = None):

        """
        _options = {}
        _options.update(self.options)
        _library_str = ConvertLibrayToStr(_options)

        if isinstance(original_data, Library):
            data_list = _library_str.generate_str(original_data, self.bibtex_format)
        elif isinstance(original_data, list):
            if all([isinstance(line, str) for line in original_data]):
                data_list = [line for line in original_data if isinstance(line, str)]
            else:
                data_list = [line for line in original_data if isinstance(line, Block)]
                data_list = _library_str.generate_str(data_list, self.bibtex_format)

        write_list(
            data_list,
            file_name,
            write_flag,
            path_storage,
            check,
            delete_first_empty,
            delete_last_empty,
            compulsory,
            delete_original_file,
        )
        return None

    def write_multi_library_to_file(
        self,
        path_output: str,
        bib_for_abbr: Union[Library, List[Block]],
        bib_for_zotero: Union[Library, List[Block]],
        bib_for_save: Union[Library, List[Block]],
        given_cite_keys: List[str] = [],
        **kwargs,
    ) -> Tuple[str, str, str]:
        _options = {}
        _options.update(self.options)
        _options["keep_entries_by_cite_keys"] = given_cite_keys
        _options["sort_entries_by_cite_keys"] = given_cite_keys

        bib_abbr = ConvertLibrayToStr(_options).generate_str(bib_for_abbr, **kwargs)
        write_list(bib_abbr, self.bib_for_abbr_name, "w", path_output, False, **kwargs)

        bib_zotero = ConvertLibrayToStr(_options).generate_str(bib_for_zotero, **kwargs)
        write_list(bib_zotero, self.bib_for_zotero_name, "w", path_output, False, **kwargs)

        bib_save = ConvertLibrayToStr(_options).generate_str(bib_for_save, **kwargs)
        write_list(bib_save, self.bib_for_save_name, "w", path_output, False, **kwargs)

        full_bib_for_abbr = os.path.join(path_output, self.bib_for_abbr_name)
        full_bib_for_zotero = os.path.join(path_output, self.bib_for_zotero_name)
        full_bib_for_save = os.path.join(path_output, self.bib_for_save_name)
        return full_bib_for_abbr, full_bib_for_zotero, full_bib_for_save

    def output_key_url_http_bib_dict(self, library: Library) -> Dict[str, List[List[str]]]:
        _options = {}
        _options.update(self.options)
        _options["empty_entry_cite_keys"] = True

        key_url_http_bib_dict: Dict[str, List[List[str]]] = {}

        for key, entry in library.entries_dict.items():

            url = entry["url"] if "url" in entry else ""
            if len(url) == 0:
                url = entry["doi"] if "doi" in entry else ""
                if (len(url) != 0) and (not re.match(r"https*://", url)):
                    url = f"https://doi.org/{url}"

            link_list = self._generate_link_list(entry)
            patch_bib = ConvertLibrayToStr(_options).generate_str([entry])

            v: List[List[str]] = [[], [], patch_bib]

            if len(url) != 0:
                v[0] = [url + "\n"]
                link_list.insert(0, rf"[www]({url})")

            join_link = []
            if link_list:
                for i in range(len(link_list) - 1):
                    join_link.append(link_list[i].strip() + " |\n")
                join_link.append(link_list[-1].strip() + "\n")

                join_link[0] = "(" + join_link[0]
                join_link[-1] = join_link[-1].strip() + ")\n"

                v[1] = join_link

            key_url_http_bib_dict.update({key: v})
        return key_url_http_bib_dict

    def _generate_link_list(self, entry) -> List[str]:
        title = entry["title"] if "title" in entry else ""
        if not title:
            return []

        title = re.sub(r"\s+", "+", title)
        url_google = f"https://scholar.google.com/scholar?q={title}"
        url_connected = f"https://www.connectedpapers.com/search?q={title}"
        url_scite = f"https://scite.ai/search?q={title}"

        # Search cited number
        cited_number = entry["annotation"] if "annotation" in entry else ""
        if cited_number:
            cited_number = re.sub(r"[^0-9]+", "", cited_number)
            cited_number = int(cited_number) if cited_number.isdigit() else ""
            google = f"[Google Scholar: {cited_number}]({url_google})"
        else:
            google = f"[Google Scholar]({url_google})"

        connected = f"[Connected Papers]({url_connected})"
        scite = f"[Scite]({url_scite})"

        link_list = []
        for i, j in zip(["google", "connected", "scite"], [google, connected, scite]):
            if i in self.display_google_connected_scite:
                link_list.append(j)

        return link_list
