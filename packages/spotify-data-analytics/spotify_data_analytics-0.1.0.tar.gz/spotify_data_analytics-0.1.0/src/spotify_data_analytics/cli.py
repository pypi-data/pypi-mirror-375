# src/spotify_data_analytics/cli.py
import argparse
from . import extract_main, transform_main, load_main

def main(argv=None):
    parser = argparse.ArgumentParser(prog="spotify-pipeline")
    parser.add_argument("--step", choices=["extract","transform","load","all"], default="all")
    parser.add_argument("--help-brief", action="store_true", help="short help")

    args = parser.parse_args(argv)

    if args.step in ("extract", "all"):
        extract_main()
    if args.step in ("transform", "all"):
        transform_main()
    if args.step in ("load", "all"):
        load_main()

if __name__ == "__main__":
    main()
