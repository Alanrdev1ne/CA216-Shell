#!/usr/bin/python3

"""
Student Name: Alan Devine
ID Number: 17412402
SOC Username: devina24
"""

import curses
import os
import getpass
import subprocess
import sys
import multiprocessing
from cmd import Cmd


class MyShell(Cmd):

    """Base Class for Shell"""

    def do_cd(self, arg):

        """cd:
        Takes 1 argument, a path to the desired directory.
        In the absence of an argument, The current working directory will
        be printed to the terminal.
        """

        if arg:

            # in the event that the path given is not a real directory
            # an OS error will be raised

            try:
                os.chdir(arg)

                # update the prompt with the new current working directory
                self.prompt = make_prompt()

            except OSError:
                return "Sorry, {} is not a valid directory".format(arg)

        # if there is no argument the current working directory will be
        # for printing returned

        else:
            return os.getcwd()

    def do_dir(self, arg):

        """dir:
        Lists the contents of a given directory,
        This will list either the directory found in an argument,
        or the current working directory if no argument is provided.
        """

        if arg:
            dir_contents = os.listdir(arg)

        else:
            dir_contents = os.listdir(".")

        # because the value is being returned, a string must be created

        string_lines = []
        current_line = ""

        for file_name in dir_contents:

            # in the case that the length of the current line plus the length
            # of the file name are greater than the width of the terminal,
            # the current line will be appended to the string lines variable
            # and current_line will be cleared. This may seem like overkill,
            # but I don't trust screen wrapping (don't ask me why)

            if len(current_line) + len(file_name) > os.get_terminal_size()[1]:
                string_lines.append(current_line.strip())
                current_line = ""

            current_line += file_name + " "

        string_lines.append(current_line.strip())

        return "\n".join(string_lines)

    def do_clr(self, arg):

        """clr:
        Clears the terminal using an ansi escape sequence.
        """

        print("\033c", end="")

    def do_environ(self, arg):

        """environ:
        Lists the shell's environment variables.
        """

        env_variables = os.environ
        env_string = ""

        for k, v in env_variables.items():
            env_string += "{}= {}\n".format(k, v)

        return env_string

    def do_echo(self, arg):

        return " ".join(arg.split())

    def do_help(self, arg):

        with open("readme", "r") as f:

            if arg is "True":
                with open("readme", "r") as f:
                    return f.read()

            lines = f.readlines()
            start_line = 0
            max_line = len(lines)

            # Ascii value for white space
            char = 0

            while True:
                # if the last character entered is white space, continue
                if char == 0:

                    if start_line + 25 > max_line:

                        remainder = start_line + 25 - max_line
                        print("".join(lines[start_line:remainder]))

                        return None

                    else:
                        print("".join(lines[start_line:start_line + 25]))
                        start_line += 25

                # read is a bash command for reading input and with these
                # arguments it will only read a single character

                char = os.system("read -n1 ans")

                # This is cheating a little but my options were this
                # rewriting this using the curses module or copying and
                # pasting code that I didn't understand from stack overflow

    def do_pause(self, arg):

        """pause:
        Prevents the user from interacting with the shell until the enter
        key is pressed.
        """

        # getpass is a module for taking passwords as inputs, one of it's
        # features is that it will mask user input.

        getpass.getpass("Press Enter to resume the shell")

    def do_quit(self, arg):

        """quit:
        Quits this shell, for a better shell :(
        """

        # quit() is a built in python function for quitting things...

        quit()

    def default(self, arg):

        """In the case that a given command isn't supported by this shell/ or
        is a program that could be run, this method will trigger
        """

        print("Sorry, '{}' is not a valid command".format(arg))

    def onecmd(self, line):

        """onecmd:
        Modified version of onecmd method found in the cmd class,
        for reference here is the path, "/lib64/python3.6/cmd.py".

        The main reason behind the need to modifie the origonal method
        is that I'm working with return statments rather than print
        statments.
        """

        # once the end of file is met, the program will exit.

        if line == "EOF":

            # we need to print a newline as once we return to the host shell
            # the prompt will appear on the same line as the last line of this
            # shell.

            print()

            # do_quit takes an argument so I'm just passing in an empty string

            self.do_quit("")

        # splitting the line given by the user into it's relative parts, e.g.
        # ["cmd", "arg", "arg", ">", "output_file"]

        line_components = line.split()

        cmd = line_components[0]
        cmd_args = line_components[1:]

        # if I/O redirection is needed, the line components will be passed to
        # the redirect method.

        if ">>" in line or ">" in cmd_args:

            # because of the way "help" is run, it requires an extra argument

            if cmd == "help":
                line_components.insert(1, "True")

            self.redirect(line_components)

        # otherwise the command will be run normally

        else:
            return self.runcmd(cmd, cmd_args)

    def runcmd(self, cmd, arg):

        """runcmd:
        Method for running commands given by the user
        """

        try:

            do_cmd = getattr(self, "do_" + cmd)
            arg = " ".join(arg)

            return do_cmd(arg)

        except AttributeError:

            if arg and arg[-1] == "&":

                # Creates a background process

                subprocess.Popen([cmd] + arg[:-1], stdout=subprocess.PIPE)

            else:
                try:

                    # Creates foreground process

                    subprocess.run([cmd] + arg)

                except OSError:

                    # If there is no command/ program that can be executed,
                    # default will be called.

                    self.default(cmd)

    def redirect(self, line):

        """Redirect:
        Method for dealing with I/O redirection.
        Takes 1 argument, the line inputted in the shell.

        Only Works with outputting/ appending the output of a command into
        a given file
        """

        if ">>" in line:
            stop = line.index(">>")

            # set mode to append

            mode = "a"

        elif ">" in line:

            stop = line.index(">")

            # set mode to write
            mode = "w"

        # everything prior to ">" or ">>" will be stored as cmd

        cmd = line[:stop]

        # the last item in the list will be the output file

        output_file = line[-1]

        # in the even that the command we are trying to run isn't a built in
        # command, an Attribute error will be raised

        try:

            # getattr() is a method for finding class attributes, such as
            # methods or variables. Since we don't want to run any of the
            # supporting commands like postcmd or runcmd, "do_" is prefixed
            # to the beginning of the command.

            do_cmd = getattr(self, "do_" + cmd[0])
            arg = " ".join(cmd[1:])
            output = do_cmd(arg)

        except AttributeError:

            cmd = subprocess.run(cmd, stdout=subprocess.PIPE)

            # the output of subprocess.run is in byte form, therefore
            # we have to decode it into utf

            output = cmd.stdout.decode("utf-8")

        finally:

            # after we get the output of either a supported command or a
            # program installed on the machine, we write the output to the
            # given file, using the appropriate mode.

            with open(output_file, mode) as f:
                f.write(output)

    def postcmd(self, cmd_val, line):

        """postcmd
        Prints the return value of a command.
        """

        # Sometimes the return value is None, in which case we don't want to
        # print.
        if cmd_val:
            print(cmd_val)

        # we still want a newline even if there's nothing to print
        else:
            print()


def make_prompt():

    """Make Prompt:
    Function for creating the shell's prompt. Modeled after the fedora prompt,
    because I'm not very creative.
    """

    # user is an environment variable
    user_name = os.environ["USER"]
    cwd = os.getcwd()
    return "[{} in {}] ".format(user_name, cwd)


def main():

    # create a instance of MyShell
    shell = MyShell()

    # generate prompt
    shell.prompt = make_prompt()

    # in the case that a batch file/ script is given, all lines will be put in
    # the shell's cmd queue as well as a call to quit the shell.

    if len(sys.argv) > 1:
        script = sys.argv[1]
        with open(script, "r") as s:
            for cmd in s.readlines():
                shell.cmdqueue.append(cmd)
            shell.cmdqueue.append("quit")

    # begin the command loop
    shell.cmdloop()


if __name__ == "__main__":
    main()
