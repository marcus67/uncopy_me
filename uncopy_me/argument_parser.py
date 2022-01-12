import argparse

from uncopy_me import logging_tools

DEFAULT_COMMIT_BLOCK_SIZE = 1000

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index-directories', nargs='*', dest='index_directories', default=[],
                        help='directories to be indexed')
    parser.add_argument('--check-directories', nargs='*', dest='check_directories', default=[],
                        help='directories to be compared against the cache')
    parser.add_argument('--cache-directory', dest='cache_directory', default="~/.cache/uncopy_me",
                        help='directory to be used for cache files')
    parser.add_argument('--config-file', dest='config_file',
                        help='configuration file')
    parser.add_argument('--commit-block-size', dest='commit_block_size', default=DEFAULT_COMMIT_BLOCK_SIZE,
                        help='number of cache operations between commits')
    parser.add_argument('--index-recursively', dest='index_recursively', default=True,
                        help='index directories recursively')
    parser.add_argument('--find-duplicates', dest='find_duplicates', action="store_true",
                        help='find duplicates in cache')
    parser.add_argument('--exclude-patterns', nargs='*', dest='exclude_patterns', default = [],
                        help='set exclude pattern for scanned picture names')
    parser.add_argument('--loglevel', dest='log_level', default=logging_tools.DEFAULT_LOG_LEVEL,
                        help='logging level', choices=['WARN', 'INFO', 'DEBUG'])
    parser.add_argument('--delete', dest='delete', action="store_true",
                        help='actually delete pictures regarded as duplicates (otherwise duplicates are only listed)')
    parser.add_argument('--check-cache', dest='check_cache', action="store_true",
                        help='removes cache entries referring to non-existing pictures')
    parser.add_argument('--similar', dest='similar', action="store_true",
                        help='use similarity hash for find duplicates '
                             '(otherwise only identical pictures are regarded as duplicates)')
    parser.add_argument('--use-priorities', dest='use_priorities', action="store_true",
                        help='use priority declarations to determine which duplicates are deleted')
    return parser

