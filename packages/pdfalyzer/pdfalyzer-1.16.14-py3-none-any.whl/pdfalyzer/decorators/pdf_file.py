from os import path
from pathlib import Path
from typing import List, Optional, Union


class PdfFile:
    """
    Wrapper for a PDF file path that provides useful methods and properties.
    """
    def __init__(self, file_path: Union[str, Path]) -> None:
        self.file_path: Path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        self.dirname = self.file_path.parent
        self.basename: str = path.basename(file_path)
        self.basename_without_ext: str = str(Path(self.basename).with_suffix(''))
        self.extname: str = self.file_path.suffix
        self.text_extraction_attempted: bool = False

    def extract_page_range(
            self,
            page_range: PageRange,
            destination_dir: Optional[Path] = None,
            extra_file_suffix: Optional[str] = None
        ) -> Path:
        """Extract a range of pages to a new PDF file (or 1 page if last_page_number not provided.)"""
        destination_dir = destination_dir or DEFAULT_PDF_ERRORS_DIR
        create_dir_if_it_does_not_exist(destination_dir)

        if extra_file_suffix is None:
            file_suffix = page_range.file_suffix()
        else:
            file_suffix = f"{page_range.file_suffix()}__{extra_file_suffix}"

        extracted_pages_pdf_basename = insert_suffix_before_extension(self.file_path, file_suffix).name
        extracted_pages_pdf_path = destination_dir.joinpath(extracted_pages_pdf_basename)
        stderr_console.print(f"Extracting {page_range.file_suffix()} from '{self.file_path}' to '{extracted_pages_pdf_path}'...")
        pdf_writer = PdfWriter()

        with open(self.file_path, 'rb') as source_pdf:
            pdf_writer.append(fileobj=source_pdf, pages=page_range.to_tuple())

        if SortableFile.confirm_file_overwrite(extracted_pages_pdf_path):
            with open(extracted_pages_pdf_path, 'wb') as extracted_pages_pdf:
                pdf_writer.write(extracted_pages_pdf)

        stderr_console.print(f"Wrote new PDF '{extracted_pages_pdf_path}'.")
        return extracted_pages_pdf_path
