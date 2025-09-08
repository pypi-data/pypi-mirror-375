from .load import *

def main():
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "load.1_1":
            load_1_1()
        elif command == "load.1_2":
            load_1_2()
        elif command == "load.3_1":
            load_3_1()
        elif command == "load.3_2":
            load_3_2()
        elif command == "load.4_1":
            load_4_1()
        elif command == "load.4_2":
            load_4_2()
        elif command == "load.5_1":
            load_5_1()
        elif command == "load.5_2":
            load_5_2()
        else:
            print("Unknown command")
    else:
        print("Usage: tensorneflow <command>")

if __name__ == "__main__":
    main()