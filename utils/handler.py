import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-r", "--remove", help="remove all records from database.db", action="store_true"
)
parser.add_argument("-d", "--daemon", help="exec in daemon mode", action="store_true")
parser.add_argument(
    "-w", "--write", help="save results in dump.csv", action="store_true"
)
parser.add_argument(
    "-i",
    "--iteration",
    help="make one iteration for make users from KSC",
    action="store_true",
)

args = parser.parse_args()
