import json
import sys, os
import pickle
from csv import reader, DictReader
from multiprocessing import pool
from tqdm import tqdm
from utils import download_file, download_ytaudio
from typing import List, Optional
from glob import glob
from os.path import splitext


AUDIOSET_ONTOLOGY_URL = "https://raw.githubusercontent.com/audioset/ontology/master/ontology.json"


class AudiosetAnnotationReaderV1(DictReader):
    def __init__(self, f, fieldnames=None, fieldtypes=None,
                 restkey=None, restval=None, dialect="excel", *args, **kwds):
        self.annotation_stats = None
        self.annotation_creation_date = None
        if fieldtypes is None:
            fieldtypes = {'YTID': str, "end_seconds": float, "start_seconds": float}
        self.fieldtypes = fieldtypes
        super().__init__(f, fieldnames=fieldnames, restkey=restkey, restval=restval,
                         dialect=dialect, *args, **kwds)
        self.init_properties()

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
            d[self.restkey] = classes
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


class AudiosetSegment:
    def __init__(self, segment_path: str, class_filters: List[Optional[str]]=[], ontology: dict=None):
        self.class_filters = class_filters
        self.ontology = self.__load_ontology(ontology)
        with open(segment_path, 'r') as f:
            annotation_reader = AudiosetAnnotationReaderV1(f)
            self.annotations = [x for x in annotation_reader]
        if self.class_filters:
            self.annotations = self.filter_annotations(self.annotations)

    @staticmethod
    def __load_ontology(ontology):
        if ontology is not None:
            return {x['name'].lower(): x['id'] for x in ontology}
        return ontology

    def filter_annotations(self, annotations):
        annotations_filtered = []
        class_ids = [v for k, v  in self.ontology.items() if k in self.class_filters]
        for annotation in annotations:
            if set(class_ids) & set(annotation.get('positive_labels', [])):
                annotations_filtered.append(annotation)
        return annotations_filtered


def retrieve_ontology():
    if not os.path.exists(AUDIOSET_ONTOLOGY_URL.split("/")[-1]):
        download_file(AUDIOSET_ONTOLOGY_URL)        
    with open(AUDIOSET_ONTOLOGY_URL.split("/")[-1], "r") as f:
        ontology = json.load(f)
    return ontology


# def download_audioset_segment(segment_url, output_dir):
#     ontology = retrieve_ontology()
#     download_file(segment_url)
#     with open(segment_url.split("/")[-1], "r") as f:
#         asannreader = AudiosetAnnotationReaderV1(f, ontology=ontology)
#         ytid_num = asannreader.annotation_stats["num_ytids"]
#         for row in tqdm(asannreader, total=ytid_num):
#             download_ytaudio(row["YTID"], start_seconds=row["start_seconds"], end_seconds=row["end_seconds"], output_dir=output_dir)


def download_audioset_segment(segment_url, output_dir, class_filters):
    ontology = retrieve_ontology()
    download_file(segment_url)
    as_seg = AudiosetSegment(segment_url.split("/")[-1], class_filters=class_filters, ontology=ontology)
    existing_files = [splitext(x.split('/')[-1])[0].replace('.info', '') for x in glob(f"{output_dir}/*.json")]
    for annotation in tqdm(as_seg.annotations):
        if annotation['YTID'] in existing_files:
            continue
        download_ytaudio(annotation["YTID"], start_seconds=annotation["start_seconds"], end_seconds=annotation["end_seconds"], output_dir=output_dir)
        # print(f'downloading {annotation["YTID"]}')


def download_audioset(dir_prefix="/home/const/data/audioset"):
    segments = {
        # "eval" : {
        #     "url": "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/eval_segments.csv"
        # },
        # "balanced_train" : {
        #     "url": "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv"
        # },
        "unbalanced_train" : {
            "url": "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv"
        }
    }

    for k, v in segments.items():
        # class_filters = ['speech', 'screaming', 'whispering', 'dog', 'cat', 'laughter', 'sigh', 'cough', 'sneeze']
        class_filters = ['speech', 'cough', 'sneeze']
        download_audioset_segment(v["url"], f"{dir_prefix}/{k}", class_filters)


if __name__ == "__main__":
    download_audioset()
