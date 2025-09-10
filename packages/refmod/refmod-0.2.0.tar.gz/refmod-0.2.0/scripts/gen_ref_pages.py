"""
Generate the code reference pages and navigation.
Note:
    Source: [mkdocstrings recepies](https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages)
"""

from pathlib import Path
import mkdocs_gen_files

SRC_DIR = "refmod"
src = Path(__file__).parent.parent / SRC_DIR
nav = mkdocs_gen_files.Nav()

for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = list(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        if len(parts) == 0:
            doc_path = doc_path.with_name("summary.md")
            full_doc_path = full_doc_path.with_name("summary.md")
        else:
            continue
    elif parts[-1] == "__main__":
        continue

    if len(parts) == 0:
        parts = [
            SRC_DIR.upper(),
        ]

    # The style tag removes the title:
    # https://github.com/squidfunk/mkdocs-material/issues/2163#issuecomment-752916358
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(
            f"""---
            comments: true
            ---
            <style>
              .md-typeset h1,
              .md-content__button {{
                display: none;
              }}
            </style> 
            ::: {ident}""".replace("    ", "")
        )

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

    for i, part in enumerate(parts):
        parts[i] = part.replace("_", " ").lower()
        # parts[i] = part.replace("_", " ").title()

    nav[parts] = doc_path.as_posix()

with mkdocs_gen_files.open("reference/summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
