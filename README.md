# pdp11-utils

Found here is a collection of scripts I've needed to author for some reason or another while dealing with a PDP-11--particularly, a PDP-11/73 resurrected from an electronics recycling center. They are all quite disparate, poorly written, and not particularly well-documented in their own source, so I will do the best to keep this up to date.

For more of the struggle, visit the relevant [docs page](http://docs.cslabs.clarkson.edu/wiki/Developing_for_a_PDP-11). You may wish to proceed there to see how to build a GCC cross-compiler (as many of these tools are meant to be part of that toolchain), or for more information on the "standard format binary tape" of [simh](https://github.com/simh/simh/)'s contrivance.

All of these are licensed under the Boost Software License. Take what you need.

## mkterp.py

```
Usage: python mkterp.py {BLOCK} {BLOCK} {BLOCK}
where each {BLOCK} is:
	[-O <origin>] to set the origin (default 1)
	-d <file> a binary file to read in data (terminates the block).
OR:
	-o <fname> to set the output file name (last instance wins).
OR:
	-p <pc> to set the address at which the program shall start (last instance wins).
```

Creates a "standard format binary tape" as required by [simh](https://github.com/simh/simh/)'s pdp11 simulator. In particular, files created by this (by default, `image.out`) are valid to be used with the simulator's `load` command. At some point, in the near future, it will also be used as the input format for a tool that can talk with the PDP-11's octal debugger to set the processor memory in the same way as the simulator.

The simulator has a way of specifying the PC that should be set after tape load. It is entirely valid (though superfluous, unless merging tapes) to make a tape containing only the section that sets the PC (by specifying -p alone). Without -p, the resulting tape does not set the PC.

## shterp.py

```
USAGE: python shterp.py [<options>] <tape> [<tape> [...]]

Where <tape> is a "standard binary format tape" (as with mkterp.py).

Options:
    -m <image> makes an binary image file of memory that would be the result
        of loading these tapes into empty (zeroed) memory in the specified
        order.
    -o <tape> outputs a merged tape, the result of combining all the tapes
        in the order specified. The origin PC will be the origin PC of the
        last tape that has one set to non-default (non-1). If no such tape
        exists, the output will have a default PC (1). mkterp.py with only
        the -p option can make an empty tape to force the PC to a certain
        value by including it at the end of the list.
    -s causes the program to be strict about checksums (default lenient).
```

Reads and validates standard format tape files. This can be used to extract their encoded information as a memory dump (which can be again encoded as an "image" tape using mkterp.py with `-O 0 -d dump`) or merge tapes together as needed. In the near future, it may be able to recover the data from these tapes as well.

## tinycom.py

TinyCom is a raw-mode serial terminal that depends on [pySerial](http://pyserial.sourceforge.net/). It was designed specifically to interface with the real serial console on the PDP-11/73, addressing many shortcomings of minicom for this purpose (basically, that minicom used line buffering and expected that it would be emulating a "real" VT). Because it runs in raw mode, most keystrokes are passed to the interface verbatim--get used to ^J for newline and the fact that "Return/Enter" is now carriage return. Every effort has been made to make the input as responsive as possible--buffering is actively disabled insofar as it can be. The end result does feel like a real serial console.

While running, ^C (the interrupt key sequence) will display the "^C menu", a cryptic blob of text indicating that it is ready to take a special command. Pressing h/H will give a slightly less cryptic description (but also take it out of ^C mode):

```
[[[^C mode commands:
    -h,H: this help text
    -q,Q: quit
    -e,E: toggle local echo
    -F: send local file
    -f: send local file, throttled
    -t, T: view/set throttle rate
    -^C: send ^C]]]
```

Acquaint yourself with using ^C,q to quit. When sending a file (using f/F), throttling may be necessary with ODT, having experience multiple occasions where it misinterprets valid commands encoded ahead-of-time in binary files because of dropped characters (remember: the PDP-11's serial console interface was generally designed around a one-character buffer, and the thing only usually runs at, at most, 15MHz). Obviously, how quickly it can respond to input depends on the load, but full-force 9600 baud was too much for ODT, whereas 1ms/byte pauses sufficed. Your mileage may vary.

All printouts generated by this program generally try to surround themselves with `[[[` and `]]]`, so you can identify what output what (it won't save you if a PDP-11 program does the same, obviously). During file upload, the serial input (from the 11) can intersperse with progress messages. Sorry, that's how it do.

Remember to use a null-modem or crossover cable! Both the computer you run this on and the PDP-11 are probably configured as DTEs.

## mkodt.py

Prints to stdout a (binary!) file consisting of the ODT commands required to set the memory of a PDP-11 to whatever would be loaded by the tape. If the tape sets PC, this will cause the PDP to run it, assuming HALT isn't set. Note that this makes absolutely no assumptions about memory mapping, valid addresses, errors during the upload, etc.; it just generates an offline file that *might* work if you cat it to the serial console while ODT is running. (Throttling may be required; tinycom.py can help you with this.) Files generated this way will be several times bigger than tape formats (because of the octal encoding) and nigh impossible to recover data from, and so they are generally unsuitable for distribution. Also, you can't just do this with a "raw" image (or an a.out, for that matter), but using mkterp.py with `-O 0 -d image` is fairly trivial, if a nuisance. Remember to redirect this to a file!

This program does *not* validate the tape using the embedded checksums. shterp.py with `-s` will do this for you. And, of course, if the file is the immediate output of mkterp.py (and I don't suck at programming), it should be valid anyway.