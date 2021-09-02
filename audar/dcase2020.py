from .utils import download_file


def task1a(output_dir="./"):
    task1a_doc = ["https://zenodo.org/record/3670167/files/TAU-urban-acoustic-scenes-2020-mobile-development.doc.zip"]
    task1a_meta = ["https://zenodo.org/record/3670167/files/TAU-urban-acoustic-scenes-2020-mobile-development.meta.zip"]
    task1a_data = [f"https://zenodo.org/record/3670167/files/TAU-urban-acoustic-scenes-2020-mobile-development.audio.{x}.zip"
              for x in range(1, 22)]
    task1a = task1a_doc + task1a_meta + task1a_data
    for url in task1a:
        download_file(url, output_dir=output_dir)


def task1b(output_dir="./"):
    task1b_doc = ["https://zenodo.org/record/3670185/files/TAU-urban-acoustic-scenes-2020-3class-development.doc.zip"]
    task1b_meta = ["https://zenodo.org/record/3670185/files/TAU-urban-acoustic-scenes-2020-3class-development.meta.zip"]
    task1b_data = [f"https://zenodo.org/record/3670185/files/TAU-urban-acoustic-scenes-2020-3class-development.audio.{x}.zip"
              for x in range(1, 22)]
    task1b = task1b_doc + task1b_meta + task1b_data
    for url in task1b:
        download_file(url, output_dir=output_dir)


def task5(output_dir="./"):
    task5_data = ["https://zenodo.org/record/3693077/files/audio.tar.gz"]
    task5_taxonomy = ["https://zenodo.org/record/3693077/files/dcase-ust-taxonomy.yaml"]
    task5_annotations = ["https://zenodo.org/record/3693077/files/annotations.csv"]
    task5_readme = ["https://zenodo.org/record/3693077/files/README.md"]
    task5 = task5_data + task5_taxonomy + task5_annotations + task5_readme
    for url in task5:
        download_file(url, output_dir=output_dir)
