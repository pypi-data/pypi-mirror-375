#
# PROGRAM: CONJUNO
# MODULE : log
#

DEBUG = 0

from sys import stdout 
from datetime import datetime
from traceback import format_exc
import inspect
from datetime import datetime

# EXCEPTION HANDLER
def exc_handl(e, msg, warning=True):
    if e is None:
        e = "Undefined Error"
    if DEBUG > 2:
        traceback.print_exc(file=sys.stdout)
    if DEBUG > 1:
        plog(msg, 2)  # CHANGE HERE
    if warning:
        if e is not None:
            plog("[!] Exception message: " + str(e))
    return P_EXIT_FAILURE

# using datetime module
def plog(message, message_priority=1):
    if message_priority > 0 or DEBUG == 1:
        cdt = datetime.now()
        print(
            "["
            + str(cdt)
            + "]["
            + str(message_priority)
            + "]["
            + inspect.stack()[1].function
            + "]["
            + str(inspect.stack()[1].lineno)
            + "]: "
            + str(message),
            flush=True,
        )

def deb(msg="None"):
  
  now = datetime.now()
  dt = now.strftime("%Y%m%d %H:%M:%S")
  try:
    f = open("/tmp/conjuno.log", "a")
  except Exception as e:
    f = open("conjuno.log", "a")
  f.write("\n"+dt+"|"+str(_getframe().f_back.f_lineno)+"|"+msg)
  f.close()
  print_exc(file=stdout)

def log(logstr):
  if DEBUG >= 1:
    now = datetime.now()
    dt = now.strftime("%Y%m%d %H:%M:%S")
    try:
      f = open("/tmp/conjuno.log", "a")
    except Exception as e:
      f = open("conjuno.log", "a")
    f.write("\n"+dt+"|"+str(logstr))
    if DEBUG >= 2:
      exc = format_exc()
      if str(exc)[:-1] != "NoneType: None":
        f.write("\n"+dt+"|Traceback:")
        f.write("\n"+str(exc)[:-1])
    f.close()

def caller(func):
  log("caller")
  #cuurent_frame = currentframe()
  #caller_frame = cuurent_frame.f_back
  #filename, lineno, function, code_context, index = getframeinfo(caller_frame)
  #caller_instance = caller_frame.f_locals['self']
  #log(f'caller instance: {caller_instance}')  # → obj
  #log(f'caller from class: {type(caller_instance).__name__}')  # → B
  #log(f'caller from method: {function}')  # → class_B_fun

