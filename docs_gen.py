import pdoc
import sys
import os
from pathlib import Path
import shutil


def copy_preload(path_out: Path) -> None:
    template_dir = Path("docs/templates/preload")
    path_out.mkdir(parents=True, exist_ok=True)
    for item in template_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(template_dir)
            dest_path = path_out / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)
    print(f"Preloaded templates into {path_out}")


def generate_docs(is_read_the_docs: bool = False) -> None:
    modules = ["mbbank"]
    output_dir = Path(
        "docs" if not is_read_the_docs else os.getenv("READTHEDOCS_OUTPUT") + "/html/"
    )
    pdoc.render.configure(
        docformat="google",
        show_source=True,
        include_undocumented=False,
        template_directory="docs/templates",
    )
    pdoc.pdoc(*modules, output_directory=output_dir)
    copy_preload(output_dir)
    print(f"Documentation generated in {output_dir.absolute()}")


if __name__ == "__main__":
    is_read_the_docs = "--rtfd" in sys.argv
    generate_docs(is_read_the_docs)
