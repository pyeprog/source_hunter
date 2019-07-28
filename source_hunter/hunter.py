import argparse

from source_hunter.models.deps_tree import DepsTree
from source_hunter.query import Query


def init_arg_parser():
    parse = argparse.ArgumentParser(description="print the relationship of your source code")
    parse.add_argument('root', type=str, help='the root path of your project')
    parse.add_argument('module', type=str, help='the path of your starting module')
    parse.add_argument('target', type=str, help='the searching function name or class name')
    parse.add_argument('--view', type=int, help='whether output a pdf file', default=1)
    parse.add_argument('--path', type=str, help='the saving path for your result.pdf', default='./')
    parse.add_argument('--name', type=str, help='the pdf file name of your result', default='result')
    parse.add_argument('--ignore', type=str, action='append',
                       help="files containing these keywords should be abandoned", default=[])
    parse.add_argument('--fullname', action='store_true')
    parse.add_argument('--suffix', action='store_true')
    parse.add_argument('--engine', type=str,
                       help='available engine: dot[default], neato, sfdp, fdp, twopi, circo, dotty, lefty',
                       default='dot')
    return parse


def hunt():
    parse = init_arg_parser()
    args = parse.parse_args()

    ignore = []
    for ignore_str in args.ignore:
        ignore.extend(ignore_str.split(','))

    tree = DepsTree(args.root, ignore_keywords=ignore)
    query = Query(tree)
    calling_tree = query.find_caller(args.module, args.target)

    if args.view:
        calling_tree.render(name=args.name, dir_path=args.path, ues_fullname=args.fullname, keep_suffix=args.suffix,
                            engine=args.engine)
    else:
        print(calling_tree)


if __name__ == '__main__':
    hunt()
