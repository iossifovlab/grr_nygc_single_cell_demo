#!/usr/bin/env python3
"""Delete labels from genomic resources.

    del_labels.py assay,technology ./single_nuclei_expression_and_atac_peaks

The first argument is a comma separated list of label names.  Those labels
are removed from the meta.labels of every genomic_resource.yaml found under
the given directories; the remaining labels, and the rest of the file, are
left byte for byte as they were.  A resource that does not carry one of the
labels is simply left alone.  When the last label of a resource is deleted
the now empty `labels:` key is dropped as well.
"""

import argparse
import sys

from resource_labels import (
    LabelEditError,
    find_resource_files,
    update_file,
)


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="Delete labels from genomic resources.",
        epilog="example: del_labels.py assay,technology "
               "./single_nuclei_expression_and_atac_peaks",
    )
    parser.add_argument(
        "keys", metavar="KEYS",
        help="comma separated names of the labels to delete, "
             "e.g. assay,technology")
    parser.add_argument(
        "paths", metavar="DIR", nargs="+",
        help="directories to search recursively for genomic_resource.yaml "
             "files (a genomic_resource.yaml file itself is also accepted)")
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="report what would change without writing anything")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="also report the resources that do not carry the labels")
    args = parser.parse_args(argv)

    keys = list(dict.fromkeys(
        key.strip() for key in args.keys.split(",") if key.strip()))
    if not keys:
        parser.error("no label names given")
    args.keys = keys
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
                resource_file, remove=args.keys, dry_run=args.dry_run)
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

    print(f"\n{updated} resource(s) {prefix}, {unchanged} did not carry "
          f"the labels, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
