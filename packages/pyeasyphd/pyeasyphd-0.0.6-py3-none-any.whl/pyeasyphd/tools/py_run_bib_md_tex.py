import os
import re
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

from pyadvtools import (
    combine_content_in_list,
    read_list,
    standard_path,
    write_list,
)

from ..bib.bibtexparser import Library
from ..main import BasicInput, PythonRunBib, PythonRunMd, PythonRunTex, PythonWriters


class PyRunBibMdTex(BasicInput):
    """A class for processing BibTeX, Markdown and LaTeX files with various operations.

    This class provides functionality to handle references, figures, and content conversion
    between Markdown and LaTeX formats.
    """

    def __init__(
        self, path_output: str, tex_md_flag: str = ".md", template_name: str = "paper", options: Dict[str, Any] = {}
    ) -> None:
        """Initialize the PyRunBibMdTex instance.

        Parameters
        ----------
        path_output : str
            Output directory path for processed files
        tex_md_flag : str, optional
            Flag indicating whether to process as LaTeX (".tex") or Markdown (".md"),
            by default ".md"
        template_name : str, optional
            Template type to use ("paper" or "beamer"), by default "paper"
        options : Dict[str, Any], optional
            Additional configuration options, by default {}

        Raises
        ------
        AssertionError
            If tex_md_flag is not ".tex" or ".md"
            If template_name is not "paper" or "beamer"
        """
        super().__init__(options)

        self.tex_md_flag = re.sub(r"\.+", ".", "." + tex_md_flag)
        assert self.tex_md_flag in [".tex", ".md"], f"{tex_md_flag} must be `.tex` or `.md`."
        self.template_name = template_name.lower()
        assert self.template_name in ["paper", "beamer"], f"{template_name} must be `paper` or `beamer`."
        self.path_output = standard_path(path_output)

        # Configuration options
        self.generate_html = options.get("generate_html", False)
        self.generate_tex = options.get("generate_tex", True)
        self.shutil_figures = options.get("shutil_figures", True)

        # Folder name configurations
        self.figure_folder_name = options.get("figure_folder_name", "fig")  # "" or "figs" or "main"
        self.bib_folder_name = options.get("bib_folder_name", "bib")  # "" or "bibs" or "main"
        self.md_folder_name = options.get("md_folder_name", "md")  # "" or "mds" or "main"
        self.tex_folder_name = options.get("tex_folder_name", "tex")  # "" or "texes" or "main"

        # Cleanup options
        self.delete_original_md_in_output_folder = options.get("delete_original_md_in_output_folder", False)
        self.delete_original_tex_in_output_folder = options.get("delete_original_tex_in_output_folder", False)
        self.delete_original_bib_in_output_folder = options.get("delete_original_bib_in_output_folder", False)

        # Initialize helper classes
        self._python_bib = PythonRunBib(self.options)
        self._python_md = PythonRunMd(self.options)
        self._python_tex = PythonRunTex(self.options)
        self._python_writer = PythonWriters(self.options)

    def run_files(
        self, file_list_md_tex: List[str], output_prefix: str = "", output_level: str = "next"
    ) -> Tuple[List[str], List[str]]:
        """Process a list of Markdown or LaTeX files.

        Parameters
        ----------
        file_list_md_tex : List[str]
            List of input file paths (Markdown or LaTeX)
        output_prefix : str, optional
            Prefix for output files, by default ""
        output_level : str, optional
            Output directory level ("previous", "current", or "next"), by default "next"

        Returns
        -------
        Tuple[List[str], List[str]]
            Tuple containing processed Markdown content and LaTeX content
        """
        file_list_md_tex = [f for f in file_list_md_tex if f.endswith(self.tex_md_flag)]
        data_list_list = [read_list(standard_path(f), "r") for f in file_list_md_tex]
        if all([len(data_list) == 0 for data_list in data_list_list]):
            return [], []

        file_base_name = os.path.splitext(os.path.basename(file_list_md_tex[0]))[0]
        output_prefix = output_prefix if output_prefix else file_base_name

        data_list_md_tex = combine_content_in_list(data_list_list, ["\n"])

        content_md, content_tex = self.python_run_bib_md_tex(
            output_prefix, data_list_md_tex, self.path_bibs, output_level
        )
        return content_md, content_tex

    def python_run_bib_md_tex(
        self,
        output_prefix: str,
        data_list_md_tex: List[str],
        original_bib_data: Union[List[str], str, Library],
        output_level: str = "next",
    ) -> Tuple[List[str], List[str]]:
        """Process BibTeX, Markdown and LaTeX content.

        Parameters
        ----------
        output_prefix : str
            Prefix for output files
        data_list_md_tex : List[str]
            List of content lines (Markdown or LaTeX)
        original_bib_data : Union[List[str], str, Library]
            BibTeX data in various formats
        output_level : str, optional
            Output directory level ("previous", "current", or "next"), by default "next"

        Returns
        -------
        Tuple[List[str], List[str]]
            Tuple containing processed Markdown content and LaTeX content
        """
        # Basic file names
        output_tex, output_md = output_prefix + ".tex", output_prefix + ".md"

        if len(data_list_md_tex) == 0:
            original_bib_data = self._python_bib.parse_to_single_standard_library(original_bib_data)
            if not original_bib_data.entries:
                return [], []

            data_list_md_tex = []
            for entry in original_bib_data.entries:
                data_list_md_tex.append(f"- [@{entry.key}]\n\n")
            data_list_md_tex.insert(0, f"## {output_prefix} - {len(data_list_md_tex)}\n\n")

        # Determine output path based on level
        if output_level == "previous":
            path_output = os.path.dirname(self.path_output)
        elif output_level == "next":
            path_output = os.path.join(self.path_output, output_prefix)
        elif output_level == "current":
            path_output = self.path_output
        else:
            path_output = self.path_output

        if not os.path.exists(path_output):
            os.makedirs(path_output)
        self.path_output = standard_path(path_output)

        return self._python_run_bib_md_tex(output_md, output_tex, data_list_md_tex, original_bib_data)

    def _python_run_bib_md_tex(
        self,
        output_md: str,
        output_tex: str,
        data_list_md_tex: List[str],
        original_bib_data: Union[List[str], str, Library],
    ) -> Tuple[List[str], List[str]]:
        """Process BibTeX, Markdown and LaTeX content.

        Parameters
        ----------
        output_md : str
            Output Markdown filename
        output_tex : str
            Output LaTeX filename
        data_list_md_tex : List[str]
            List of content lines (Markdown or LaTeX)
        original_bib_data : Union[List[str], str, Library]
            BibTeX data in various formats

        Returns
        -------
        Tuple[List[str], List[str]]
            Tuple containing processed Markdown content and LaTeX content
        """
        # Copy figures if enabled
        if self.shutil_figures:
            figure_names = self.search_figure_names(data_list_md_tex)
            self.shutil_copy_figures(self.figure_folder_name, self.path_figures, figure_names, self.path_output)

        # Extract citation keys from content
        key_in_md_tex = self.search_cite_keys(data_list_md_tex, self.tex_md_flag)

        # Process bibliography
        full_bib_for_zotero, full_bib_for_abbr, full_bib_for_save = "", "", ""
        if key_in_md_tex:
            # Generate bib contents
            abbr_library, zotero_library, save_library = self._python_bib.parse_to_multi_standard_library(
                original_bib_data, key_in_md_tex
            )
            key_in_md_tex = sorted(list(abbr_library.entries_dict.keys()), key=key_in_md_tex.index)

            # Write bibliography files
            _path_output = os.path.join(self.path_output, self.bib_folder_name)
            full_bib_for_abbr, full_bib_for_zotero, full_bib_for_save = self._python_writer.write_multi_library_to_file(
                _path_output, abbr_library, zotero_library, save_library, key_in_md_tex
            )

        # Process content based on format
        if self.tex_md_flag == ".md":
            # Write original markdown content
            write_list(data_list_md_tex, output_md, "w", os.path.join(self.path_output, self.md_folder_name), False)

            # Generate processed content and write to given files
            data_list_md, data_list_tex = self._python_md.special_operate_for_md(
                self.path_output,
                data_list_md_tex,
                output_md,
                full_bib_for_abbr,
                full_bib_for_zotero,
                self.template_name,
                self.generate_html,
                self.generate_tex,
            )
        else:
            data_list_md, data_list_tex = [], data_list_md_tex

        # Generate LaTeX output if enabled
        if self.generate_tex:
            self._python_tex.generate_standard_tex_data_list(
                data_list_tex,
                output_tex,
                self.path_output,
                self.figure_folder_name,
                self.tex_folder_name,
                self.bib_folder_name,
                os.path.basename(full_bib_for_abbr),
                self.template_name,
            )

        # Cleanup original files if enabled
        if self.delete_original_md_in_output_folder:
            self._cleanup_file(os.path.join(self.path_output, self.md_folder_name, output_md))

        if self.delete_original_tex_in_output_folder:
            self._cleanup_file(os.path.join(self.path_output, self.tex_folder_name, output_tex))

        if self.delete_original_bib_in_output_folder:
            for file in [full_bib_for_abbr, full_bib_for_zotero, full_bib_for_save]:
                self._cleanup_file(file)

        return data_list_md, data_list_tex

    @staticmethod
    def search_figure_names(data_list: List[str], figure_postfixes: Optional[List[str]] = None) -> List[str]:
        """Search for figure filenames in content.

        Parameters
        ----------
        data_list : List[str]
            List of content lines to search
        figure_postfixes : Optional[List[str]], optional
            List of figure file extensions to look for, by default None

        Returns
        -------
        List[str]
            List of found figure filenames
        """
        if figure_postfixes is None:
            figure_postfixes = ["eps", "jpg", "png", "svg", "psd", "raw", "jpeg", "pdf"]

        regex = re.compile(rf'[\w\-]+\.(?:{"|".join(figure_postfixes)})', re.I)
        figure_names = []
        for line in data_list:
            figure_names.extend(regex.findall(line))
        return sorted(set(figure_names), key=figure_names.index)

    @staticmethod
    def shutil_copy_figures(fig_folder_name: str, path_fig: str, fig_names: List[str], path_output: str) -> None:
        """Copy figure files to output directory.

        Parameters
        ----------
        fig_folder_name : str
            Name of figures folder in output directory
        path_fig : str
            Source directory containing figures
        fig_names : List[str]
            List of figure filenames to copy
        path_output : str
            Output directory path

        Returns
        -------
        None
        """
        if not os.path.exists(path_fig):
            print(f"{path_fig} does not existed.")
            return None

        file_list = []
        for root, _, files in os.walk(path_fig, topdown=False):
            for name in files:
                if name in fig_names:
                    file_list.append(os.path.join(root, name))

        for file in file_list:
            path_output_file = os.path.join(path_output, fig_folder_name, os.path.basename(file))
            p = os.path.dirname(path_output_file)
            if not os.path.exists(p):
                os.makedirs(p)
            shutil.copy(file, path_output_file)
        return None

    @staticmethod
    def search_cite_keys(data_list: List[str], tex_md_flag: str = ".tex") -> List[str]:
        r"""Extract citation keys from content according to their places.

        Parameters
        ----------
        data_list : List[str]
            List of content lines to search
        tex_md_flag : str, optional
            Flag indicating content format (".tex" or ".md"), by default ".tex"

        Returns
        -------
        List[str]
            List of found citation keys

        Notes
        -----
        For LaTeX, searches for \\cite, \\citep, \\citet patterns
        For Markdown, searches for [@key], @key; and ;@key] patterns
        """
        cite_key_list = []
        if tex_md_flag == ".tex":
            regex_list = [re.compile(r"\\[a-z]*cite[tp]*{\s*([\w\-.,:/\s]*)\s*}")]
            cite_key_list.extend(regex_list[0].findall("".join(data_list)))
            cite_key_list = combine_content_in_list([re.split(",", c) for c in cite_key_list])
        elif tex_md_flag == ".md":
            regex_list = [
                re.compile(r"\[@([\w\-.:/]+)\]"),
                re.compile(r"@([\w\-.:/]+)\s*;"),
                re.compile(r";\s*@([\w\-.:/]*)\s*]"),
            ]
            cite_key_list = combine_content_in_list(
                [regex_list[i].findall("".join(data_list)) for i in range(len(regex_list))]
            )
        else:
            print(f"{tex_md_flag} must be `.tex` or `.md`.")

        cite_key_list = [c.strip() for c in cite_key_list if c.strip()]
        return sorted(set(cite_key_list), key=cite_key_list.index)

    def _cleanup_file(self, file_path: str) -> None:
        """Cleanup files and empty directories.

        Parameters
        ----------
        file_path : str
            Path to file to be removed

        Returns
        -------
        None
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            dir_path = os.path.dirname(file_path)
            if dir_path != self.path_output:  # Don't remove the main output directory
                if len([f for f in os.listdir(dir_path) if f != ".DS_Store"]) == 0:
                    shutil.rmtree(dir_path)
