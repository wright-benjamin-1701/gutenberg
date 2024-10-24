from utils import update
from report import report

# this script can be run multiple times per day safely

if __name__ == "__main__":

    try:
        update()
    except:
        pass

    try:
        report()
    except:
        pass
