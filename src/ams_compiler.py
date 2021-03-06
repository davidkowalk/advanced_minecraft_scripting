import warnings

help_str = """
ams transpiler is designed for mincraft mcfunctions to be transformed from a more human readable version into a minecraft runnable version.

-h  Show this message
    Alias: --help, --h

===========================

-c  Provide a config file.
    ams -c [filename]

-i  Provide input file.
    Not compatible with -c
    ams -i [filename]

-o  Provide an output file
    Not Compatible with -c.
    Must first provide input file with -i [filename]
    ams -i [filename] -o [filename]

-p  Creates project file. Must comply with following format:
    ams -p [project file] -i [filename(s)] -o [filename(s)]
    Alias: --createproject

    Example: ams -p project.json -i in1 in2 in3 -o out1 out2 out3

-a  Defines an alias in an existing project. Must comply with the following format:
    ams -a <key> <value> <project>

    If any string contains a space the string must be surrounded by quotation marks.
    Example:

    ams -a location \"x y z\" project.py

-d  Show debug information
    ams [options] -d

    Alias: --debug
"""

def main():
    import json
    from sys import argv as args

    # Initialiizing to read args from command line
    arg_pointer = 1

    cdict = {}
    config = False
    input = False
    output = False
    debug = False
    args_supplied = False

    # import args from command line

    if len(args) == 1:
        print("Must provide args. Type 'ams -h' for help.")
        exit(1)

    elif args[arg_pointer] == "-h" or args[arg_pointer] == "--h" or args[arg_pointer] == "--help":
        print(help_str)
        exit()

    elif args[arg_pointer] == "-p" or args[arg_pointer] == "--createproject":
        create_project(args, 1, json)
        exit()

    elif args[arg_pointer] == "-a" or args[arg_pointer] == "--define":
        add_definition(args, 1)
        exit()


    while arg_pointer < len(args):

        if args[arg_pointer] == "-c":
            config = True
            args_supplied = True
            try:
                cfile = args[arg_pointer+1]
            except:
                raise ValueError("Please supply a config file")

            arg_pointer += 2
            continue

        if args[arg_pointer] == "-i" and config == False:

            args_supplied = True
            input = True
            try:
                cdict["ifiles"] = [args[arg_pointer+1]]
                if not output:
                    cdict["ofiles"] = ["out_"+args[arg_pointer+1]]
            except:
                raise ValueError("-i requires an input file.\nUsage: -i [filename]")


            arg_pointer += 2
            continue

        if args[arg_pointer] == "-o" and config == False:

            args_supplied = True
            output = True
            try:
                cdict["ofiles"] = [args[arg_pointer+1]]
            except:
                raise ValueError("-o requires an input file.\nUsage: -o [filename]")

            arg_pointer += 2
            continue

        if args[arg_pointer] == "-d" or args[arg_pointer] == "--debug":

            args_supplied = True
            debug = True
            arg_pointer += 1
            continue


        print(f"Did not recognize this argument: {args[arg_pointer]}. Ignoring...")
        arg_pointer += 1

    if not args_supplied:
        print("Must provide args. Type 'ams -h' for help.")
        exit(1)

    # Read Config file

    if config:
        try:
            with open(cfile) as file:
                loaded_config_dict = json.load(file)
        except:
            raise ValueError(f"Failed to read config file {cfile}")

        # Check Values

        if not ("ifiles" in loaded_config_dict and "ofiles" in loaded_config_dict):
            raise ValueError("Config file must provide ifiles and ofiles.")
        elif len(loaded_config_dict["ifiles"]) != len(loaded_config_dict["ofiles"]):
            raise ValueError(f"Number of input files must match output files.")

        cdict = {**loaded_config_dict, **cdict}

    # Read and compile each file in config.
    if debug:
        print("Config:\n")
        print(json.dumps(cdict, indent = 2))

    for i in range(len(cdict["ifiles"])):
        in_file = cdict["ifiles"][i]
        out_file = cdict["ofiles"][i]

        print(f"Compiling {in_file}...")

        with open(in_file, "r") as inf:
            in_text = inf.read()

        if "define" in cdict:
            for alias in cdict["define"]:
                in_text = in_text.replace(alias, cdict["define"][alias])

        in_text = in_text.split("\n")

        tree_list = build_tree(in_text, debug=debug)

        out_text = compile_tree_list(tree_list)

        with open(out_file, "w") as out:
            out.write(out_text)

        print("DONE!\n")

def add_definition(args, pointer):
    from os.path import isfile
    import json
    """
    Creates a definition for a project file.
    Usage: ams -d <key> <value> <project file>
    """

    if len(args) < 5:
        print("Did not provide enough arguments.")
        return

    key = args[pointer+1]
    value = args[pointer+2]
    path = args[pointer+3]


    if not isfile(path):
        print(f"\"{path}\" is not a file.")
        return

    try:
        with open(path, "r") as f:
            content_dict = json.load(f)
    except:
        print(f"Failed to read json at \"{path}\"\nPlease create a valid file first. (See -h)")
        return

    # Create definition if it does not exist
    if not "define" in content_dict:
        content_dict["define"] = dict()

    if key in content_dict["define"]:
        print(f"{key} already exists: {content_dict['define'][key]}.")


        while True:
            answer = input("Would you like to overwrite? (Y/N): ")

            if answer == "N" or answer == "n":
                print("Aborting.")
                return
            elif answer == "Y" or answer == "y":
                break
            else:
                print("Invalid answer.\n")

        content_dict["define"][key] = value

    else:
        content_dict["define"][key] = value


    with open(path, "w") as f:
        json.dump(content_dict, f, indent=2)

    return



def create_project(args, arg_pointer, json):
    """
    Creates Project file from console args.
    Usage: ams -p <project file> -i <filename(s)> -o <filename(s)>
    """
    out_filename = args[arg_pointer+1]
    print(f"Creating Project {out_filename}!")
    arg_pointer += 2

    reading_in = False
    reading_out = False

    infiles = list()
    outfiles = list()

    while arg_pointer < len(args):

        if args[arg_pointer] == "-i":
            reading_in = True
            reading_out = False

        elif args[arg_pointer] == "-o":
            reading_in = False
            reading_out = True

        elif reading_in:
            infiles.append(args[arg_pointer])

        elif reading_out:
            outfiles.append(args[arg_pointer])

        else:
            print("Unknown Command\nType \"ams -h\" for help.")
            exit()

        arg_pointer += 1

    # print(f"Infiles: {infiles}")
    # print(f"Outfiles: {outfiles}")
    if len(infiles) != len(outfiles):
        print("\nWARNING: Number of input and output files does not match.\n")

    dict = {"ifiles": infiles, "ofiles": outfiles}

    with open(out_filename, "w") as f:
        json.dump(dict, f, indent=2)

    print("DONE!")


def build_tree(file, debug = False):
    """
    Takes in a list of strings and builds a command tree from it.
    Each child gets defined with one indent (Tab) more than it's parent. Example:

    execute if condition1
        if condition2
            run command 1
            run command 2
        if condition3
            run command 1
            run command 2
    """

    line = 0
    tree_list = []

    while line < len(file):
        # Get current command
        command = file[line]

        # SKip empty and comments
        if len(command.strip()) == 0:
            line += 1
            continue

        next_tree, line = __build_element__(file, line, debug = debug)

        tree_list.append(next_tree)

    return tree_list


def __build_element__(file, line, debug = False):
    """
    Look at given line of file. If it's a comment create marker, if empty skip it and if neither create node.

    Then look at all following lines. If the indent is greater than the current on, execute __build_element__ on the next line and add the returned element as a child. The returned line is the next line to be checked.

    If the indent is equal or smaller return
    """
    # Get current command
    command = file[line]

    #If empty return
    if len(command.strip()) == 0:
        return None, line

    # Count indents and cast to node
    #indent = command.count(indent_marker)
    indent = __count_indents__(command)

    if command.strip().startswith("#"):
        current_element = marker(command.strip())
    else:
        current_element = node(command.strip())

    next_line = line+1

    #As long as you have not reached end of file
    while next_line != len(file):
        if debug:
            print("Line: ", next_line, "\t", file[next_line])

        # Add all children
        next_command = file[next_line]

        if len(next_command.strip()) == 0:
            next_line += 1
            continue

        next_indent = __count_indents__(next_command)

        if next_indent > indent:
            next_child, next_line = __build_element__(file, next_line, debug)
            current_element.add_child(next_child)
        else:
            break



    return current_element, next_line


def compile_tree_list(tree_list):
    """
    Compiles node.compile for each element in the list and
    compiles the string to be pasted into the file.
    """
    compiled_list = []
    for tree in tree_list:
        compiled_list += tree.compile()

    compiled_string = ""
    for element in compiled_list:
        compiled_string += element+"\n"

    return compiled_string


def __count_indents__(string):
    # Accept either "\t" or " " as indent.

    indent_chars = ["\t", " "]

    indents = 0
    for char in string:
        if char in indent_chars:
            indents += 1
        else:
            break

    return indents

class marker:
    def __init__(self, string):
        self.string = string

    def add_child(self, child):
        warnings.warn(f"Cannot add child to comment.")

    def to_str(self, n=1):
        return self.string

    def compile(self, parent = ""):
        """
        Returns marker as while stacktrace.
        parent
            marker

        compiles to:
        [
            \"marker\"
        ]
        """
        return [self.string]

class node:
    """
    Tree Node for command tree.
    """

    def __init__(self, string):
        self.string = string
        self.children = []

    def add_child(self, child):
        """
        Accepts either Strings or cmd_node objects. Adds child to children list
        """

        if type(child) == str:
            child = node(child)

        self.children.append(child)

    def to_str(self, n=1):
        """
        Bakes String of self and all children
        """
        #print(n)
        ret_str = self.string
        for child in self.children:
            ret_str += "\n"+"\t"*n+child.to_str(n+1)

        return ret_str

    def compile(self, parent = ""):
        """
        Compiles tree into list. Example:
        execute if condition
            run command1
            run command2

        gets compiled to:
        [
            execute if condition run command1,
            execute if condition run command2
        ]
        """
        next_str = parent + self.string + " "
        next_list = []


        if len(self.children) > 0:
            for child in self.children:
                next_list += child.compile(next_str)

            return next_list
        else:
            return [next_str]


if __name__ == '__main__':
    main()
