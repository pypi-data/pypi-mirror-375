import json
import os
from typing import Any, Dict

from pyadvtools import read_list, standard_path


class BasicInput(object):
    """Basic input.

    Args:
        options (Dict[str, Any]): Options.

    Attributes:
        path_bibs (str): Path bibs.
        path_figures (str): Path figures.
        path_templates (str): Path templates.

        full_abbr_article_dict (Dict[str, str]): Full abbr article dict.
        full_abbr_inproceedings_dict (Dict[str, str]): Full abbr inproceedings dict.
        full_names_in_json (str): Full names in json.
        abbr_names_in_json (str): Abbr names in json.

        full_csl_style_pandoc (str): Full path to csl style for pandoc.
        full_tex_article_template_pandoc (str): Full path to tex article template for pandoc.
        article_template_tex (List[str]): Article template for LaTex.

        article_template_header_tex (List[str]): Article template header for LaTex.
        article_template_tail_tex (List[str]): Article template tail for LaTex.
        beamer_template_header_tex (List[str]): Beamer template header for LaTex.
        beamer_template_tail_tex (List[str]): Beamer template tail for LaTex.
        tex_math_commands_tex (List[str]): Tex math commands for LaTex.
        tex_usepackages_tex (List[str]): Tex usepackages for LaTex.
        handly_preamble (bool): Handly preamble.

        options (Dict[str, Any]): Options.
    """

    def __init__(self, options: Dict[str, Any]) -> None:
        # The paths of Figures, Bibs, and Templates
        self.path_bibs: str = standard_path(options.get("path_bibs", ""))
        self.path_figures: str = standard_path(options.get("path_figures", ""))
        self.path_templates: str = standard_path(options.get("path_templates", ""))

        # Update
        path_config = standard_path(options.get("path_config", ""))
        if len(self.path_bibs) == 0:
            for folder in ["bib", "bibs", "Bib", "Bibs", "BIB", "BIBS"]:
                if os.path.exists(p := os.path.join(path_config, folder)):
                    self.path_bibs = p
                    break

        if len(self.path_figures) == 0:
            for folder in ["figure", "figures", "Figure", "Figures", "FIGURE", "FIGURES"]:
                if os.path.exists(p := os.path.join(path_config, folder)):
                    self.path_figures = p
                    break

        if len(self.path_templates) == 0:
            for folder in ["template", "templates", "Template", "Templates", "TEMPLATE", "TEMPLATES"]:
                if os.path.exists(p := os.path.join(path_config, folder)):
                    self.path_templates = p
                    break

        # bib/core
        self._initialize_middlewares(options)

        # main
        self._initialize_pandoc_md_to(options)
        self._initialize_python_run_tex(options)

        self.options = options

    # bib/core
    def _initialize_middlewares(self, options: Dict[str, Any]) -> None:
        full_json_c = os.path.join(self.path_templates, "AbbrFull", "conferences.json")
        full_json_j = os.path.join(self.path_templates, "AbbrFull", "journals.json")
        if os.path.isfile(full_json_c):
            with open(full_json_c, "r") as f:
                try:
                    json_dict = json.loads(f.read())
                except Exception as e:
                    print(e)
                    json_dict = {}
                full_abbr_inproceedings_dict = {p: json_dict[p].get("conferences", {}) for p in json_dict}
        else:
            full_abbr_inproceedings_dict = {}

        if os.path.isfile(full_json_j):
            with open(full_json_j, "r") as f:
                try:
                    json_dict = json.loads(f.read())
                except Exception as e:
                    print(e)
                    json_dict = {}
                full_abbr_article_dict = {p: json_dict[p].get("journals", {}) for p in json_dict}
        else:
            full_abbr_article_dict = {}

        inproceedings_dict = options.get("full_abbr_inproceedings_dict", {})
        if len(inproceedings_dict) == 0:
            inproceedings_dict = full_abbr_inproceedings_dict
        self.full_abbr_inproceedings_dict = full_abbr_inproceedings_dict

        article_dict = options.get("full_abbr_article_dict", {})
        if len(article_dict) == 0:
            article_dict = full_abbr_article_dict
        self.full_abbr_article_dict = full_abbr_article_dict

        full_names_in_json = options.get("full_names_in_json", "names_full")
        if len(full_names_in_json) == 0:
            full_names_in_json = "names_full"
        self.full_names_in_json = full_names_in_json

        abbr_names_in_json = options.get("abbr_names_in_json", "names_abbr")
        if len(abbr_names_in_json) == 0:
            abbr_names_in_json = "names_abbr"
        self.abbr_names_in_json = abbr_names_in_json

        options["full_abbr_article_dict"] = self.full_abbr_article_dict
        options["full_abbr_inproceedings_dict"] = self.full_abbr_inproceedings_dict

        options["full_names_in_json"] = self.full_names_in_json
        options["abbr_names_in_json"] = self.abbr_names_in_json

    # main
    def _initialize_pandoc_md_to(self, options: Dict[str, Any]) -> None:
        csl_name = options.get("csl_name", "apa-no-ampersand")
        if len(csl_name) == 0:
            csl_name = "apa-no-ampersand"
        self.full_csl_style_pandoc = os.path.join(self.path_templates, f"CSL/{csl_name}.csl")
        self.full_tex_article_template_pandoc = os.path.join(self.path_templates, "TEX/eisvogel.tex")

        self.article_template_tex = read_list(os.path.join(self.path_templates, "TEX/Article.tex"))

    def _initialize_python_run_tex(self, options: Dict[str, Any]) -> None:
        self.article_template_header_tex = read_list(os.path.join(self.path_templates, "TEX/Article_Header.tex"))
        self.article_template_tail_tex = read_list(os.path.join(self.path_templates, "TEX/Article_Tail.tex"))
        self.beamer_template_header_tex = read_list(os.path.join(self.path_templates, "TEX/Beamer_Header.tex"))
        self.beamer_template_tail_tex = read_list(os.path.join(self.path_templates, "TEX/Beamer_Tail.tex"))
        self.math_commands_tex = read_list(os.path.join(self.path_templates, "TEX/math_commands.tex"))
        self.usepackages_tex = read_list(os.path.join(self.path_templates, "TEX/Style.tex"))

        # handly preamble
        self.handly_preamble = options.get("handly_preamble", False)
        if self.handly_preamble:
            self.article_template_header_tex, self.article_template_tail_tex = [], []
            self.beamer_template_header_tex, self.beamer_template_tail_tex = [], []
            self.math_commands_tex, self.usepackages_tex = [], []
