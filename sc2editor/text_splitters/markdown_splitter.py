"""
Module for textsplitting Markdown documents.

This module splits a Markdown document into text and creates a LangChain Document.
"""

# Python Standard Library imports
from pathlib import Path

# Third-party Library imports
from langchain_core.documents import Document
from langchain_text_splitters import ExperimentalMarkdownSyntaxTextSplitter


def markdown_load_split() -> list[Document]:
    """
    Function that loads markdown files, splits text based on markdown grammar, and returns a list of Langchain Documents.

    Returns:
        Returns a list of LangChain Documents split by Markdown syntax.
    """
    datas_dir = Path(__file__).parents[1] / "datas"
    tutorial_datas_dir = datas_dir / "new_tutorials"
    not_allow_dirs = set(("Data_Primer",))

    documents = []

    # Get list of folders in 'new_tutorials directory'
    for tutorial_dir in Path(tutorial_datas_dir).iterdir():
        dir_name = tutorial_dir.name
        # Check if Folder is Allowed
        if dir_name not in not_allow_dirs:
            # Import markdown files in that folder
            for markdown_file in Path(tutorial_dir).iterdir():
                if markdown_file.is_file() and markdown_file.suffix == ".md":
                    markdown_file_name = markdown_file.name
                    with open(markdown_file, "r", encoding="utf-8") as f:
                        markdown_text = f.read()

                    # Split text based on markdown syntax
                    markdown_split_result = (
                        ExperimentalMarkdownSyntaxTextSplitter().split_text(
                            markdown_text
                        )
                    )
                    # Add metadata to each result
                    for order, markdown_res in enumerate(markdown_split_result):
                        markdown_res.metadata["page_content_order"] = order
                        markdown_res.metadata["source"] = (
                            f"https://s2editor-guides.readthedocs.io/New_Tutorials/{dir_name}/{markdown_file_name[:-3]}/"
                        )
                        markdown_res.metadata["languages"] = ["eng"]
                        markdown_res.metadata["file_directory"] = str(dir_name)
                        markdown_res.metadata["filename"] = str(markdown_file_name)
                        markdown_res.metadata["filetype"] = "text/markdown"

                    # Add the result to documents
                    documents.extend(markdown_split_result)
                    print(
                        f"Loaded {len(markdown_split_result)} documents from {markdown_file_name} in {dir_name}"
                    )

    print(f"Total documents loaded: {len(documents)}")
    return documents
