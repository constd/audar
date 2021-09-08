# Dataset Download Manager

This flask app runs a interface to a simple application,
which:

* allows workers to request a next download ID.
* tracks the current state of items by download ID.
* Allows batch updating.

# How to Run The API

From `downloadmgr` dir...

## In Development
```
export FLASK_ENV=development; FLASK_APP=apiapp flask run
```

## Live
```
export FLASK_ENV=production; FLASK_APP=apiapp flask run
```

You may want to include `--ip 0.0.0.0` to make the flask app available outside `localhost`.


# How to initialize the database

* Step 1: From the root of this repo, generate a `all_segments.csv` containing the list of all segments in your dataset, using the script `scripts/load_audioset_ids.py`. Call it like this:

    ```
    python scripts/load_audioset_ids.py <path-to-your-dataset-root>
    ```

    If audioset lives in a directory not called `auidoset`, then you'll need to specify the name of the audioset directory using `--audioset-path`.

* Step 2: Initialize the database.

    ```
    # from the `downloadmgr` directory...
    flask init-db
    ```

* Step 3: Ingest the segments from step 1:

```
    # from `downloadmgr` dir
    flask ingest-raw ../all_segments.csv
```

* Step 4 (optional): Batch update the state of already-downloaded files.

    Generate a text file, where each line has a file ID. Then:

    ```
    flask bulk-update-state <path-to-id-file.txt> <state>
    ```

    eg:
    ```
    flask bulk-update-state <path-to-id-file.txt> completed
    ```

# Pages Overview

```
/   # index: shows some available items from the db to prove it's working.

/id/<ytid>  # display the record for a single item.
```


# API Overview

```
/api

    /segments
        /<id>  GET   # get info for a single segment
        /count GET   # get counts for a subset of segments.
                     #   you can use query parameters to filter.
    /download
        /next  GET   # Get a next randomly available id to download.
        /<id>  PUT   # update the state for a single ID.
        /batch POST  # update the state for a batch of IDs.
```
