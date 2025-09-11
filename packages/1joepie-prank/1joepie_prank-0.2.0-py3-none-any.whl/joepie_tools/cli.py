"""CLI for joepie_tools pranks."""
import argparse
import logging
from joepie_tools.hackerprank import (
    fake_hack_screen, fake_matrix, fake_terminal, fake_file_dump, fake_warning_popup
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("joepie_tools")

def positive_int(v):
    iv = int(v)
    if iv < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return iv

def positive_float(v):
    fv = float(v)
    if fv < 0.5:
        raise argparse.ArgumentTypeError("duration must be >= 0.5")
    return fv

def main(argv=None):
    parser = argparse.ArgumentParser(prog="joepie_tools", description="Joepie prank tools CLI")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("hack", help="Open fake hack windows")
    p1.add_argument("-n", "--num", type=positive_int, default=3)
    p1.add_argument("-d", "--duration", type=positive_float, default=8.0)

    p2 = sub.add_parser("matrix", help="Open matrix-style window")
    p2.add_argument("-d", "--duration", type=positive_float, default=12.0)

    p3 = sub.add_parser("term", help="Open fake typing terminal")
    p3.add_argument("-d", "--duration", type=positive_float, default=10.0)

    p4 = sub.add_parser("dump", help="Open fake file dump")
    p4.add_argument("-d", "--duration", type=positive_float, default=6.0)

    p5 = sub.add_parser("popup", help="Show a fake warning popup")
    p5.add_argument("-m", "--message", type=str, default="Warning: Unauthorized access")
    p5.add_argument("-d", "--duration", type=positive_float, default=4.0)

    args = parser.parse_args(argv)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.cmd == "hack":
        fake_hack_screen(num_windows=args.num, duration=args.duration)
    elif args.cmd == "matrix":
        fake_matrix(duration=args.duration)
    elif args.cmd == "term":
        fake_terminal(duration=args.duration)
    elif args.cmd == "dump":
        fake_file_dump(duration=args.duration)
    elif args.cmd == "popup":
        fake_warning_popup(message=args.message, duration=args.duration)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
