"""A utility to display and modify polytaxis metadata."""
import argparse
import polytaxis

def main():
    """List and modify tags."""
    parser = argparse.ArgumentParser(
        description='Modify polytaxis metadata on a file.',
    )
    parser.add_argument(
        'file', 
        help='Files to modify',
        nargs='*', 
    )
    parser.add_argument(
        '-c', 
        '--clear', 
        help='Clear tags. Applied first.',
        nargs='*', 
    )
    parser.add_argument(
        '-a', 
        '--add', 
        help='Add tag.',
        nargs=2, 
        action='append',
    )
    parser.add_argument(
        '-r', 
        '--remove', 
        help='Remove tag.',
        nargs=2, 
        action='append',
        default=[],
    )
    parser.add_argument(
        '-s',
        '--strip',
        help='Remove polytaxis header.',
        action='store_true',
    )
    parser.add_argument(
        '-l', 
        '--list', 
        help='List tags after operations.', 
        dest='list', 
        action='store_true',
    )
    parser.set_defaults(list=False, strip=False, add=[], remove=[])
    args = parser.parse_args()

    if args.strip and (args.add or args.remove or args.clear or args.list):
        parser.error(
            'You cannot use any other options with -s/--strip.'
        )

    for filename in args.file:
        if args.strip:
            polytaxis.strip_tags(filename)
            continue

        tags = polytaxis.get_tags(filename) or {}
        modify = False
        if args.clear:
            tags = {}
            modify = True
        for key, val in args.add:
            if not key in tags:
                tags[key] = set()
            tags[key].add(val)
            modify = True
        for key, val in args.remove:
            if not key in tags:
                continue
            try:
                tags[key].remove(val)
            except KeyError:
                pass
            modify = True
        if modify:
            polytaxis.set_tags(filename, tags)
        if args.list:
            print('Final tags for {}:\n{}\n'.format(
                filename,
                tags,
            ))

if __name__ == '__main__':
    main()
