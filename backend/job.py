from utils import update

# this script can be run multiple times per day safely

if __name__ == "__main__":

    try:
        update()
    except:
        pass
