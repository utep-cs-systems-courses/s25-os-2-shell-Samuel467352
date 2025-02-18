#! /user/bin/env python3

import os, sys, time, re

while 1:
    os.write(1, ">>".encode())

    command = os.read(0, 100000).strip()

    if command.decode() == 'exit':
        os.write(1, "bye\n".encode())
        sys.exit(1)

    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        continue
    elif rc == 0:
        pass
    else:
        childPidCode = os.wait()
        continue
