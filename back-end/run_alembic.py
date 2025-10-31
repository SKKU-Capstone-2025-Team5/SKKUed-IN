import sys
from alembic.config import Config, CommandLine

def run_alembic_command(args):
    alembic_cfg = Config("alembic.ini")
    CommandLine(alembic_cfg).main(argv=args)

if __name__ == '__main__':
    # The first argument is the script name itself, so we skip it.
    # The remaining arguments are passed to alembic.command.main
    run_alembic_command(sys.argv[1:])
