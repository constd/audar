from .utils import download_file


def download(output_dir="./"):
    fsd50k_doc = ["https://zenodo.org/record/4060432/files/FSD50K.doc.zip"]
    fsd50k_meta = ["https://zenodo.org/record/4060432/files/FSD50K.metadata.zip"]
    fsd50k_ground_truth = ["https://zenodo.org/record/4060432/files/FSD50K.ground_truth.zip"]
    for url in fsd50k_doc + fsd50k_meta + fsd50k_ground_truth:
        download_file(url, output_dir=output_dir)

    dev_data = ["https://zenodo.org/record/4060432/files/FSD50K.dev_audio.zip"]
    dev_data += [f"https://zenodo.org/record/4060432/files/FSD50K.dev_audio.z{x:02d}"
              for x in range(1, 6)]
    for url in dev_data:
        download_file(url, output_dir=output_dir)

    eval_data = [
        "https://zenodo.org/record/4060432/files/FSD50K.eval_audio.zip",
        "https://zenodo.org/record/4060432/files/FSD50K.eval_audio.z01"
    ]
    for url in eval_data:
        download_file(url, output_dir=output_dir)
