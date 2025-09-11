#!/usr/local/bin/python

from os.path import splitext, join
import typer
from typing_extensions import Annotated
from cbz.constants import AgeRating, Format, Manga, PageType, YesNo
from cbz.page import PageInfo
from argparse import ArgumentParser
from typing import Optional
from pathlib import Path
from cbz.comic import ComicInfo
from PIL import Image
from tqdm import tqdm
import rarfile
import zipfile


# Functions


def parse_args():
    """Parse command line arguments."""

    parser = ArgumentParser(
            prog='🪡 Manga-Stitcher',
            description="Manga Stitcher is a straightforward tool designed to automatically combine manga pages vertically, creating a seamless reading experience. Many manga releases include extra \"tail\" images—often containing the scanlator's logo or credits—in separate files. This script detects and merges these pages, saving you time and ensuring your manga is presented as intended.",
        )

    parser.add_argument(
        'directory',
        help='The path to the directory full of CBZ/CBR/RAR/ZIP chapters',
    )

    parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        default=False,
        dest='recursive',
        help='Recursively search the directory for CBR/CBZ/RAR/ZIP files',
    )

    parser.add_argument(
        '--title',
        '-t',
        type=str,
        default=None,
        help='The title to use for the stitched manga (overrides default)',
        required=False,
    )

    parser.add_argument(
        '--series',
        '-s',
        type=str,
        default=None,
        help='The series to use for the stitched manga (overrides default)',
        required=False,
    )

    return parser.parse_args()


def extract_cbr(cbr_path):
    """Extract CBR/RAR file contents."""

    with rarfile.RarFile(cbr_path) as rar_ref:
        extraction_dir = Path(cbr_path).with_suffix('')
        rar_ref.extractall(extraction_dir)

        return extraction_dir


def extract_cbz(cbz_path):
    """Extract CBZ/ZIP file contents."""

    with zipfile.ZipFile(cbz_path) as zip_ref:
        extraction_dir = Path(cbz_path).with_suffix('')
        zip_ref.extractall(extraction_dir)

        return extraction_dir


def extract_comic(comic_path):
    """Extract both CBZ/ZIP and CBR/RAR files."""

    # Load the comic file
    if str(comic_path).endswith('.cbz') or str(comic_path).endswith('.zip'):
        comic = extract_cbz(comic_path)
    elif str(comic_path).endswith('.cbr') or str(comic_path).endswith('.rar'):
        comic = extract_cbr(comic_path)
    else:
        raise ValueError("Unsupported format. Must be .cbz or .cbr")

    return comic


def get_stitched_pages(extraction_dir: Path, chapter: int):
    """Stitch pages together and return a list of PageInfo objects."""

    stitched_pages = []

    pages = sorted(list(extraction_dir.iterdir()))

    for page in tqdm(range(0, len(pages) - 1), desc='Stitching pages', unit='page pair', position=1):
        if page % 2 != 0:
            continue

        img_path = pages[page]
        tail_path = pages[page + 1]

        img = Image.open(img_path)
        tail = Image.open(tail_path)

        # Check if img aspect ratio is portrait compared to tail aspect ratio

        if img.width != tail.width or img.height <= tail.height:
            continue

        # Stitch img and tail

        new_img = Image.new(img.mode, (max(img.width, tail.width), img.height + tail.height))
        new_img.paste(img, (0, 0))
        new_img.paste(tail, (0, img.height))

        extension = splitext(img_path.name)[1]
        stitched_file = join(extraction_dir, f'stitched_{chapter}_{page+1}.{extension}')

        new_img.save(stitched_file)

        stitched_pages.append(PageInfo.load(path=stitched_file, type=PageType.STORY))

    return stitched_pages


def create_stitched_comic(files: list[Path], chapter: int, title: Optional[str] = None, series: Optional[str] = None):
    """Create a stitched comic from the given chapter CBR/CBZ/RAR/ZIP file list and index."""

    filename = files[chapter]

    # print(f'Processing file: {filename}')

    extraction_dir = extract_comic(filename)

    # print(f'Extracted to: {extraction_dir}')

    stitched_pages = get_stitched_pages(extraction_dir, chapter)

    comic = ComicInfo.from_pages(
        pages=stitched_pages,
        title=title if title else f'Stitched Manga Chapter {chapter + 1}',
        series=series if series else '',
        number=1,
        language_iso='en',
        format=Format.WEB_COMIC,
        black_white=YesNo.YES,
        manga=Manga.YES,
        age_rating=AgeRating.ADULTS18
    )

    # Pack the comic book content into a CBZ file format
    cbz_content = comic.pack()

    # Define the path where the CBZ file will be saved
    cbz_path = filename.with_suffix('.stitched.cbz')

    # Write the CBZ content to the specified path
    cbz_path.write_bytes(cbz_content)

    # print(f'Stitched comic saved to: {cbz_path}')

    # Clean up extracted files
    for page in extraction_dir.iterdir():
        page.unlink()

    extraction_dir.rmdir()


def main(
    directory: Annotated[str, typer.Argument(help="The path to the directory full of CBZ/CBR/RAR/ZIP chapters")] = "",
    recusrive: Annotated[bool, typer.Option(help="Recursively search the directory for CBR/CBZ/RAR/ZIP files")] = False,
    title: Annotated[str, typer.Option(help="The title to use for the stitched manga (overrides default)")] = "",
    series: Annotated[str, typer.Option(help="The series to use for the stitched manga (overrides default)")] = ""
):
    """Main function to process the directory of CBR/CBZ/RAR/ZIP files."""

    print('\n>>> 🪡 Manga-Stitcher <<<\n\n')

    print(f'Processing directory: {directory}')

    # Find all CBR/CBZ files in directory

    glob_term = '**/*' if recusrive else '*'

    files = (p.resolve() for p in Path(directory).glob(glob_term) if p.suffix in {".cbz", ".cbr", ".rar", ".zip"})

    # Sort files by name

    files = sorted(files)

    for chapter in tqdm(range(0, len(files)), desc='Chapters', unit='chapter', position=2):
        # Skip already stitched files

        if str(files[chapter]).endswith('.stitched.cbz') or str(files[chapter]).endswith('.stitched.cbr'):
            continue

        create_stitched_comic(files, chapter, title, series)

    print('\nAll files processed!')
    print('\n>>> Done! <<<\n')


if __name__ == "__main__":
    args = parse_args()

    main(args.directory, args.recursive, args.title, args.series)
