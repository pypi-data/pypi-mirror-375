import os
import re

from pyadvtools import (
    combine_content_in_list,
    read_list,
    write_list,
)

html_head = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{}</title>
"""

html_style = """  <style>
    html {font-size: 22px;}
    body {margin: 0 auto; max-width: 76em;}
    #copyID {font-size: 18px;}
  </style>
  <script>
    function copy(element) {
      if (element.type == "button"){
      element.type="text";
      }
      element.style.color="black";
      element.style.backgroundColor="#C7EDCC";
      element.select();
      element.setSelectionRange(0, 99999);
      navigator.clipboard.writeText(element.value);
      window.getSelection().removeAllRanges();
      element.type="button";
    }
  </script>
</head>
<body>
"""

html_tail = """
</body>
</html>
"""

textarea_header = '<textarea id="copyID" onclick="copy(this)" rows="16" cols="145">\n'
textarea_tail = "\n</textarea>"


def operate_on_generate_html(html_name: str) -> None:
    if not (data_list := read_list(html_name, "r", None)):
        return None

    head_list = [html_head.format(os.path.basename(html_name).split('.')[0].strip()), html_style, "\n"]
    tail_list = [html_tail]

    content = "".join(data_list)
    content = content.replace("<pre><code>", textarea_header).replace("</code></pre>", textarea_tail)
    for i in re.findall(r"<li>(.*?)<details>", content, re.DOTALL):
        content = content.replace(rf"<li>{i}<details>", f"<li><details>\n<summary>\n{i.strip()}\n</summary>")
    data_list = combine_content_in_list([head_list, [content], tail_list])
    write_list(data_list, html_name, "w", None, False)
    return None
