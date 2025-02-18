import asyncio
import os

from griffe import Docstring
from griffe import DocstringSectionKind
from mbbank import MBBank, MBBankAsync, CapchaOCR, CapchaProcessing


def parse_doc(class_doc):
    list_docs = []
    doc_main = Docstring(class_doc.__doc__)
    docs_pr = doc_main.parse("google")
    doc_md = {}
    doc_md["name"] = "mbbank." + class_doc.__qualname__
    for i in docs_pr:
        if i.kind is DocstringSectionKind.text:
            doc_md["doc"] = i.value
        elif i.kind is DocstringSectionKind.attributes:
            doc_md["attributes"] = [i.as_dict() for i in i.value]
        elif i.kind is DocstringSectionKind.parameters:
            doc_md["parameters"] = [i.as_dict() for i in i.value]
    list_docs.append(doc_md)
    for i in dir(class_doc):
        attb = getattr(class_doc, i)
        if i.startswith("_") or attb.__doc__ is None:
            continue
        elif not callable(attb):
            continue
        doc_main = Docstring(attb.__doc__)
        docs_pr = doc_main.parse("google")
        doc_md = {"name": attb.__name__}
        if asyncio.iscoroutinefunction(attb):
            doc_md["name"] = "async " + doc_md["name"]
        for i in docs_pr:
            if i.kind is DocstringSectionKind.text:
                doc_md["doc"] = i.value
            elif i.kind is DocstringSectionKind.attributes:
                doc_md["attributes"] = [i.as_dict() for i in i.value]
            elif i.kind is DocstringSectionKind.parameters:
                doc_md["parameters"] = [i.as_dict() for i in i.value]
            elif i.kind is DocstringSectionKind.returns:
                doc_md["returns"] = [i.as_dict() for i in i.value]
            elif i.kind is DocstringSectionKind.raises:
                doc_md["raises"] = [i.as_dict() for i in i.value]
        list_docs.append(doc_md)
    return list_docs


def from_list_to_md(doc_list):
    str_out = []

    def out(s=""):
        str_out.append(s)

    for n, it in enumerate(doc_list):
        pram = "" if "parameters" not in it else ", ".join([pr["name"] for pr in it["parameters"]])
        if n == 0:
            out(f"# {it['name']}({pram})")
        else:
            out(f"\n### {it['name']}({pram})")
        if "doc" in it:
            out(f":   {it['doc']}")
        if "attributes" in it:
            out("\n **Attributes**")
            for j in it["attributes"]:
                out()
                out(f"{j['name']} ({j['annotation']}): {j['description']}")
        if "parameters" in it:
            out("\n **Parameters**")
            for j in it["parameters"]:
                out()
                out(f"`{j['name']}` ({j['annotation']}): {j['description']}")
        if "returns" in it:
            out("\n **Returns**")
            for j in it["returns"]:
                out()
                out(f"    {j['name']} ({j['annotation']}): {j['description']}")
        if "raises" in it:
            out("\n **Raises**")
            for j in it["raises"]:
                out(f"\n    {j['annotation']}: {j['description']}")
        out()
    return "\n".join(str_out)


if "api_document" not in os.listdir("./docs"):
    os.mkdir("./docs/api_document")

with open("./docs/api_document/sync_api.md", "w") as f:
    data = from_list_to_md(parse_doc(MBBank))
    f.write(data)

with open("./docs/api_document/async_api.md", "w") as f:
    data = from_list_to_md(parse_doc(MBBankAsync))
    f.write(data)

with open("./docs/api_document/image_processing.md", "w") as f:
    data = from_list_to_md(parse_doc(CapchaProcessing))
    f.write(data)
    f.write("\n\n")
    data = from_list_to_md(parse_doc(CapchaOCR))
    f.write(data)
