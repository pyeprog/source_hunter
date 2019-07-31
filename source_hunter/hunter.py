import argparse

from source_hunter.models.deps_tree import DepsTree
from source_hunter.query import Query
from source_hunter.utils.log_utils import logger
from source_hunter.utils.path_utils import PathUtils


def init_arg_parser():
    parse = argparse.ArgumentParser(description="print the relationship of your source code")
    parse.add_argument('root', type=str, help='the root path of your project')
    parse.add_argument('module', type=str, help='the path of your starting module')
    parse.add_argument('target', type=str, help='the searching function name or class name')
    parse.add_argument('--stdout', action='store_true', help='whether only output to stdout')
    parse.add_argument('--path', type=str, help='the saving path for your result.pdf', default='./')
    parse.add_argument('--name', type=str, help='the pdf file name of your result', default='result')
    parse.add_argument('--ignore', type=str, action='append',
                       help="files containing these keywords should be abandoned", default=[])
    parse.add_argument('--fullname', action='store_true', help='if use full name as node label')
    parse.add_argument('--suffix', action='store_true', help='if add suffix to node label')
    parse.add_argument('--engine', type=str,
                       help='available engine: dot[default], neato, sfdp, fdp, twopi, circo, dotty, lefty',
                       default='dot')
    parse.add_argument('--not_use_gitignore', action='store_false', help='include those files specified by .gitignore')
    parse.add_argument('--lang', type=str, help='support lang: python[defalt]', default='python')
    parse.add_argument('--format', type=str, help='pdf[default], png', default='pdf')
    parse.add_argument('--debug', type=int, help='debug level: 0=None, 1=light, 2=heavy', default=0)
    return parse


def hunt():
    parse = init_arg_parser()
    args = parse.parse_args()

    ignore = []
    for ignore_str in args.ignore:
        ignore.extend(ignore_str.split(','))

    logger.set_debug(args.debug)

    tree = DepsTree(PathUtils.normalize_to_abs(args.root), lang=args.lang, ignore_keywords=ignore)
    query = Query(tree)
    calling_tree = query.find_caller(PathUtils.normalize_to_abs(args.module), args.target)

    if args.stdout:
        print(calling_tree)
    else:
        calling_tree.render(name=args.name,
                            dir_path=PathUtils.normalize_to_abs(args.path),
                            ues_fullname=args.fullname,
                            keep_suffix=args.suffix,
                            engine=args.engine,
                            output_format=args.format)


if __name__ == '__main__':
    hunt()
