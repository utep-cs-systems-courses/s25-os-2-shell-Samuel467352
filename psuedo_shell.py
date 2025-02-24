#! /user/bin/env python3

import os, sys, time, re

class Shell:
    def __init__(self):
        self.cd = "cd"
        self.exit = "exit"
        self.commands = [self.cd, self.exit]
    def run_base_command(self, args):
        if args[0] == self.cd:
            try:
                os.chdir(args[1])
            except FileNotFoundError:
                print("Directory was not found")
                return
        else:
            os.write(1, "bye".encode())
            sys.exit(0)

    def parse(self, shell_in):
        commands = []
        cmnds = shell_in.split("|")
        for cmnd in cmnds:
            cmnd = cmnd.split(" ")

            out_ind = None
            in_ind = None
            
            #get the indexs for redirects
            try:
                out_ind = cmnd.index(">")
            except:
                out_ind = None
            try:
                in_ind = cmnd.index("<")
            except:
                in_ind = None


            if out_ind:
                part1 = cmnd[:out_ind]
                part2 = cmnd[out_ind:]
                commands.append({'cmd': part1[0],
                                 'args': part1[0:],
                                 'input': None,
                                 'output': part2})
                
            elif in_ind:
                part1 = cmnd[:in_ind]
                part2 = cmnd[in_ind:]
                commands.append({'cmd': part1[0],
                                 'args': part1[0:],
                                 'input': part2,
                                 'output': None})
                
            else:
                commands.append({'cmd': cmnd[0],
                                 'args': cmnd[0:],
                                 'input': None,
                                 'output': None})
        return commands
    
    def redirect(self, cmd):
        if cmd['input']:
            os.close(0)
            os.open(cmd['input'], os.O_RDONLY)
            os.set_inheritable(0, True)

        if cmd['output']:
            os.close(1)
            os.open(cmd['output'], os.O_CREAT | os.O_WRONLY)
            os.set_inheritable(1, True)
            

            
    def run(self):
        while 1:
            #get ps1 and print it onto the command line
            ps1 = os.getenv("PS1", "$ ")
            os.write(1, ps1.encode())


            #get args from standard input
            shell_input = os.read(0, 10000).decode().strip()
            
            #for built in functions
            for_stand = shell_input.split(" ")
            if for_stand[0].lower() in self.commands:
                self.run_base_command(for_stand[0])

            #otherwise proceed with parsing
            results = self.parse(shell_input)

            if not results:
                continue

            cmd_0, cmd_1 = results if len(results) != 1 else (results[0], None)

            rc = os.fork()

            if rc < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)

            elif rc == 0:                 # child
                self.redirect(cmd_0)

                if cmd_1:
                    pass #piping is not yet implemented
                self.execute(cmd_0['args'])
                
            else:                           # parent (forked ok)
                if cmd_1:
                    pass #piping is not yet implemented
                else:
                    childPidCode = os.wait() #commence waiting

            

            
                
                

    def execute(self, args):
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args)
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly

            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(0)

sh = Shell()
sh.run()
