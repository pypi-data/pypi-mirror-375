# encoding=utf-8
#
# PROGRAM: CONJUNO
# MODULE : main
# 

# set your locale
#locale.setlocale(locale.LC_ALL, '')    

# python libraries import
from getopt import getopt, GetoptError
from os import sep
from pathlib import Path 
from sys import argv, exit, stdout, path
try: # windows compatible
  from signal import signal, SIGWINCH
except Exception as e:
  pass

# program libraries import
from conjuno._version import __version__
from conjuno.notebook import Notebook
from conjuno.log import log
from conjuno.log import plog
from conjuno.log import exc_handl

nb=None

def version_callback():
  txt="conjuno {ver}".format(ver=__version__)
  print(txt)
  exit()

def help_callback():
  txt="""
 conjuno {ver} [ console jupyter notebooks ]

 -d, --debug
   turns on kernel debug messages

 -h, --help
   prints this help

 -k kernel_type, --kernel kernel_type
   runs conjuno with specified kernel
   when no kernel is specified python3
   kernel is used

 -n, --no-kernel
   runs conjuno with no kernel

 -v, --version
   displays the current program version

 -r, --run
   runs notebook and saves result 
   into <fname>_run.ipynb

""".format(ver=__version__)
  print(txt)
  exit()

def main():
  global nb
  # default filename
  def_fname = "Untitled"
  try:
    # "k:rvldn",
    opts, args = getopt(
      argv[1:],
      "k:dhnrv", [ 
        "debug",
        "help",
        "kernel",
        "no-kernel",
        "run",
        "version",
      ]
    )
  except GetoptError as e:
    print(e)
    exit(1)

  #print(str(opts))
  #print(str(args))
  
  fname=def_fname
  fext=".ipynb"
  # if there is one argument 
  # provided it possibly a filename
  if len(args)==1:
    # if there is a dot in the filename
    if args[0][-6:]==fext:
      #print("1 argument own file ext")
      fname=args[0]
    else:
      #print("1 argument not our file ext")
      fname=args[0]+fext
  elif len(args)==0:
    #print("No arguments")
    fname+=fext
  else:
    #print("More than 1 argument")
    fname+=fext
  #print(fname)

  notebook_path = Path(".",fname)
  kernel_cwd = notebook_path.parent
  save_path = None
  no_kernel = False
  debug = False
  fold = False
  mode = "interactive"
  kernel = "python3"

  #PP 
  #PP  -d, --debug
  #PP    turns on kernel debug messages
  #PP
  #PP  -h, --help
  #PP    prints this help
  #PP
  #PP  -k kernel_type, --kernel kernel_type
  #PP    runs conjuno with specified kernel
  #PP    when no kernel is specified python3
  #PP    kernel is used
  #PP
  #PP  -n, --no-kernel
  #PP    runs conjuno with no kernel
  #PP
  #PP  -v, --version
  #PP    displays the current program version
  #PP
  #PP  -r, --run
  #PP    runs notebook and saves result 
  #PP    into <fname>_run.ipynb
  #PP    
  for o, a in opts:
    if o in ("-d","--debug"):
      debug = True
    elif o in ("-h","--help"):
      help_callback()
    elif o in ("-k","--kernel"):
      if a == '': 
        kernel = "python3"
      else:
        kernel = a
    elif o in ("-n","--no-kernel"):
      no_kernel = True
    elif o in ("-v","--version"):
      version_callback()
    elif o in ("-r", "--run"):
      mode = "batch"
    else:
      print("Unhandled option")
  #print("kernel: "+kernel)
  #print("[*] Loading jupyter client...")
  from jupyter_client.kernelspec import KernelSpecManager
  #print("[*] Loading notebook... ")
  # Prepare Notebook Object
  nb = Notebook(
    notebook_path,
    kernel_cwd=kernel_cwd,
    kernel_name=kernel,
    no_kernel=no_kernel or False,
    save_path=save_path,
    debug=bool(debug),
    fold=bool(fold),
    mode=mode,
  )
  if mode == 'batch':
    import asyncio
    assert no_kernel is not True
    asyncio.run(nb.run_all(mode="batch"))
    if save_path is None:
      directory = notebook_path.parent
      #prefix = str(directory / f"{notebook_path.stem}_run")
      #save_path = find_available_name(directory, prefix)
      save_path = Path(".",fname.replace(".ipynb","_run.ipynb"))
    nb.save(save_path)
    print(f"Executed notebook has been saved to: {save_path}")
  else:
    #nb.init()
    import asyncio
    asyncio.get_event_loop().run_until_complete(nb.init())

def terminal_resize(p_he,p_wi):
  log("[i] main.terminal_resize event")
  nb.c.end_curses()
  nb.c.init_curses()
  nb.c.scr.refresh()
  nb.c.get_term_size()
  nb.layout_reset()
  nb.clear_pads(clear=True)
  nb.valid=0
  nb.update_layout()

def cli():
  try: # windows compatible
    signal(SIGWINCH, terminal_resize)
  except Exception as e:
    pass 
  try:
    main()
  except Exception as e:
    #nb.c.end_curses()
    exc_handl(e,"[ ERR-0010 = main err ]")
    plog("[!] main.cli exception: "+str(e))
    #print("[!] main.cli exception: "+str(e))

if __name__ == "__main__":
  cli()
