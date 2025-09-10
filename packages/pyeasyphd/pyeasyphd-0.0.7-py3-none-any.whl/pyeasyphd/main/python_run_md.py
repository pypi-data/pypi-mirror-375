import copy
import os
import re
import shutil
import time
from typing import Any, Dict, List, Tuple

from pyadvtools import (
    combine_content_in_list,
    delete_empty_lines_last_occur_add_new_line,
    read_list,
    write_list,
)

from ..bib.core import ConvertStrToLibrary
from .basic_input import BasicInput
from .pandoc_md_to import PandocMdTo
from .python_writers import PythonWriters


class PythonRunMd(BasicInput):
    """Python markdown.

    Args:
        options (Dict[str, Any]): Options.

    Attributes:
        delete_temp_generate_md (bool = True): Whether to delete temp generate md.
        add_reference_in_md (bool = True): Whether to add reference in md.
        add_bib_in_md (bool = False): Whether to add bib in md.
        replace_cite_to_fullcite_in_md (bool = False): Whether to replace cite to fullcite in md.
        replace_by_basic_beauty_complex_in_md (str = "beauty"): Replace by basic, beauty, or complex.
        display_basic_beauty_complex_references_in_md (str = "beauty"): Display basic, beauty, or complex references.
    """

    def __init__(self, options: Dict[str, Any]) -> None:
        super().__init__(options)

        # for md
        self.final_output_main_md_name: str = options.get("final_output_main_md_name", "")
        self.delete_temp_generate_md: bool = options.get("delete_temp_generate_md", True)
        self.add_reference_in_md: bool = options.get("add_reference_in_md", True)
        self.add_bib_in_md: bool = options.get("add_bib_in_md", False)
        self.replace_cite_to_fullcite_in_md: bool = options.get("replace_cite_to_fullcite_in_md", False)
        self.replace_by_basic_beauty_complex_in_md: str = options.get("replace_by_basic_beauty_complex_in_md", "beauty")
        self.display_basic_beauty_complex_references_in_md: str = options.get(
            "display_basic_beauty_complex_references_in_md", "beauty"
        )

        # for md
        self._pandoc_md_to = PandocMdTo(self.options)

        _options = {}
        _options["is_standardize_bib"] = False
        _options["is_display_implicit_comments"] = False
        _options.update(options)
        self._generate_library = ConvertStrToLibrary(_options)

    # for markdown files
    def special_operate_for_md(
        self,
        path_output: str,
        data_list_md: List[str],
        output_md_name: str,
        full_bib_for_abbr: str,
        full_bib_for_zotero: str,
        template_name: str = "article",
        generate_html: bool = False,
        generate_tex: bool = True
    ) -> Tuple[List[str], List[str]]:
        """Markdown."""
        path_temp = os.path.join(path_output, "{}".format(time.strftime("%Y_%m_%d_%H_%M_%S")))
        if not os.path.exists(path_temp):
            os.makedirs(path_temp)

        # write original md content to temp file
        full_temp_md = os.path.join(path_temp, output_md_name)
        write_list(data_list_md, full_temp_md, "w", None, False)

        # pandoc md to md to update md content
        if read_list(full_bib_for_abbr, "r") and read_list(full_bib_for_zotero, "r"):
            data_list_md = self._special_operate_for_md(
                output_md_name, path_temp, full_bib_for_abbr, full_bib_for_zotero
            )
        elif os.path.exists(full_bib_for_abbr) and os.path.exists(full_bib_for_zotero):
            print(f"The content of bib: {full_bib_for_abbr} or {full_bib_for_zotero} is empty.")
        else:
            pass

        # main name
        main_name = self.final_output_main_md_name
        if len(main_name) == 0:
            main_name = output_md_name.split(".md")[0] + "_" + self.replace_by_basic_beauty_complex_in_md
            main_name = main_name + "_" + self.display_basic_beauty_complex_references_in_md + ".md"
        if main_name.lower() == output_md_name.lower():
            main_name = main_name.split(".md")[0] + "_.md"
        if main_name[-3:] != ".md":
            main_name = main_name + ".md"

        # write new generated md content to given file
        write_list(data_list_md, main_name, "w", path_output, False)

        # for generating html file from md file
        if data_list_md and generate_html:
            self._pandoc_md_to.pandoc_md_to_html(
                path_output, path_output, main_name, f'{main_name.split(".md")[0]}.html', True
            )

        # pandoc md to latex
        data_list_tex = []
        if generate_tex:
            n5 = "5_pandoc" + ".tex"
            data_list_tex = self._pandoc_md_to.pandoc_md_to_tex(template_name, path_temp, path_temp, output_md_name, n5)

        # delete temp path
        if self.delete_temp_generate_md:
            shutil.rmtree(path_temp)
        return data_list_md, data_list_tex

    def _special_operate_for_md(
        self,
        output_md_name: str,
        path_temp: str,
        full_bib_for_abbr: str,
        full_bib_for_zotero: str,
    ) -> List[str]:
        # pandoc markdown to markdown
        n1 = "1_pandoc" + ".md"
        data_list_md = self._pandoc_md_to.pandoc_md_to_md(full_bib_for_abbr, path_temp, path_temp, output_md_name, n1)

        # use zotero bib to generate library
        bib_for_zotero = read_list(full_bib_for_zotero, "r")
        library = self._generate_library.generate_library(bib_for_zotero)

        _options = {}
        _options.update(self.options)
        _options["add_index_to_enties"] = False
        _python_writers = PythonWriters(_options)
        key_url_http_bib_dict = _python_writers.output_key_url_http_bib_dict(library)

        content_md = []
        if data_list_md and key_url_http_bib_dict:
            key_basic_dict, key_beauty_dict, key_complex_dict = self._pandoc_md_to.generate_key_data_dict(
                data_list_md, key_url_http_bib_dict
            )

            key_in_md = list(key_url_http_bib_dict.keys())

            # generate by replacing `- [@citation_key]` to `- [citation_key]`
            content = read_list(output_md_name, "r", path_temp)
            if self.replace_cite_to_fullcite_in_md:
                regex = re.compile(r"(\s*[-\+\*]\s*)\[@({})\]".format("|".join(key_in_md)))
                for i in range(len(content)):
                    if not (mch := regex.match(content[i])):
                        continue

                    content[i] = content[i].replace(mch.group(), mch.group(1) + "[" + mch.group(2) + "]")
            n2 = "2_generate" + ".md"
            write_list(content, n2, "w", path_temp)

            # pandoc markdown to markdown
            n3 = "3_pandoc" + ".md"
            data_list_md = self._pandoc_md_to.pandoc_md_to_md(full_bib_for_abbr, path_temp, path_temp, n2, n3)

            # generate by replacing `- [citation_key]` to `- reference`
            if self.replace_cite_to_fullcite_in_md:
                regex = re.compile(r"(\s*)([-\+\*])(\s*)[\\]*\[({})[\\]*\]".format("|".join(key_in_md)))
                for i in range(len(data_list_md)):
                    if not (mch := regex.search(data_list_md[i])):
                        continue

                    space_one, b, space_two, cite_key = mch.groups()
                    if self.replace_by_basic_beauty_complex_in_md.lower() == "basic":
                        temp_list = copy.deepcopy(key_basic_dict[cite_key])
                    elif self.replace_by_basic_beauty_complex_in_md.lower() == "complex":
                        temp_list = copy.deepcopy(key_complex_dict[cite_key])
                    else:
                        temp_list = copy.deepcopy(key_beauty_dict[cite_key])

                    temp = "".join(self._special_format(temp_list, space_one, space_two))
                    data_list_md[i] = data_list_md[i].replace(mch.group(), space_one + b + space_two + temp.strip())
            n4 = "4_generate" + ".md"
            write_list(data_list_md, os.path.join(path_temp, n4), "w")

            # obtain footnote part (in the last part of the contents)
            main_part, last_part = [], []
            main_part_flag, last_part_flag = True, True
            for line_index in range(len(data_list_md)):
                if main_part_flag and re.match(r"#+ References\s[\[{]", data_list_md[line_index]):
                    main_part_flag = False
                    main_part = delete_empty_lines_last_occur_add_new_line(data_list_md[:line_index])
                if last_part_flag and re.match(r"^\[\^1]: ", data_list_md[line_index]):
                    last_part_flag = False
                    last_part = delete_empty_lines_last_occur_add_new_line(data_list_md[line_index:])

            if main_part_flag:
                main_part = delete_empty_lines_last_occur_add_new_line(data_list_md)
            if self.add_reference_in_md:
                main_part.append("\n## References\n")
            if len(last_part) > 0:
                last_part.insert(0, "[//]: (Footnotes)\n\n")
                last_part.append("\n")

            # for bib
            bib_in_md = []
            if self.add_bib_in_md:
                temp_c = combine_content_in_list([key_url_http_bib_dict[k][2] for k in key_in_md])
                bib_in_md = combine_content_in_list([["<details>\n```\n"], temp_c, ["```\n</details>\n"]])

            # Generate basic/beauty/complex markdown content
            if dct := eval(f"key_{self.display_basic_beauty_complex_references_in_md}_dict"):
                content_md = self._generate_content_md(dct, key_in_md, main_part, last_part, bib_in_md)
        return content_md

    @staticmethod
    def _special_format(temp_list: List[str], space_one: str, space_two: str) -> List[str]:
        # special format for alignment
        for j in range(len(temp_list) - 1):
            if temp_list[j][-1] == "\n":
                temp_list[j + 1] = (space_one + " " + space_two) + temp_list[j + 1]
        return temp_list

    def _generate_content_md(
        self,
        key_basic_beauty_complex_dict: Dict[str, List[str]],
        key_in_md_tex: List[str],
        main_part: List[str],
        last_part: List[str],
        bib_in_md: List[str],
    ) -> List[str]:
        temp_b = []
        if self.add_reference_in_md:
            temp_b = combine_content_in_list([key_basic_beauty_complex_dict[k] for k in key_in_md_tex], ["\n"])
        content_md = combine_content_in_list([main_part, ["\n"], temp_b, last_part, bib_in_md])
        return content_md
