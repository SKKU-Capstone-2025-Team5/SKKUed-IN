import sys
from alembic.config import Config
from alembic import command

def run_alembic_command(args):
    alembic_cfg = Config("alembic.ini")
    command.main(alembic_cfg, args)

if __name__ == '__main__':
    # The first argument is the script name itself, so we skip it.
    # The remaining arguments are passed to alembic.command.main
    run_alembic_command(sys.argv[1:])
