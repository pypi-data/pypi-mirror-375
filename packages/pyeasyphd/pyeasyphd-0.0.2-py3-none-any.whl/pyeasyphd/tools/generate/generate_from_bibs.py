import os
import re
from typing import Any, Dict, List, Union

from pyadvtools import IterateSortDict, standard_path, write_list

from ...bib.bibtexparser import Entry, Library
from ...main import PandocMdTo, PythonRunBib, PythonWriters
from ...utils.utils import html_head, html_style, html_tail, textarea_header, textarea_tail
from ..experiments_base import generate_standard_publisher_abbr_options_dict


def preparation(
    path_storage: str,
    path_output: str,
    output_basename: str,
    pub_type: str,
    issue_or_month_flag: Union[str, List[str]] = "current_issue",
    year_flag: Union[str, List[str]] = "current_year",
    options: Dict[str, Any] = {},
):
    """Prepare paths and flags for data generation.

    Examples
    --------
    |              | current_issue | last_issue | current_month | last_month | given_month | given_months | all_months |
    |--------------|---------------|------------|---------------|------------|-------------|--------------|------------|
    | current_year |               |            |               |            | "2"         | ["1", "3"]   |            |
    | given_year   | "2020"        |            |               |            |             |              |            |
    | given_years  | ["2025"]      |            |               |            |             |              |            |
    | all_years    |               |            |               |            |             |              |            |

    Returns
    -------
    Tuple[str, str, bool]
        Returns (path_root, path_output, combine_flag)
    """
    # default settings
    path_storage = standard_path(path_storage)
    path_output = standard_path(path_output)

    # "absolute_path" or "relative_path"
    absolute_or_relative_path = options.get("absolute_or_relative_path", "absolute_path")

    # Create path components
    yy = "-".join(year_flag) if isinstance(year_flag, List) else year_flag
    im = "-".join(issue_or_month_flag) if isinstance(issue_or_month_flag, List) else issue_or_month_flag

    if options.get("early_access", False):
        base_path = f"{output_basename}/{pub_type.title()}_Early_Access/{yy}_{im}"
        path_output = os.path.join(path_output + "_Early_Access", f"{yy}_{im}")
    else:
        base_path = f"{output_basename}/{pub_type.title()}/{yy}_{im}"
        path_output = os.path.join(path_output, f"{yy}_{im}")

    path_root = base_path if absolute_or_relative_path == "absolute_path" else ""

    # Determine combine flag
    b = options.get("early_access", False) and (year_flag != "all_years")
    c = year_flag == "current_year"
    c = c and (not isinstance(issue_or_month_flag, list)) and (issue_or_month_flag != "all_months")
    combine_flag = b or c

    return path_root, path_output, combine_flag


def generate_from_bibs_and_write(
    path_storage: str,
    path_output: str,
    output_basename: str,
    pub_type: str,
    generate_or_combine: str,
    year_flag: Union[str, List[str]] = "current_year",
    issue_or_month_flag: Union[str, List[str]] = "current_issue",
    options: Dict[str, Any] = {},
) -> None:
    """Generate or combine data from bibliographies.

    Parameters
    ----------
    path_storage : str
        Path to storage directory
    path_output : str
        Path to output directory
    generate_or_combine : str
        Either "generate_data" or "combine_data"
    year_flag : Union[str, List[str]], optional
        Flag for year selection, by default "current_year"
    issue_or_month_flag : Union[str, List[str]], optional
        Flag for issue/month selection, by default "current_issue"
    options : Dict[str, Any], optional
        Additional options, by default {}
    """
    path_root, path_output, combine_flag = preparation(
        path_storage, path_output, output_basename, pub_type, issue_or_month_flag, year_flag, options
    )

    if generate_or_combine == "generate_data":
        publisher_abbr_dict = generate_standard_publisher_abbr_options_dict(path_storage, options)
        for publisher in publisher_abbr_dict:
            pp = os.path.join(path_output, publisher.lower())

            publisher_html_body = []
            for abbr in publisher_abbr_dict[publisher]:
                print(f"*** Processing {publisher.upper()}: {abbr} ***")
                new_options = publisher_abbr_dict[publisher][abbr]

                # Get bibliography path
                path_abbr = os.path.join(path_storage, f"{publisher.lower()}/{abbr}")
                if isinstance(year_flag, str) and year_flag.isdigit():
                    for root, _, files in os.walk(path_abbr, topdown=True):
                        files = [f for f in files if f.endswith(".bib")]
                        if files := [f for f in files if re.search(f"_{year_flag}.bib", f)]:
                            path_abbr = os.path.join(root, files[0])

                # Generate and process library
                library = generate_given_library(path_abbr, issue_or_month_flag, year_flag, new_options)

                # Generate md, tex, pdf, html
                html_body = generate_md_tex_pdf_html(abbr, library, pp, new_options)
                if combine_flag and html_body:
                    publisher_html_body.extend(html_body + ["\n"])

            # Combine for publisher
            if publisher_html_body:
                html_content = _html_content(publisher_html_body[:-1], publisher)
                write_list(html_content, f"{publisher}_all.html", "w", pp, False)

    elif generate_or_combine == "combine_data":
        # Compulsory
        options["include_abbr_list"] = []
        options["exclude_abbr_list"] = []
        publisher_abbr_dict = generate_standard_publisher_abbr_options_dict(path_storage, options)
        for publisher in publisher_abbr_dict:
            print(f"*** Combining papers for {publisher.upper()} ***")
            pp = os.path.join(path_output, publisher.lower())
            absolute_path = f"{path_root}/{publisher}" if len(path_root) > 0 else ""

            link = [f"# {publisher.upper()}\n\n"]
            for abbr in publisher_abbr_dict[publisher]:
                if os.path.exists(os.path.join(pp, abbr, f"{abbr}.html")):
                    link.append(f"- [{abbr}]({absolute_path}/{abbr}/{abbr}.html)\n")

            if combine_flag:
                link.insert(1, f"- [All Journals]({absolute_path}/{publisher}_all.html)\n")

            # Process combined content
            if len(link) > 1:
                write_list(link, f"{publisher}_link.md", "w", pp, False)
                PandocMdTo({}).pandoc_md_to_html(pp, pp, f"{publisher}_link.md", f"{publisher}_link.html", True)

            # Clean up
            for name in ["_link"]:
                if os.path.exists(file := os.path.join(pp, f"{publisher}{name}.md")):
                    os.remove(file)
    return None


def generate_given_library(
    original_data: Union[List[str], str, Library],
    issue_or_month_flag: Union[str, List[str]],
    year_flag: Union[str, List[str]] = "current_year",
    options: Dict[str, Any] = {},
) -> Library:
    """Generate a Library object from input data with given filters.

    Parameters
    ----------
    original_data : Union[List[str], str, Library]
        Input bibliography data
    issue_or_month_flag : Union[str, List[str]]
        Flag for issue/month selection
    year_flag : Union[str, List[str]], optional
        Flag for year selection, by default "current_year"
    options : Dict[str, Any], optional
        Additional options, by default {}

    Returns
    -------
    Library
        Processed library object
    """
    _options = {}
    # convert_str_to_library
    _options["is_standardize_bib"] = False  # default is True
    # middlewares_str_to_library.py
    _options["is_display_implicit_comments"] = False  # default is True

    # convert_library_to_library.py
    _options["choose_abbr_zotero_save"] = "save"  # default is "save"
    # middlewares_library_to_library.py
    _options["generate_entry_cite_keys"] = False  # default is False
    _options["function_common_again"] = False  # default is True
    _options["function_common_again_abbr"] = False  # default is True
    _options["function_common_again_zotero"] = False  # default is True
    _options["function_common_again_save"] = False  # default is True

    # convert_library_to_str.py
    # middlewares_library_to_str.py
    _options["is_sort_entry_fields"] = True  # compulsory
    _options["is_sort_blocks"] = True  # compulsory
    _options["sort_entries_by_field_keys_reverse"] = True  # compulsory

    # convert_str_to_str.py
    _options["default_additional_field_list"] = []
    # middlewares_str_to_str.py
    _options["substitute_in_bib"] = False  # default is True

    _options.update(options)
    _python_bib = PythonRunBib(_options)

    # Generate nested entries dictionary
    entry_type_year_volume_number_month_entry_dict = _python_bib.parse_to_nested_entries_dict(original_data)
    old_dict = entry_type_year_volume_number_month_entry_dict

    # Filter by year_flag
    new_dict = {}
    for entry_type in old_dict:
        years = [year for year in old_dict[entry_type]]

        # Update years
        if isinstance(year_flag, List):
            years = sorted(list(set(years).intersection(set(year_flag))))
        elif year_flag.lower().strip() == "all_years":
            years = years
        elif year_flag.lower().strip() == "current_year":
            years = years[:1]
        else:
            if year_flag not in years:
                continue
            else:
                years = [year_flag]

        for year in years:
            new_dict.setdefault(entry_type, {}).update({year: old_dict[entry_type][year]})

    # Filter by issue/month flag
    if issue_or_month_flag in ["current_issue", "last_issue"]:
        return obtain_issue_flag_library(new_dict, issue_or_month_flag)

    return obtain_month_flag_library(new_dict, issue_or_month_flag)


def obtain_issue_flag_library(
    old_dict: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, List[Entry]]]]]], issue_flag: str = "current_issue"
) -> Library:
    """Filter library by issue flag."""
    old_dict = IterateSortDict(True).dict_update(old_dict)

    entries = []
    for entry_type in old_dict:
        for year in old_dict[entry_type]:
            temp_dict = old_dict[entry_type][year]

            # Article entries
            if entry_type.lower() == "article":
                volumes, numbers, months = [], [], []
                for volume in (volumes := [volume for volume in temp_dict]):
                    for number in (numbers := [number for number in temp_dict[volume]]):
                        months = [month for month in temp_dict[volume][number]]
                        break
                    break

                if issue_flag == "current_issue":  # current volume, current issue, and current month
                    entries.extend(temp_dict[volumes[0]][numbers[0]][months[0]])

                elif issue_flag == "last_issue":
                    # Logic for getting previous issue
                    if len(months) == 1:
                        if len(numbers) == 1:
                            if len(volumes) == 1:
                                entries.extend(temp_dict[volumes[0]][numbers[0]][months[0]])
                            else:
                                numbers = [number for number in temp_dict[volumes[1]]]
                                months = [month for month in temp_dict[volumes[1]][numbers[0]]]
                                entries.extend(temp_dict[volumes[1]][numbers[0]][months[0]])
                        else:
                            months = [month for month in temp_dict[volumes[0]][numbers[1]]]
                            entries.extend(temp_dict[volumes[0]][numbers[1]][months[0]])
                    else:
                        entries.extend(temp_dict[volumes[0]][numbers[0]][months[1]])

                else:
                    print(f"Unknown issue flag: {issue_flag}.")

            else:
                # Non-article entries
                for volume in temp_dict:
                    for number in temp_dict[volume]:
                        for month in temp_dict[volume][number]:
                            entries.extend(temp_dict[volume][number][month])

    return Library(entries)


def obtain_month_flag_library(
    old_dict: Dict[str, Dict[str, Dict[str, Dict[str, Dict[str, List[Entry]]]]]],
    month_flag: Union[str, List[str]] = "current_month",
) -> Library:
    """Filter library by month flag."""
    new_dict = {}
    for entry_type in old_dict:
        for year in old_dict[entry_type]:

            for volume in old_dict[entry_type][year]:
                for number in old_dict[entry_type][year][volume]:
                    for month in old_dict[entry_type][year][volume][number]:
                        new_dict.setdefault(entry_type, {}).setdefault(year, {}).setdefault(month, {}).setdefault(
                            volume, {}
                        ).setdefault(number, []).extend(old_dict[entry_type][year][volume][number][month])

    # Sort
    old_dict = IterateSortDict(True).dict_update(new_dict)

    entries = []
    for entry_type in old_dict:
        for year in old_dict[entry_type]:
            temp_dict = old_dict[entry_type][year]
            default_months = [month for month in temp_dict]

            # Update month
            new_months = []
            if month_flag == "current_month":  # current_month
                new_months = [default_months[0]]
            elif month_flag == "last_month":  # last_month
                new_months = [default_months[1]] if len(default_months) > 1 else []
            elif month_flag == "all_months":  # all months
                new_months = default_months
            else:
                if isinstance(month_flag, str):  # given month
                    if month_flag in default_months:
                        new_months = [month_flag]
                else:
                    for month in month_flag:  # given months
                        if month in default_months:
                            new_months.append(month)

            for month in new_months:
                for volume in temp_dict[month]:
                    for number in temp_dict[month][volume]:
                        entries.extend(temp_dict[month][volume][number])

    return Library(entries)


def generate_md_tex_pdf_html(
    abbr_standard: str,
    original_bib_data: Union[List[str], str, Library],
    path_output: str,
    options: Dict[str, Any] = {},
) -> List[str]:
    """Generate markdown and LaTeX from bibliography data."""
    options_: dict = {
        # convert_str_to_library
        "is_standardize_bib": False,
        # middlewares_str_to_library.py
        "is_display_implicit_comments": False,
        #
        # convert_library_to_library.py
        # middlewares_library_to_library.py
        "function_common_again": False,
        "function_common_again_abbr": False,
        "function_common_again_zotero": False,
        "function_common_again_save": False,
        "abbr_index_article_for_abbr": 2,
        "abbr_index_inproceedings_for_abbr": 2,
        #
        # convert_library_to_str.py
        "empty_entry_cite_keys": True,
        # middlewares_library_to_str.py
        "is_sort_entry_fields": True,
        "is_sort_blocks": True,
        "sort_entries_by_field_keys_reverse": True,
    }
    options_.update(options)

    # Process bibliography data
    _python_bib = PythonRunBib(options_)
    _, zotero_library, _ = _python_bib.parse_to_multi_standard_library(original_bib_data)

    _python_writer = PythonWriters(options_)

    # Generate HTML content body
    html_body = []
    for entry in zotero_library.entries:
        html_body.append(_format_entry(entry, abbr_standard, _python_writer.write_to_str([entry])))

    if len(html_body) > 0:
        html_body = (
            [f'<h2 id="{abbr_standard.lower()}">{abbr_standard} - {len(zotero_library.entries)}</h2>\n', "<ul>\n"]
            + html_body
            + ["</ul>\n"]
        )

        html_content = _html_content(html_body, abbr_standard)

        # Write output file
        write_list(html_content, f"{abbr_standard}.html", "w", os.path.join(path_output, abbr_standard), False)

    return html_body


def _html_content(html_body, abbr_standard):
    html_content = [html_head.format(abbr_standard), html_style, "\n"]
    html_content.extend(html_body)
    html_content.extend([html_tail])
    return html_content


def _format_entry(entry, abbr, data_list):
    """Format a single bibliography entry into HTML."""
    number = entry["number"] if "number" in entry else ""
    pages = entry["pages"] if "pages" in entry else ""
    title = entry["title"] if "title" in entry else ""
    year = entry["year"] if "year" in entry else ""
    volume = entry["volume"] if "volume" in entry else ""

    url = ""
    if "doi" in entry:
        doi = entry["doi"]
        url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
    elif "url" in entry:
        url = entry["url"]

    line = _format_entry_apa(title, year, volume, number, pages, url, abbr)

    line = f"<li><details>\n<summary>\n{line.strip()}\n</summary>\n"

    return line + textarea_header + "".join(data_list).rstrip() + textarea_tail + "\n</details></li>\n"


def _format_entry_apa(title, year, volume, number, pages, url, abbr):
    line = f"({year}). {title}. <em>{abbr}</em>"
    if volume:
        line += f", <em>{volume}</em>"
        if number:
            line += f"({number})"

    if pages:
        line += f", {pages}"

    line += "."

    if url:
        line += f" (<a href='{url}'>www</a>)"

    return line
