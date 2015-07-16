import argparse
import os

import polytaxis

def main():
    parser = argparse.ArgumentParser(
        description='Modifies polytaxis headers on files.',
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Files to modify.',
    )
    args = parser.parse_args()

    for filename in args.files:
        if os.path.isdir(filename):
            parser.error(
                'File [{}] must be a regular file, but it is a directory.'.format(
                    filename,
                )
            )

        tags = polytaxis.get_tags(filename)
        if not tags:
            print(
                'File [{}] has no polytaxis header; skipping.'.format(filename)
            )
            continue

        # TODO your code here
        print(tags)

        polytaxis.set_tags(filename, tags)

if __name__ == '__main__':
    main()
