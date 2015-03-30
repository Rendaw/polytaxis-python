"""A utility to display and modify polytaxis metadata."""
import argparse
import polytaxis

def minmax_append_action(nmin, nmax):
    class Inner(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                raise argparse.ArgumentTypeError(
                    'argument "{argname}" requires between {nmin} and {nmax} arguments'.format(
                        argname=self.dest,
                        nmin=nmin,
                        nmax=nmax,
                    )
                )
            getattr(args, self.dest).append(values)
    return Inner

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
        '-e', 
        '--empty', 
        help='Create an empty header. Applied first.',
        action='store_true',
    )
    parser.add_argument(
        '-a', 
        '--add', 
        help='Add tag.',
        nargs='+',
        action=minmax_append_action(1, 2),
    )
    parser.add_argument(
        '-r', 
        '--remove', 
        help='Remove tag.',
        nargs='+',
        action=minmax_append_action(1, 2),
        default=[],
    )
    parser.add_argument(
        '-s',
        '--strip',
        help='Strip polytaxis header.',
        action='store_true',
    )
    parser.add_argument(
        '-u',
        '--unsized',
        help='Add or convert to unsized header.',
        action='store_true',
    )
    parser.add_argument(
        '-z',
        '--sized',
        help='Convert to sized header.',
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
    if not args.add and not args.remove and not args.empty and not args.strip:
        args.list = True

    if args.sized and args.unsized:
        parser.error(
            'You cannot specify both -z/--sized and -u/--unsized simultaneously.'
        )

    unsized = None
    if args.unsized:
        unsized = True
    if args.sized:
        unsized = False

    if args.strip and (args.add or args.remove or args.empty or args.list):
        parser.error(
            'You cannot use any other options with -s/--strip.'
        )

    for filename in args.file:
        if args.strip:
            polytaxis.strip_tags(filename)
            continue

        tags = polytaxis.get_tags(filename) or {}
        modify = False
        if args.empty:
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
            polytaxis.set_tags(filename, tags, unsized=unsized)
        if args.list:
            print('Tags in {}:\n{}'.format(
                filename,
                polytaxis.encode_tags(tags).decode('utf-8'),
            ))

if __name__ == '__main__':
    main()
