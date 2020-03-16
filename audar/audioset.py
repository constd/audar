import json
import sys, os
import pickle
from csv import reader, DictReader
from multiprocessing import pool
from tqdm import tqdm
from utils import download_file, download_ytaudio

AUDIOSET_ONTOLOGY_URL = "https://raw.githubusercontent.com/audioset/ontology/master/ontology.json"

class AudiosetAnnotationReaderV1(DictReader):
    def __init__(self, f, ontology=None, fieldnames=None, fieldtypes=None,
                 restkey=None, restval=None, dialect="excel", *args, **kwds):
        self.ontology = self.__load_ontology(ontology)
        self.annotation_stats = None
        self.annotation_creation_date = None
        if fieldtypes is None:
            fieldtypes = {'YTID': str, "end_seconds": float, "start_seconds": float}
        self.fieldtypes = fieldtypes
        super().__init__(f, fieldnames=fieldnames, restkey=restkey, restval=restval,
                         dialect=dialect, *args, **kwds)
        self.init_properties()

    @staticmethod
    def __load_ontology(ontology):
        if ontology is not None:
            return {x["id"]: x for x in ontology}
        return ontology

    def init_properties(self):
        row = next(self.reader)
        self.annotation_creation_date = [x.strip("#").rstrip().lstrip() for x in row]
        row = next(self.reader)
        self.annotation_stats = {x.split("=")[0].strip("#|\' \'|\n"): int(x.split("=")[1]) for x in row}
        row = next(self.reader)
        row = [x.strip("#|\' \'|\n") for x in row]
        self.fieldnames = row[:-1]
        if self.restkey is None:
            self.restkey = row[-1]
        self.line_num = self.reader.line_num

    def __next__(self):
        row = next(self.reader)
        self.line_num = self.reader.line_num

        while row == []:
            row = next(self.reader)
        if self.fieldtypes is None:
            d = dict(zip(self.fieldnames, row))
        else:
            # converts fields to a specific datatype (e.g. strings to floats)
            d = {f: self.fieldtypes[f](r) for f, r in zip(self.fieldnames, row)}

        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            classes = [x.strip("\' \'|\"") for x in row[lf:]]
            if self.ontology is not None:
                classes = {x: self.ontology[x] for x in set(classes)}
            d[self.restkey] = classes
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


def retrieve_ontology():
    if not os.path.exists(AUDIOSET_ONTOLOGY_URL.split("/")[-1]):
        download_file(AUDIOSET_ONTOLOGY_URL)
    with open(AUDIOSET_ONTOLOGY_URL.split("/")[-1], "r") as f:
        ontology = json.load(f)
    return ontology


def download_audioset_segment(segment_url, output_dir):
    ontology = retrieve_ontology()
    download_file(segment_url)
    with open(segment_url.split("/")[-1], "r") as f:
        asannreader = AudiosetAnnotationReaderV1(f, ontology=ontology)
        ytid_num = asannreader.annotation_stats["num_ytids"]
        for row in tqdm(asannreader, total=ytid_num):
            download_ytaudio(row["YTID"], start_seconds=row["start_seconds"], end_seconds=row["end_seconds"], output_dir=output_dir)


def download_audioset(dir_prefix="data"):
    segments = {
        "eval" : {
            "url": "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/eval_segments.csv"},
        "balanced_train" : {
            "url": "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv"},
        "unbalanced_train" : {
            "url": "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv"}
    }

    for k, v in segments.items():
        download_audioset_segment(v["url"], f"{dir_prefix}/{k}")
