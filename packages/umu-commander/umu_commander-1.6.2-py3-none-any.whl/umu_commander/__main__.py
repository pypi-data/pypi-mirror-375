import os
import sys
from collections.abc import Callable
from json import JSONDecodeError

from umu_commander import configuration as config
from umu_commander import database as db
from umu_commander import tracking, umu_config
from umu_commander.classes import ExitCode
from umu_commander.configuration import CONFIG_DIR, CONFIG_NAME
from umu_commander.util import print_help

# TODO: Add related projects shoutout
# https://github.com/Faugus/faugus-launcher
# https://github.com/SeongGino/Nero-umu
# https://github.com/korewaChino/umu-wrapper

# TODO: https://inquirerpy.readthedocs.io/en/latest/


def main() -> ExitCode:
    try:
        config.load()

    except (JSONDecodeError, KeyError):
        config_path: str = os.path.join(CONFIG_DIR, CONFIG_NAME)
        config_path_old: str = os.path.join(CONFIG_DIR, CONFIG_NAME + ".old")

        print(f"Config file at {config_path} could not be read.")

        if not os.path.exists(config_path_old):
            print(f"Config file renamed to {config_path_old}.")
            os.rename(config_path, config_path_old)

    except FileNotFoundError:
        config.dump()

    try:
        db.load()

    except JSONDecodeError:
        db_path: str = os.path.join(config.DB_DIR, config.DB_NAME)
        db_path_old: str = os.path.join(config.DB_DIR, config.DB_NAME + ".old")

        print(f"Tracking file at {db_path} could not be read.")

        if not os.path.exists(db_path_old):
            print(f"DB file renamed to {db_path_old}.")
            os.rename(db_path, db_path_old)

    except FileNotFoundError:
        pass

    dispatch: dict[str, Callable] = {
        "track": tracking.track,
        "untrack": tracking.untrack,
        "users": tracking.users,
        "delete": tracking.delete,
        "create": umu_config.create,
        "run": umu_config.run,
    }

    try:
        dispatch[sys.argv[1]]()

    except IndexError:
        print_help()
        return_val = ExitCode.SUCCESS

    except KeyError:
        print("Unrecognised verb.")
        print_help()
        return_val = ExitCode.INVALID_SELECTION

    except ValueError:
        return_val = ExitCode.INVALID_SELECTION

    else:
        return_val = ExitCode.SUCCESS

    finally:
        tracking.untrack_unlinked()
        db.dump()

    return return_val.value


if __name__ == "__main__":
    exit(main())
