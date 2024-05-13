# Music info

## Prepare

```bash
conda create --prefix ./.venv python=3.11.5 -y
conda activate ./.venv
pip install -r requirements.txt
```

## Usage


```python
python main.py -p <path_to_music_file> -g <default genre> -c <comment>
```

```python
usage: main.py [-h] -p PATH [-g DEFAULT_GENRE] [-c COMMENT]

Update MP3 tags (Release date, Genre, Comment)

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Directory path containing MP3 files
  -g DEFAULT_GENRE, --default_genre DEFAULT_GENRE
                        Default genre to apply to all MP3 files where we cannot find genre information
  -c COMMENT, --comment COMMENT
                        Comment to apply to all MP3 files
```