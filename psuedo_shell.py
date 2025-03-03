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
        elif args[0] == self.exit:
            os.write(1, "exiting shell, bye!".encode())
            sys.exit(0)
            
        else:
            os.write(1, "unknown command".encode())

    def parse(self, shell_in):
        commands = []
        cmnds = shell_in.split('|')
        print(cmnds)
        for cmnd in cmnds:
            cmnd = cmnd.strip()
            print(f"Parsing command: {cmnd}")
            sect = cmnd.split(" ")

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
                part2 = cmnd[out_ind+1:]
                commands.append({'cmd': sect[0].strip(),
                                 'args': part1.strip(),
                                 'input': None,
                                 'output': part2.strip()})
                
            elif in_ind:
                part1 = cmnd[:in_ind]
                part2 = cmnd[in_ind+1:]
                commands.append({'cmd': sect[0].strip(),
                                 'args': part1.strip(),
                                 'input': part2.strip(),
                                 'output': None})
                
            else:
                commands.append({'cmd': sect[0].strip(),
                                 'args': cmnd.strip(),
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
            print(shell_input)
            
            #for built in functions
            for_stand = shell_input.split(" ")
            if for_stand[0].lower() in self.commands:
                self.run_base_command(for_stand)
                continue

            #otherwise proceed with parsing
            results = self.parse(shell_input)

            if not results:
                continue

            cmd_0, cmd_1 = results if len(results) != 1 else (results[0], None)
            print(cmd_0)

            pr, pw = None, None
            if cmd_1:
                pr, pw = os.pipe()
                for f in (pr, pw):
                    os.set_inheritable(f, True)
                print("pipe fds: pr=%d, pw=%d" % (pr,pw))

            import fileinput

            rc = os.fork()

            if rc < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)

            elif rc == 0:                 # child
                self.redirect(cmd_0)

                #for piping
                if cmd_1:
                    os.close(pr)
                    os.dup(pw)
                    for fd in (pr, pw):
                        os.close(fd)
                    print("child created")

                self.execute(cmd_0)
                
            else:                           # parent (forked ok)
                if cmd_1:
                    print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
                    os.close(pw)
                    childPidCode = os.wait()

                    rc2 = os.fork()

                    if rc2 < 0:
                        os.write(2, ("fork 2 failed, returning %d\n" % rc).encode())
                        sys.exit(1)
                    elif rc2 == 0:
                        self.redirect(cmd_0)
                        os.dup2(pr, 0)
                        os.close(pr)

                        self.execute(cmd_0)
                    else:
                        os.close(pr)
                        childPidCode = os.wait()
                
                else:
                    childPidCode = os.wait() #commence waiting

            

            
                
                

    def execute(self, args):
        command = args['cmd']
        arguments = args['args'].split()
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            print(args)
            program = f"{dir}/{command}"
            try:
                os.execve(program, arguments, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly


        os.write(2, ("Child:    Could not exec %s\n" % args['cmd']).encode())
        sys.exit(0)

sh = Shell()
sh.run()
