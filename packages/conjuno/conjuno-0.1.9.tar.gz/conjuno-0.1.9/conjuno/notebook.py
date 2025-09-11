# encoding=utf-8
#
# PROGRAM: CONJUNO
# MODULE : notebook
#

# curses
import curses

# python libraries import
from asyncio import get_event_loop, create_task, run, CancelledError, ensure_future, sleep
from itertools import chain
from os import environ, chdir, system
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, cast

# jupyter kernel
from kernel_driver import driver as kdriver
from kernel_driver import KernelDriver

# program libraries import
from conjuno._version import __version__
from conjuno.console import Curses
from conjuno.format import Format
from conjuno.help import Help
from conjuno.log import log
from conjuno.keymaps import Keymap, KeymapStack

#from inspect import currentframe, getframeinfo, getmodulename

# CURSES GETCH TIMEOUT INTERVAL
#REFRESH_INTERVAL=900 # in miliseconds 0.9 second
REFRESH_INTERVAL=100 # in miliseconds 0.1 second
# CURSES PADS
PIN=0
POU=1
PSB=2

from conjuno.cell import (
    Cell
)

class Notebook(Help, Format):

    app: None #Optional[Application]
    valid: int # valid and displayed
    filename: str
    #layout: Layout
    copied_cell: Optional[Cell]
    #console: Console
    #console: None
    _run_notebook_nb_path: str
    cells: List[Cell]
    executing_cells: Dict[int, Cell]
    json: Dict[str, Any]
    kd: Optional[KernelDriver]
    execution_count: int
    msg_id_2_execution_count: Dict[str, int]
    current_cell_idx: int
    top_cell_idx: int
    bottom_cell_idx: int
    #lexer: Optional[PygmentsLexer] = PygmentsLexer(PythonLexer)
    language: str
    kernel_name: str
    no_kernel: bool
    dirty: bool
    quitting: bool
    kernel_cwd: Path
    kernel_status: str
    kernel_exe_tm: int
    editor_msg: str
    #search_buffer: Buffer
    search_buffer: None
    marks: List[int]
    debug: bool
    fold: bool
    ext_edit: int
    scr: None
    wi: int
    he: int
    left_margin: int 
    c: Curses
    pad_active: str
    pis: list
    pos: list
    yscr: int
    xscr: int
    lscr: int
    k   : int
    mode: str
    keymap: None
    gmod: int
    output_wrap: bool
    lno: int

    def __init__(
        self,
        nb_path: Path,
        kernel_cwd: Path = Path("."),
        kernel_name: str = "",
        no_kernel: bool = False,
        save_path: Optional[Path] = None,
        debug: bool = False,
        fold: bool = False,
        mode: str = "interactive",
    ):
        log("[o] -------------------------------------")
        log(f"[o] ... conjuno {__version__} ... init [ok]")
        self.mode = mode
        if self.mode != "batch":
          self.c = Curses()
          self.c.init_curses()
        self.pad_active = "I"
        self.valid = 0
        self.status_line_valid = 0
        self.debug = debug
        self.fold = fold
        self.nb_path = nb_path.resolve()
        self.kernel_cwd = kernel_cwd.resolve()
        chdir(self.kernel_cwd)
        # self.app = None
        self.copied_cell = None
        self.console = None #Console()
        #set_console(self.console)
        self.save_path = save_path
        self.no_kernel = no_kernel
        self.kernel_exe_tm = 0
        self.executing_cells = {}
        self.top_cell_idx = 0
        self.bottom_cell_idx = -1
        self.current_cell_idx = 0
        if self.nb_path.is_file():
            self.read_nb()
        else:
            self.create_nb(kernel_name)
        self.filename = self.nb_path.stem
        self.dirty = False
        self.quitting = False
        self.execution_count = 0
        self.msg_id_2_execution_count = {}
        self.edit_mode = False
        self.help_mode = False
        self.search_buffer = None #Buffer()
        self.marks = []
        for i in range(256):
            self.marks.append(0)
        self.editor_msg = "|x|"
        self.ext_edit = 0
        self.left_margin = 5
        #self.c.scr.addstr(self.c.he-1,0,self.get_bottom_bar_text())
        pos = []
        self.force_refresh = 0
        self.k = 32
        if self.mode != "batch":
          # pad input
          self.pis = [0,0,0,0,0,self.c.wi-1]
          # pad output (-2 counts with status line)
          self.pos = [0,0,1,0,self.c.he-2,self.c.wi-1]
          # pad status line
          self.psb = [0,0,self.c.he-1,0,self.c.he-1,self.c.wi-1]
          # scrolling parameters for the pad
          self.yscr = 0
          self.xscr = 0
          self.lscr = 0
          self.focus(0)
          self.gmod=0
          #self.output_wrap=False
          self.output_wrap=True
          self.lno=True
          self.update_layout()

    def set_language(self):
        self.kernel_name = self.json["metadata"]["kernelspec"]["name"]
        self.language = self.json["metadata"]["kernelspec"]["language"]
        #if self.language == "python":
        #    self.lexer = PygmentsLexer(PythonLexer)
        #elif self.language == "javascript":
        #    self.lexer = PygmentsLexer(PythonLexer)
        #elif self.language == "cpp":
        #    self.lexer = PygmentsLexer(CppLexer)
        #else:
        #    self.lexer = None
        if self.no_kernel:
            self.kd = None
        else:
          try:
            self.kd = KernelDriver(kernel_name=self.kernel_name, log=False)
            kdriver._output_hook_default = self.output_hook
          except RuntimeError:
            self.kd = None
 

    def display_help(self):
      log("[?] notebook.display_help")
      help_txt="""----------------------------------------------

           CONSOLE JUPYTER NOTEBOOK

  help - press j,k,q (down, up, exit help)

----------------------------------------------

  Keyboard:

  enter, ctrl+e - run current cell
  t - run as external program (e.g. curses)
  u, page up - scroll fullscreen page up
  n, page down - scroll fulscreen page down
  h, left - scroll fullscreen left more
  l, right - scroll fullscreen right more
  h, left - scroll fullscreen left
  m - toggle markdown cell
  l, right - scroll fullscreen right
  i - switch to input
  o - switch to output
  w - toggle wrap output
  f - switch current pad full-screen
  r - reset layout
  gg - go to first cell
  shift+g (G) - go to last cell
  k, up - previous cell
  j, down - next cell
  a - insert cell above current cell
  a - insert cell below current cell
  x - cut cell
  c - copy the cell
  ctrl+v - paste cell above
  ctrl+v - paste cell below
  s, ctrl+s - save notebook
  e - edit input cell [1]
  ctrl+p - run all cells one by one
  q - quit

----------------------------------------------"""
      self.clear_pads(False)
      self.c.scr.timeout(-1)
      k="0"
      ys=0
      while k!=ord("q"):
        self.c.pad_prn(POU,0,0,help_txt)
        if k==ord("j"):
          if (len(help_txt.split("\n"))-ys>1):
            ys+=1
        elif k==ord("k"):
          if ys>0:
            ys-=1
        self.c.pad_refresh(POU,ys,0,0,0,self.c.he-1,self.c.wi-1)
        k = self.c.scr.getch()
        self.c.get_term_size()
      self.c.scr.timeout(REFRESH_INTERVAL)
      self.valid = 0

    async def kernel_stop(self):
      await self.kd.stop()

    def clear_pads(self,clear=False):
      if clear:
        if sum(self.pis)!=0:
          self.c.pads[PIN].clear()
        if sum(self.pos)!=0:
          self.c.pads[POU].clear()
        self.c.pads[PSB].clear()
      else:
        if sum(self.pis)!=0:
          self.c.pads[PIN].erase()
        if sum(self.pos)!=0:
          self.c.pads[POU].erase()
        self.c.pads[PSB].erase()
        #self.c.scr.erase()

    def is_fullscreen(self):
      ret=0
      # input or output aren fullscreen
      if self.current_cell.json["cell_type"] != "markdown":
        if sum(self.pis)==0 or sum(self.pos)==0:
          ret=1
      return(ret)
       
    def layout_reset(self):
      self.pis = [0,0,0,0,0,self.c.wi-1]
      #self.c.scr.addstr(1,0," "*(self.c.wi-1))
      self.pos = [0,0,1,0,self.c.he-1-1,self.c.wi-1]
      self.psb = [0,0,self.c.he-1,0,self.c.he-1,self.c.wi-1]
      self.yscr = 0
      self.xscr = 0
      self.lscr = 0
      self.valid = 0

    def refresh_input(self):
      self.c.pad_refresh(PIN,
        self.pis[0],self.pis[1],
        self.pis[2],self.pis[3],
        self.pis[4],self.pis[5])

    def refresh_output(self):
      self.c.pad_refresh(POU,
        self.pos[0],self.pos[1],
        self.pos[2],self.pos[3],
        self.pos[4],self.pos[5])

    def refresh_status_line(self):
      self.c.pad_refresh(PSB,
        self.psb[0],self.psb[1],
        self.psb[2],self.psb[3],
        self.psb[4],self.psb[5])

    @property
    def current_cell(self):
        return self.cells[self.current_cell_idx]

    async def run_cell(self, idx: Optional[int] = None):
        if idx is None:
            idx = self.current_cell_idx
        self.focus(idx)
        await self.current_cell.run()
        self.valid=0

    #def goto_last_cell(self):
    #    self.focus(len(self.cells) - 1)

    def goto_first_cell(self):
        self.focus(0)

    def print_bottom_bar(self):
      self.c.pad_prn(PSB,0,0,self.get_bottom_bar_text())

    def print_cell_input(self):
      log("[*] console.print_cell_input")
      ibtxt=""
      #if self.fold:
      #  ibtxt = self.current_cell.input_buffer.split('\n')[0]
      ## if fold is off then print the whole input buffer
      #else:
      ibtxt = self.current_cell.input_buffer
      # HERE
      #if self.current_cell.json["cell_type"] == "markdown":
      #  self.pad_active="I"
      #  self.pis = [0,0,0,0,self.c.he-1,self.c.wi-1]
      #  self.pos = [0,0,0,0,0,0]
      #elif self.current_cell.json["cell_type"] == "code":
      #  self.pad_active="I"
      self.c.pad_prn(PIN,0,0,ibtxt)
      self.valid=0

    # PRINTS CELL OUTPUT INFO (Out)
    def print_cell_execution_count(self):
      log("[*] console.print_cell_execution count")
      #log(str(self.current_cell.json))
      if "execution_count" in self.current_cell.json and self.current_cell.json["cell_type"]!="markdown":
          execution_count = self.current_cell.json["execution_count"]
          if execution_count:
            #shex=len(str(execution_count))
            shex=4
            #if sum(self.pis)!=0 and sum(self.pos)!=0:
            if self.is_fullscreen()==0:
              self.c.pad_prn(PIN,0,self.c.wi-shex-7,"Out: [{:>4d}]".format(execution_count))
      ##else:
      #  self.c.pad_prn(POU,2,0,"{:>4d}".format(0))

    # PRINTS CELL OUTPUT
    def print_cell_output(self,text=""):
      log("[*] console.print_cell_output")
      #cuurent_frame = currentframe()
      #caller_frame = cuurent_frame.f_back
      #filename, lineno, function, code_context, index = getframeinfo(caller_frame)
      #caller_instance = caller_frame.f_locals['self']
      #log(f'caller instance: {caller_instance}')  # → obj
      #log(f'caller from class: {type(caller_instance).__name__}')  # → B
      #log(f'caller from method: {function}')  # → class_B_fun
      #log("[*] console.print_cell_output")
      self.lno=0
      linelen=0
      #self.print_cell_execution_count()
      #if len(text)==0:
      #self.c.pads[POU].clear()
      #text=""
      error_msg=0
      try:
        if "outputs" in self.current_cell.json:
          if self.current_cell.json["outputs"][0]:
            outputs=self.current_cell.json["outputs"][0]
            if outputs:
              if "output_type" in outputs:
                if outputs["output_type"]=="error":
                  error_msg=1
                  text, height = self.current_cell.get_output_text(outputs)
                else:
                  text, height = self.current_cell.get_output_text(outputs)
          else:
            text = ""
            height = 0
      except:
        #pass
        log("[!] notebook.print_cell_output: "+str(text))
      if error_msg==1:
        log("[.] notebook.print_cell_output: "+str(outputs))
        f=open("traceback.tmp","bw")
        f.write(text.encode())
        f.close()
        f=open("traceback.tmp","rb")
        bin_text=f.read()
        f.close()
        self.c.render_ans(self.c.pads[POU],bin_text)
        self.c.pad_refresh(POU,0,0,1,0,self.c.he-1-10,self.c.wi-1)
      else:
        if not self.output_wrap:
          for line in text.split('\n'):
            try:
              self.c.pad_prn(POU,0+self.lno,0,line)
            except:
              break
            self.lno+=1
        else:
          try:
            self.lno=0
            for ly, line in enumerate(text.split('\n')):
              if self.lno>1:
                if len(line)>self.c.wi:
                  for wl in range(0,int(len(line)/self.c.wi)+1): # wrap line
                    #if wl==0 and len(line)>0:
                    #  line="+ "+line
                    self.c.pad_prn(POU,0+self.lno,0,line[(self.c.wi)*wl:(self.c.wi)*(wl+1)])
                    #self.c.pad_prn(POU,0+self.lno,0,str(ly)+" "+str(wl))
                    self.lno+=1
                else:
                  self.c.pad_prn(POU,self.lno,0,line)
                  self.lno+=1
              else:
                self.c.pad_prn(POU,self.lno,0,line)
                self.lno+=1
          except Exception as e:
            log("[!] notebook.print_cell_output: "+str(e))

    async def run_all(self, mode=None):
        if self.kd:
            if not hasattr(self.kd, "kernel_process"):
                try:
                    log("[!] notebook.run_all: starting kernel")
                    await self.kd.start()
                    log("[!] notebook.run_all: kernel started")
                    # print("Starting kd in run_all")
                except Exception as e:
                    # print(str(e))
                    self.kernel_status = "error" + str(e)
                    pass
        for i in range(0, len(self.cells)):
            await self.run_cell(i)
        if mode == "batch":
            if self.kd:
                log("[!] notebook.run_all: stopping kernel process")
                try:
                  await self.kd.stop()
                  log("[!] notebook.run_all: kernel process stopped")
                except Exception as e:
                  log("[!] notebook.run_all: kernel stop exception: "+str(e))
        else:
            self.focus(0)

    async def tmp_run_ext(self,fname):
       system('python3 '+fname) 
       return(0)

    def tmp_edit_cell(self):
       system('vim /tmp/asdf_conjuno_tmp.txt') 
       return(0)

    async def _run_kernel(self):
       if self.kd:
           await self.kd.start()
           log("[@] notebook._run_kernel: starting kernel")
       #await self.app.run_async()

    async def run_current_cell(self):
        try:
          if self.current_cell.json["cell_type"] == "code":
            #await self.run_cell()
            #await self.cell_run()
            #cell_run=ensure_future(self.run_cell())
            #from asyncio import get_event_loop
            #loop = get_event_loop()
            #await self.queue_run_cell()
            # get_event_loop().run(self.queue_run_cell())
            #get_event_loop().run(self.queue_run_cell())
            #from asyncio import get_event_loop
            #loop = get_event_loop()
            #loop.run_until_complete(self.queue_run_cell())
            await self.queue_run_cell()
            #await self.run_cell()
            #self.queue_run_cell()
            self.kernel_exe_tm = 0
            #loop.run_until_complete(self.run_cell())
            #run(self.run_cell())
            #self.kernel_exe_tm = 0
            #self.layout_reset()
            self.valid = 0
        except Exception as e:
          log("[!] notebook.run_current_cell exception: "+str(e))

    def goto_next_cell(self):
       if self.current_cell_idx < len(self.cells):
         #self.go_down()
         self.focus(self.current_cell_idx+1)
         self.layout_reset()
         self.valid=0

    def goto_previous_cell(self):
        if self.current_cell_idx > 0:
          self.go_up()
          self.layout_reset() 
          self.valid=0

    def goto_last_cell(self):
        self.focus(len(self.cells) - 1)
        self.layout_reset() 
        self.valid=0

    def edit_current_cell(self):
        text = self.current_cell.input_buffer
        f=open("/tmp/asdf_conjuno_tmp.txt","w")
        f.write(text)
        f.close()
        self.c.end_curses()
        self.tmp_edit_cell()
        self.c.init_curses()
        f=open("/tmp/asdf_conjuno_tmp.txt","r")
        txt=f.read()
        f.close()
        self.enter_cell()
        self.current_cell.input_buffer = txt
        self.exit_cell()
        #self.current_cell.input_width=self.current_cell.calc_input_width()
        #self.layout_reset()
        self.dirty = True
        self.valid = 0
        #log("[i] notebook input edit cell: "+str(self.current_cell.input_buffer))

    def save_notebook(self):
        self.save()
        self.status_line_valid = 0
        self.valid=0

    def cut_current_cell(self):
        self.cut_cell()
        self.layout_reset()
        self.valid=0

    def reset_layout(self):
        self.layout_reset() 
        self.valid=0

    def toggle_output_wrap(self):
        if self.output_wrap:
          self.output_wrap=False
        else:
          self.output_wrap=True
        self.valid=0

    def switch_current_pad_fullscreen(self):
        if self.pad_active=="I":
          self.pis = [0,0,0,0,self.c.he-1,self.c.wi-1]
          self.pos = [0,0,0,0,0,0]
        elif self.pad_active=="O":
          self.pis = [0,0,0,0,0,0]
          self.pos = [0,0,0,0,self.c.he-1,self.c.wi-1]
        self.valid = 0

    def switch_to_input(self):
        if self.pad_active=="O":
            self.pad_active="I"
            self.layout_reset()
            self.valid=0
            #self.current_cell.update_json()

    def switch_to_output(self):
        if self.pad_active=="I":
            self.pad_active="O"
            self.layout_reset()
            self.valid=0
            #self.current_cell.update_json()

    def fullscreen_scroll_up(self):
        if self.is_fullscreen()==1:
          if self.yscr-self.c.he-1 > 0:
            self.yscr-=self.c.he-1
          else: 
            self.yscr=0
          if self.pad_active=="I":
            self.pis = [self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
            self.valid = 0
          elif self.pad_active=="O":
            self.pos = [0+self.yscr,0,0,0,self.c.he-1,self.c.wi-1]
            self.pos = [self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
            self.valid = 0

    def fullscreen_scroll_down(self):
        if self.is_fullscreen()==1:
          if self.pad_active=="I":
            xih = len(self.current_cell.input_buffer.split('\n'))
            if self.yscr+self.c.he-1 < xih:
              self.yscr+=self.c.he-1
              self.pis = [self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
              self.valid = 0
          elif self.pad_active=="O":
            xoh=self.current_cell.output_height
            if self.yscr+self.c.he-1 <= self.lno:
              self.yscr+=self.c.he-1
              self.pos = [self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
              self.clear_pads(False)
              self.c.scr.refresh()
              self.valid = 0

    def fullscreen_scroll_left(self,shift=1):
        if self.is_fullscreen()==1:
          if self.pad_active=="O":
            if self.lscr > 0:
              self.lscr-=shift
              self.pos=[self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
              self.valid=0
          elif self.pad_active=="I":
            if self.lscr-shift > 0:
              self.lscr-=shift
              self.pis=[self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
              self.valid=0

    def fullscreen_scroll_right(self,shift=1):
        if self.is_fullscreen()==1:
          if self.pad_active=="O":
            if self.current_cell.output_width - self.lscr > self.c.wi-1:
              self.lscr+=shift
              self.pos=[self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
              self.valid=0
          if self.pad_active=="I":
            #log(f"[i] {self.current_cell.input_width}")
            if self.current_cell.input_width - self.lscr > self.c.wi-1:
              self.lscr+=shift
              self.pis = [self.yscr,self.lscr,0,0,self.c.he-1,self.c.wi-1]
              self.valid = 0 

    def run_as_external_program(self):
        fname = self.current_cell.run_in_console()
        self.tmp_run_ext(fname)
        self.k=self.c.scr.getch()
        self.valid = 0

    def keys_sequence_gg(self):
        if self.gmod==2:
          self.gmod=0
          self.goto_first_cell()
          self.layout_reset() 
          self.valid=0

    def insert_cell_above(self):
        self.insert_cell(below=False)
        self.layout_reset()
        self.valid=0

    def insert_cell_below(self):
        self.insert_cell(below=True)
        self.layout_reset()
        self.valid=0

    def copy_current_cell(self):
        self.copy_cell()
        self.layout_reset()
        self.valid=0

    async def run_all_cells(self):
        try:
          self.focus(0)
          for i in range(0, len(self.cells)):
              cell_type = self.current_cell.json["cell_type"] 
              if self.kernel_status == "idle": 
                #if cell_type != "markdown":
                #  #await self.queue_run_cell()
                self.focus(i)
                self.switch_to_output()
                self.switch_current_pad_fullscreen()
                await self.current_cell.run()
                #self.layout_reset() 
                self.update_layout()
                self.valid=0
                await sleep(4.0)
        except Exception as e:
          log("[!] notebook.run_all_cells exception: "+str(e))

    async def _get_input(self):
        # variables
        k=32
        exe_time=0
        cell_run=None
        # initial layout creationg
        self.create_layout()
        # initial layout update
        self.update_layout()
        #bar_update=ensure_future(self.bottom_bar_update())
        # getch refersh interval
        #self.c.scr.timeout(REFRESH_INTERVAL)
        self.keymap = Keymap()
        self.keymapstack = KeymapStack()
        #KS 1 - display help 
        self.keymap.bind("1", self.display_help, ())
        #KS enter, ctrl+e - run current cell
        self.keymap.bind([5,13,'\n', curses.KEY_ENTER], self.run_current_cell, ())
        #KS t - run as external program (e.g. curses)
        self.keymap.bind("t", self.run_as_external_program, ())
        #KS u, page up - scroll fullscreen page up
        self.keymap.bind(["u",curses.KEY_PPAGE], self.fullscreen_scroll_up, ())
        #KS n, page down - scroll fulscreen page down 
        self.keymap.bind(["n",curses.KEY_NPAGE], self.fullscreen_scroll_down, ())
        #KS h, left - scroll fullscreen left more
        self.keymap.bind(["H",curses.KEY_LEFT], self.fullscreen_scroll_left, (self.c.wi-1,))
        #KS l, right - scroll fullscreen right more
        self.keymap.bind(["L",curses.KEY_RIGHT], self.fullscreen_scroll_right, (self.c.wi-1,))
        #KS h, left - scroll fullscreen left
        self.keymap.bind(["h",curses.KEY_LEFT], self.fullscreen_scroll_left, ())
        #KS m - toggle markdown cell
        self.keymap.bind(["m"], self.toggle_markdown_cell, ())
        #KS l, right - scroll fullscreen right
        self.keymap.bind(["l",curses.KEY_RIGHT], self.fullscreen_scroll_right, ())
        #KS i - switch to input
        self.keymap.bind("i", self.switch_to_input, ())
        #KS o - switch to output
        self.keymap.bind("o", self.switch_to_output, ())
        #KS w - toggle wrap output 
        self.keymap.bind("w", self.toggle_output_wrap, ())
        #KS f - switch current pad full-screen
        self.keymap.bind("f", self.switch_current_pad_fullscreen, ())
        #KS r - reset layout
        self.keymap.bind("r", self.reset_layout, ())
        #KS gg - go to first cell
        self.keymap.bind([7,"g"], self.keys_sequence_gg, ())
        #KS shift+g (G) - go to last cell
        self.keymap.bind([7,"G"], self.goto_last_cell, ())
        #KS k, up - previous cell
        self.keymap.bind(["k",curses.KEY_UP], self.goto_previous_cell, ())
        #KS j, down - next cell
        self.keymap.bind(["j",curses.KEY_DOWN], self.goto_next_cell, ())
        #KS a - insert cell above current cell
        self.keymap.bind("a", self.insert_cell_above, ())
        #KS a - insert cell below current cell
        self.keymap.bind("b", self.insert_cell_below, ())
        #KS x - cut cell
        self.keymap.bind("x", self.cut_current_cell, ())
        #KS c - copy the cell
        self.keymap.bind("c", self.copy_current_cell, ())
        #KS ctrl+v - paste cell above
        self.keymap.bind([22], self.paste_cell, (None,False))
        #KS ctrl+v - paste cell below
        self.keymap.bind("v", self.paste_cell, (None,True))
        #KS s, ctrl+s - save notebook
        self.keymap.bind("s", self.save_notebook, ())
        #KS e - edit input cell [1]
        self.keymap.bind("e", self.edit_current_cell, ())
        #KS ctrl+p - run all cells one by one
        self.keymap.bind("p", self.run_all_cells, ())
        #KS q - quit
        self.keymap.bind("q", self.exit, ())
        #
        self.c.scr.timeout(REFRESH_INTERVAL)
        self.keymapstack.push(self.keymap)
        loop_cnt=0
        while True:
          self.c.get_term_size()
          k = self.c.scr.getch()
          if k > 0 and self.valid == 0:
            log("[i] notebook._get_input "+chr(k))
            self.valid = 0
          if self.kernel_status != "idle":
            if loop_cnt%10==0 and loop_cnt > 0:
              self.kernel_exe_tm+=1
              self.status_line_valid = 0
            loop_cnt+=1
          if self.valid == 0 or self.status_line_valid == 0:
            self.status_line_valid == 0
            self.update_layout()
          # double g
          if self.gmod==0 and k==ord("g") and k!=-1:
            self.gmod=1
          elif self.gmod==1 and k==ord("g") and k!=-1:
            self.gmod=2
          elif k>0:
            self.gmod=0
          self.keymapstack.process(k)
          if self.quitting:
            self.c.end_curses()
            exit(0)
          await sleep(0.05)

    async def init(self):
        await self._run_kernel()
        #get_event_loop().run_until_complete(self._run_kernel())
        if self.mode != "batch":
          await self._get_input()

    def update_layout(self):
        try:
          # CLEAR AND PRINT PADS
          if self.valid == 0:
            self.clear_pads()
            self.status_line_valid = 0
            self.print_cell_input()
            self.print_cell_output()
            self.print_cell_execution_count()
            if sum(self.pis)!=0:
              self.refresh_input()
            if sum(self.pos)!=0:
              self.refresh_output()
            self.valid = 1
          if self.status_line_valid == 0:
            self.print_bottom_bar()
            self.refresh_status_line()
            self.status_line_valid = 1
          self.c.scr.refresh()
        except Exception as e:
          self.clear_pads()
          log("[!] update_layout exception "+str(e))
          self.c.scr.getch()
          pass

    def create_layout(self):
        try:
          inout_cells = list(
              chain.from_iterable(
                  [
                      (
                          [cell.input_prefix, cell.input],
                          [cell.output_prefix, ONE_COL, cell.output, ONE_COL],
                      )
                      for cell in self.cells[
                          self.top_cell_idx : self.bottom_cell_idx + 1  # noqa
                      ]
                  ]
              )
          )
        except Exception as e:
          self.clear_pads()
          log("-- CREATE LAYOUR PROBLEM: "+str(e))
          self.c.scr.getch()

    # HERE BOTTOM BAR TEXT
    def get_bottom_bar_text(self,exe_state="idle"):
        text = "[ ]"
        if self.dirty:
          text = "[+]"
        # ACTIVE INPUT OR OUTPUT
        text += f"[{self.pad_active}]"

        #self.kernel_status = "idle"
        #if exe_state == "exec":
        #  self.kernel_status = exe_state          
        #else:
        if self.kd and not self.no_kernel and self.kernel_name:
          if exe_state != "idle":
            self.kernel_status = exe_state
          else:
            if self.executing_cells:
              self.kernel_status = "busy"
            else:
              self.kernel_status = "idle"
        else:
          self.kernel_name = "no kernel"
          self.kernel_status = "none"
        text += f"[{self.kernel_name}][{self.kernel_status}]"
        #text += "[{:>02d}:{:>02d}:{:>02d}.{:1d}]".format(
        #  #int(int(self.kernel_exe_tm%10)/360),
        #  #int(int(self.kernel_exe_tm%10)/60),
        #  #int(int(self.kernel_exe_tm%10)/10),
        #  #self.kernel_exe_tm%10
        #)
        text += "[{:>02d}:{:>02d}:{:>02d}]".format(
          int(self.kernel_exe_tm/360),
          int(self.kernel_exe_tm/60),
          self.kernel_exe_tm%60
        )
        
        #text += " " + self.editor_msg
        text += f"[{self.current_cell_idx+1}/{len(self.cells)}]"
        return(text)

    def focus(self, idx: int):
        if idx >= 0 and idx < len(self.cells):
          ##if self.app:
          ##    if self.update_visible_cells(idx, no_change) or update_layout:
          #self.app.layout.focus(self.cells[idx].input_window)
          #self.c.scr.clear()
          #self.c.scr.refresh()
          self.current_cell_idx = idx
          #if update_layout:
          #  self.update_layout()
          #self.c.scr.refresh()

    def update_visible_cells(self, idx: int, no_change: bool) -> bool:
        #self.app = cast(Application, self.app)
        #size = self.app.renderer.output.get_size()
        available_height = size.rows - 2  # status bars
        if idx < self.top_cell_idx or self.bottom_cell_idx == -1:
            # scroll up
            (
                self.top_cell_idx,
                self.bottom_cell_idx,
            ) = self.get_visible_cell_idx_from_top(idx, available_height)
            return True
        if idx > self.bottom_cell_idx:
            # scroll down
            (
                self.top_cell_idx,
                self.bottom_cell_idx,
            ) = self.get_visible_cell_idx_from_bottom(idx, available_height)
            return True
        if no_change:
            return False
        # there might be less or more cells, or the cells' content may have changed
        top_cell_idx_keep, bottom_cell_idx_keep = (
            self.top_cell_idx,
            self.bottom_cell_idx,
        )
        while True:
            (
                self.top_cell_idx,
                self.bottom_cell_idx,
            ) = self.get_visible_cell_idx_from_top(self.top_cell_idx, available_height)
            if self.top_cell_idx <= idx <= self.bottom_cell_idx:
                break
            self.top_cell_idx += 1
        return not (
            self.top_cell_idx == top_cell_idx_keep
            and self.bottom_cell_idx == bottom_cell_idx_keep
        )

    def get_visible_cell_idx_from_top(
        self, idx: int, available_height: int
    ) -> Tuple[int, int]:
        cell_nb = -1
        #for cell in self.cells[idx:]:
        #    available_height -= cell.get_height()
        #    available_height -= cell.get_height()
        #    cell_nb += 1
        #    if available_height <= 0:
        #        break
        # bottom cell may be clipped by ScrollablePane
        # top_cell_id, bottom_cell_idx
        return idx, idx + cell_nb

    def get_visible_cell_idx_from_bottom(
        self, idx: int, available_height: int
    ) -> Tuple[int, int]:
        cell_nb = -1
        # for cell in self.cells[idx::-1]:
        #for cell in self.cells[idx:]:
        #    available_height -= cell.get_height()
        #    cell_nb += 1
        #    if available_height <= 0:
        #        break
        # top cell may be clipped by ScrollablePane
        # return idx - cell_nb, idx
        # changed in v0.1.2 orig:
        # top_cell_id, bottom_cell_idx
        return idx, idx + cell_nb

    def exit_cell(self):
        self.edit_mode = False
        self.current_cell.update_json()
        self.current_cell.set_input_readonly()

    def edit_in_editor(self):
        self.edit_mode = True
        self.current_cell.open_in_editor()

    def run_in_console(self):
        self.edit_mode = True
        self.current_cell.run_in_console()
        idx = self.current_cell_idx
        #self.focus(idx, update_layout=True)
        self.focus(idx)

    def edit_result_in_editor(self):
        self.edit_mode = True
        self.current_cell.open_result_in_editor()

    def enter_cell(self):
        self.edit_mode = True
        #self.current_cell.set_input_editable()

    def move_up(self):
        idx = self.current_cell_idx
        if idx > 0:
            self.dirty = True
            self.cells[idx - 1], self.cells[idx] = self.cells[idx], self.cells[idx - 1]
            #self.focus(idx - 1, update_layout=True)
            self.focus(idx - 1)

    def move_down(self):
        idx = self.current_cell_idx
        if idx < len(self.cells) - 1:
            self.dirty = True
            self.cells[idx], self.cells[idx + 1] = self.cells[idx + 1], self.cells[idx]
            #self.focus(idx + 1, update_layout=True)
            self.focus(idx + 1)

    def clear_all_output(self):
        for i in range(0, len(self.cells)):
          self.focus(i)
          self.current_cell.clear_output()
        self.focus(0)

    def clear_output(self):
        self.current_cell.clear_output()

    def toggle_markdown_cell(self):
        text=""
        if self.current_cell.json["cell_type"]=="code":
          self.markdown_cell()
          self.switch_to_input()
        elif self.current_cell.json["cell_type"]=="markdown":
          self.code_cell()
          self.switch_to_output()
        self.update_layout()

    def markdown_cell(self):
        self.current_cell.set_as_markdown()

    def code_cell(self):
        self.current_cell.set_as_code()

    async def queue_run_cell(self, and_select_below: bool = False):
        if self.kd:
            cell = self.current_cell
            if and_select_below:
                if self.current_cell_idx == len(self.cells) - 1:
                    self.insert_cell(self.current_cell_idx + 1)
                self.focus(self.current_cell_idx + 1)
            await cell.run()

    def cut_cell(self, idx: Optional[int] = None):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx
        self.copied_cell = self.cells.pop(idx)
        if not self.cells:
            self.cells = [Cell(self)]
        elif idx == len(self.cells):
            idx -= 1
        #self.focus(idx, update_layout=True)
        self.focus(idx)

    def copy_cell(self, idx: Optional[int] = None):
        if idx is None:
            idx = self.current_cell_idx
        idx = self.current_cell_idx
        self.copied_cell = self.cells[idx]

    async def paste_cell(self, idx: Optional[int] = None, below=False):
        if self.copied_cell is not None:
            self.dirty = True
            if idx is None:
                idx = self.current_cell_idx + below
            pasted_cell = self.copied_cell.copy()
            self.cells.insert(idx, pasted_cell)
            #self.focus(idx, update_layout=True)
            self.focus(idx)
            self.layout_reset()
            self.valid=0

    def insert_cell(self, idx: Optional[int] = None, below=False):
        self.dirty = True
        if idx is None:
            idx = self.current_cell_idx + below
        self.cells.insert(idx, Cell(self))
        #self.focus(idx, update_layout=True)
        self.focus(idx)

    def output_hook(self, msg: Dict[str, Any]):
        log("[*] Invoking output hoook")
        text=""
        try:
             msg_id = msg["parent_header"]["msg_id"]
             execution_count = self.msg_id_2_execution_count[msg_id]
             msg_type = msg["header"]["msg_type"]
             content = msg["content"]
             #log("[*] notebook.output_hook: msg --"+msg_id+" "+str(execution_count))
             #log("[=] notebook.output_hook content : "+str(content))
             #log("[=] content : "+str(msg))
             #log(str_state)
             if "execution_state" in content:
               exe_state=content["execution_state"]
               str_state=self.get_bottom_bar_text(exe_state)
               log("[=] notebook.output_hook ["+msg_type+"]: "+str(content["execution_state"]) + " exe state")
               return(0) 
             #if "status" in content:
             #  if content["status"]=="busy":
             #    log("[=] notebook.output_hook ["+content["status"]+"]: "+str(content["execution_state"]) + " busy exe state")
             #    return(0) 
             log("[*] notebook.output_hook ["+msg_type+"]: received msg")
             # CLEAR THE PREVIOUS OUTPUTS
             outputs = self.executing_cells[execution_count].json["outputs"]
             if msg_type == "stream":
                 #if (not outputs) or (outputs[-1]["name"] != content["name"]):
                 #outputs.append({
                 outputs = [ {
                   "name": content["name"], 
                   "output_type": msg_type, 
                   "text": content["text"]
                 } ]
                 #outputs[-1]["text"].append(content["text"])
                 #outputs[-1]["text"]=content["text"]
             elif msg_type in ("display_data", "execute_result"):
                 data_type = "text/plain"
                 res_out = "NO OUTPUT"
                 if "text/plain" in content["data"]:
                   res_out = content["data"].get("text/plain", "")
                   data_type = "text/plain"
                 elif "text/html" in content["data"]:
                   res_out = content["data"].get("text/html", "")
                   data_type = "text/html"
                 #if len(outputs) > 0:
                 #log("[?] notebook.output_hook: "+str(outputs[-1]["data"])+" "+str(content["data"]))
                 #if outputs[-1]["data"][data_type][0][:-1] == res_out:
                 #   return 
                 try:
                   #outputs.append(
                   #outputs = { "data": {
                   #data_type: [ res_out + "\n", ""],
                   #outputs.append({ "data": {
                   outputs = [ { "data": {
                       data_type: [ res_out + "\n", ""],
                     },
                     "execution_count": execution_count,
                     "metadata": {},
                     "output_type": msg_type,
                   } ]
                 except Exception as e:
                   log("[!] display data output error: " + str(e))
             #self.c.scr.addstr(3,0,f"Out:")
             #self.c.scr.addstr(4,0, "----")
             #self.c.scr.addstr(5,0,"{:>4d}".format(execution_count))
             # text = rich_print(f"Out[{execution_count}]:", 
             #   style="red", end=""
             # )
             ## HERE 20220803
             #    self.executing_cells[
             #        execution_count
             #    ].output_prefix.content = 
             # FormattedTextControl(text=ANSI(text))
             elif msg_type == "error":
                 #outputs.append(
                 outputs = [ {
                   "ename": content["ename"],
                   "evalue": content["evalue"],
                   "output_type": "error",
                   "traceback": content["traceback"],
                 } ]
             else:
                 return
             # self.executing_cells[execution_count].output.content 
             # = FormattedTextControl(
             #    text=text
             # )
             log("[*] notebook.output_hook [received kernel output]")
             #self.current_cell.json["outputs"]=outputs
             self.executing_cells[execution_count].json["outputs"]=outputs
             # self.c.pads[POU].clear()
             # text, height = self.current_cell.get_output_text(outputs)
             # self.print_cell_output()
             # self.print_cell_execution_count(execution_count)
             # self.focus(self.current_cell_idx, update_layout=True)
             # shift=0
             # linelen=0
             # ecs=len(str(execution_count)) # execution count shift
             # #log(str(ecs))
             #for lin in text.split('\n'):
             #  self.c.scr.move(3+shift,self.left_margin+ecs+1)
             #  self.c.scr.addstr(lin)
             #  shift+=1
             #self.c.scr.refresh()
             #height_keep = self.executing_cells[execution_count].output.height
             #self.executing_cells[execution_count].output.height = height
             #if self.app and height_keep != height:
             # height has changed
             #if height_keep != height:
             #self.current_cell.output = outputs
             #log("[.] notebook.output_hook: "+str(self.current_cell.json)) 
             log("[d] cell.output_hook: "+str(len(self.executing_cells))+" "+str(execution_count))
             self.valid = 0
        except Exception as e:
             log("[!] notebook:output_hook OUTPUT HOOK ERROR: "+ str(e))

    async def exit(self):
      # Causes whole term to hang. Better autosave than hang
      #if self.dirty and not self.quitting:
      #    self.quitting = True
      #    return
      try:
        if self.kd:
          if hasattr(self.kd, "kernel_process"):
            log("[!] notebook.exit: stopping kernel process")
            await self.kd.stop()
      except Exception as e:
        print("Kernel stop error." + str(e))
        log("Kernel stop error." + str(e))
      log("[x] conjuno exit ...")
      #print("[x] conjuno exit ...")
      self.quitting=True 
      self.c.end_curses()
      #exit(0)

    def go_up(self):
        #self.focus(self.current_cell_idx - 1, no_change=True)
        #self.focus(self.current_cell_idx-1, no_change=False)
        self.focus(self.current_cell_idx-1)

    def go_down(self):
        #self.focus(self.current_cell_idx + 1, no_change=True)
        self.focus(self.current_cell_idx+1)

    def nb_search(self):
        self.search_buffer.open_in_editor()
        search_str = self.search_buffer.text
        idx = self.current_cell_idx + 1
        for i in range(idx, len(self.cells)):
            txt = self.cells[i].input_buffer
            if search_str in txt:
                # print("FOUND: "+str(txt))
                self.focus(i)
                break

    def nb_repeat_search(self):
        search_str = self.search_buffer.text
        if search_str:
            idx = self.current_cell_idx + 1
            for i in range(idx, len(self.cells)):
                txt = self.cells[i].input_buffer
                if search_str in txt:
                    # print("FOUND: "+str(txt))
                    self.focus(i)
                    break

    def nb_search_backwards(self):
        search_str = self.search_buffer.text
        if search_str:
            idx = self.current_cell_idx - 1
            for i in range(idx, 0, -1):
                txt = self.cells[i].input_buffer
                if search_str in txt:
                    # print("FOUND: "+str(txt))
                    self.focus(i)
                    break

    def nb_set_mark(self, mark_no):
        idx = self.current_cell_idx
        self.marks[mark_no] = idx
        self.editor_msg = "Mark '" + str(chr(mark_no)) + "' set to cell " + str(idx)

    def nb_goto_mark(self, mark_no):
        idx = self.marks[mark_no]
        self.focus(idx)
        self.editor_msg = "Goto Mark '" + str(chr(mark_no)) + "' @ cell " + str(idx)

