import sys
from alembic.config import Config, CommandLine
from alembic import command

def run_alembic_command(args):
    alembic_cfg = Config("alembic.ini")
    if args and args[0] == "upgrade":
        command.upgrade(alembic_cfg, args[1] if len(args) > 1 else "head")
    elif args and args[0] == "revision":
        command.revision(alembic_cfg, message=args[1] if len(args) > 1 else None, autogenerate=True)
    else:
        print("Usage: python run_alembic.py [upgrade <revision>] | [revision <message>]")

if __name__ == '__main__':
    # The first argument is the script name itself, so we skip it.
    # The remaining arguments are passed to run_alembic_command
    run_alembic_command(sys.argv[1:])
