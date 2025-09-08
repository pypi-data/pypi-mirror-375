import os
import re
from typing import Any, Dict, List, Union

from pyadvtools import standard_path, transform_to_data_list, write_list

from ...bib.bibtexparser import Library
from ...main import PythonRunBib, PythonWriters


def replace_to_standard_cite_keys(
    full_tex_md: str, full_bib: str, path_output: str, options: Dict[str, Any]
) -> List[str]:
    ext = os.path.splitext(full_tex_md)[-1]
    if ext not in [".tex", ".md", "md", "tex"]:
        print(f"{full_tex_md} must be `.tex` or `.md` file.")
        return []

    path_output = standard_path(path_output)

    bib_data = transform_to_data_list(full_bib, ".bib")
    old_key_new_entry_dict = generate_old_key_new_entry_dict(bib_data, options)

    data = "".join(transform_to_data_list(full_tex_md, ext))
    for old_key, new_entry in old_key_new_entry_dict.items():
        if ext == ".tex":
            data = re.sub(r"\\cite([a-z]*){\s*" + old_key + r"\s*}", r"\\cite\1{" + new_entry.key + "}", data)
            data = re.sub(r"\\cite([a-z]*){\s*" + old_key + r"\s*,", r"\\cite\1{" + new_entry.key + ",", data)
            data = re.sub(r",\s*" + old_key + r"\s*,", r"," + new_entry.key + r",", data)
            data = re.sub(r",\s*" + old_key + r"\s*}", r"," + new_entry.key + "}", data)
        elif ext == ".md":
            data = re.sub(r"\[@\s*" + old_key + r"\s*\]", r"[@" + new_entry.key + "]", data)
            data = re.sub(r"\[@\s*" + old_key + r"\s*,", r"[@" + new_entry.key + ",", data)
            data = re.sub(r",\s*" + old_key + r"\s*,", r"," + new_entry.key + r",", data)
            data = re.sub(r",\s*" + old_key + r"\s*\]", r"," + new_entry.key + "]", data)
        else:
            pass
    data_list = data.splitlines(keepends=True)
    write_list(data_list, f"new{ext}", "w", path_output, False)

    _options = {}
    _options.update(options)
    _options["is_sort_blocks"] = False  # default is True
    _python_write = PythonWriters(_options)
    _python_write.write_to_file(list(old_key_new_entry_dict.values()), "new.bib", "w", path_output, False)
    return data_list


def generate_old_key_new_entry_dict(bib_data: Union[List[str], str], options: Dict[str, Any]) -> dict:
    # generate library
    _options = {}
    _options.update(options)
    _options["generate_entry_cite_keys"] = False  # default is False
    _python_bib = PythonRunBib(_options)
    library = _python_bib.parse_to_single_standard_library(bib_data)

    _options = {}
    _options.update(options)
    _options["generate_entry_cite_keys"] = True  # default is False
    _python_bib = PythonRunBib(_options)

    old_key_new_entry_dict = {}
    generate_cite_keys: List[str] = []
    for old_key in (entries_dict := library.entries_dict):
        new_library = _python_bib.parse_to_single_standard_library(Library([entries_dict[old_key]]))
        if len(new_library.entries) == 1:
            new_entry = new_library.entries[0]

            # update cite key
            new_key = new_entry.key
            while new_key in generate_cite_keys:
                new_key += "-a"
            new_entry.key = new_key

            # save
            generate_cite_keys.append(new_entry.key)
            old_key_new_entry_dict[old_key] = new_entry

        else:
            old_key_new_entry_dict[old_key] = entries_dict[old_key]
    return old_key_new_entry_dict
