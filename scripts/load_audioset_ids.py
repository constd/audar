import pathlib

import click
import pandas as pd

from audar import audioset


DATASPLITS_DIR = "datasplits"
SEGMENTS_FILES = {
    "balanced_train": "balanced_train_segments.csv",
    "eval": "eval_segments.csv",
    "unbalanced_train": "unbalanced_train_segments.csv"
}


def load_segments(segments_path):
    # kwargs = {
    #     "comment": "#",
    #     "header": None,
    #     "names": ["YTID", "start_seconds", "end_seconds", "positive_labels"]
    # }
    items = []
    with open(segments_path) as fh:
        reader = audioset.AudiosetAnnotationReaderV1(fh)
        for l in reader:
            items.append(l["YTID"])

    return items


@click.command()
@click.argument("dataset-dir")
@click.option("--audioset-path", default="audioset")
def load_audioset_ids(audioset_path, dataset_dir):
    """Loads all AudioSet segments files, and writes them
    as a single csv, with aggregated fields to load into
    a database later.
    """
    audioset_path = pathlib.Path(dataset_dir) / audioset_path
    click.echo(f"Loading audioset .csvs from {audioset_path}")

    datasplits_path = audioset_path / DATASPLITS_DIR

    unbalanced_train_segment_ids = load_segments(datasplits_path / SEGMENTS_FILES["unbalanced_train"])
    balanced_train_segment_ids = load_segments(datasplits_path / SEGMENTS_FILES["balanced_train"])
    eval_train_segment_ids = load_segments(datasplits_path / SEGMENTS_FILES["eval"])

    complete_segments_df = pd.concat([
        pd.DataFrame({"YTID": unbalanced_train_segment_ids, "partition": "unbalanced_train"}),
        pd.DataFrame({"YTID": balanced_train_segment_ids, "partition": "balanced_train"}),
        pd.DataFrame({"YTID": eval_train_segment_ids, "partition": "eval"}),
    ], ignore_index=True)

    out_file = "all_segments.csv"
    complete_segments_df.to_csv(out_file, compression="zip")

    click.secho(f"All Segments written to: {out_file}")


if __name__ == "__main__":
    load_audioset_ids()
