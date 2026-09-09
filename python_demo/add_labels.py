#!/usr/bin/env python3
"""Add or update labels on genomic resources.

    add_labels.py "{assay: 10x_multeomix}" ./single_nuclei_expression_and_atac_peaks

The first argument is a YAML mapping of the labels to set.  Every
genomic_resource.yaml found under the given directories gets those labels
added to its meta.labels; a label that is already there keeps its place in
the file and only its value is rewritten.  Nothing else in the file is
touched.
"""

import argparse
import sys

import yaml

from resource_labels import (
    LabelEditError,
    find_resource_files,
    update_file,
)


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="Add or update labels on genomic resources.",
        epilog='example: add_labels.py "{assay: 10x_multeomix, replicate: 2}" '
               './single_nuclei_expression_and_atac_peaks',
    )
    parser.add_argument(
        "labels", metavar="LABELS",
        help="the labels to set, as a YAML mapping, "
             'e.g. "{assay: 10x_multeomix}"')
    parser.add_argument(
        "paths", metavar="DIR", nargs="+",
        help="directories to search recursively for genomic_resource.yaml "
             "files (a genomic_resource.yaml file itself is also accepted)")
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="report what would change without writing anything")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="also report the resources that already have the labels")
    args = parser.parse_args(argv)

    try:
        labels = yaml.safe_load(args.labels)
    except yaml.YAMLError as error:
        parser.error(f"could not parse LABELS as YAML: {error}")
    if labels is None:
        parser.error("no labels given")
    if not isinstance(labels, dict):
        parser.error(
            "LABELS must be a YAML mapping of label names to values, "
            'e.g. "{assay: 10x_multeomix}"')
    for key in labels:
        if not isinstance(key, str):
            parser.error(f"label names must be strings, {key!r} is not")
    args.labels = labels
    return args


def main(argv=None):
    args = parse_arguments(argv)

    try:
        resource_files = find_resource_files(args.paths)
    except LabelEditError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if not resource_files:
        print("no genomic_resource.yaml files found under "
              f"{', '.join(args.paths)}", file=sys.stderr)
        return 1

    prefix = "would update" if args.dry_run else "updated"
    updated = unchanged = failed = 0
    for resource_file in resource_files:
        try:
            changes, changed = update_file(
                resource_file, add=args.labels, dry_run=args.dry_run)
        except (LabelEditError, OSError) as error:
            print(f"error: {error}", file=sys.stderr)
            failed += 1
            continue

        if changed:
            updated += 1
        else:
            unchanged += 1
        if changed or args.verbose:
            print(f"{prefix if changed else 'unchanged'} {resource_file}")
            for change in changes:
                if change.modifies or args.verbose:
                    print(f"  {change.format()}")

    print(f"\n{updated} resource(s) {prefix}, {unchanged} already had "
          f"the labels, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
