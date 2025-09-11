from utils import fatal
import commands as cmd


def main():
    args = cmd.main_parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
