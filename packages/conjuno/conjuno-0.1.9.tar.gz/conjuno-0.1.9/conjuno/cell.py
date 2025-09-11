# encoding=utf-8
#
# PROGRAM: CONJUNO
# MODULE : cell
#

from sys import path, stdout
from uuid import uuid4
from typing import Dict, List, Any, Optional, Union, cast
from copy import deepcopy

from conjuno.log import log
#from inspect import currentframe, getframeinfo, getmodulename
import traceback

def empty_cell_json():
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [],
        "outputs": [],
    }


class Cell:

    input: str #Union[Frame] 
    output: str # Window
    json: Dict[str, Any]
    input_prefix: str # Window
    output_prefix: str # Window
    input_window: str # Window
    input_buffer: str # Buffer
    output_buffer: str # Buffer
    fold: bool
    ext_edit: bool
    max_colors: str
    input_width: int
    input_height: int
    output_height: int
    output_width: int
    #c: Curses

    def __init__(
        self, notebook, cell_json: Optional[Dict[str, Any]] = None, mode="interactive"
    ):
        try:

            #self.c = Curses()
            #self.vshift = 0
            #self.hshift = 0
            self.notebook = notebook
            self.json = cell_json or empty_cell_json()
            self.input_prefix = "" # Window(width=10)
            self.output_prefix = "" # Window(width=10, height=0)
            self.fold = self.notebook.fold
            self.ext_edit = False
            self.input_buffer = "".join(self.json["source"])
            #self.input_buffer= input_text
            self.calc_input_width()
            output_text = ""
            self.output_height=0
            output_height=0
            outputs = []

            if self.json["cell_type"] == "code":
                execution_count = self.json["execution_count"] or " "
                #text = f"\nIn [{execution_count}]:" + self.fold_tag(),
                #text = f"\nIn [{execution_count}]:"
                if "outputs" in self.json:
                  if len(self.json["outputs"]) in self.json:
                    outputs = self.json["outputs"][0]
                else:
                  outputs = "[]"
                #self.c.scr.addstr(1,0, f"In [{execution_count}]:")
                #text = self.rich_print(
                #    f"\nIn [{execution_count}]:" + self.fold_tag(),
                #    style="green",
                #)
                #self.input_prefix.content = FormattedTextControl(text=text)
                #self.input_prefix.content = text
                #self.notebook.print_cell_execution_count(execution_count)
                #for output in outputs:
                #    if "execution_count" in output:
                #        text = self.rich_print(
                #            f"Out[{output['execution_count']}]:",
                #            style="red",
                #        )
                #        self.output_prefix.content = FormattedTextControl(
                #            text=text
                #        )
                #        break
            #self.input_buffer = Buffer(on_text_changed=self.input_text_changed)
            #self.input_buffer.text = input_text

            #self.set_input_readonly(mode)
            #if self.json["cell_type"] == "markdown":
            #    self.input = [ONE_ROW, [ONE_COL, self.input_window], ONE_ROW]
            #else:
            #    self.input = Frame(self.input_window, style="green")
            #self.output = Window(content=FormattedTextControl(text=output_text))
            #self.output = Window(content=output_text)
            self.input_window = "" # Window()
            if len(outputs)>0:
              output_text, output_height = self.get_output_text(outputs)
            self.output = output_text
            self.output_buffer = "" # Buffer()
            self.output_height = output_height
            #self.input_buffer = input_text
            self.calc_input_width()
            #if self.fold:
            #    self.input_window.height = 1
            #self.input_height = 1
        except Exception as e:
            log("[!] ERR cell.__init__ "+str(e))

    def calc_input_width(self):
      input_text = self.input_buffer
      xiw=0
      for line in input_text.split('\n'):
        if len(line) > xiw:
          xiw = len(line)
      self.input_width = xiw

    def calc_output_text_width(self,text) -> int:
        width=0
        for line in text.split('\n'):
          if len(line) > width:
            width = len(line)
        self.output_width=width
        return(width)

    def get_input_height(self) -> int:
        #input_height = cast(int, self.input_window.height) + 2  # include frame
        #output_height = cast(int, self.output.height)
        #xoh=self.current_cell.input_height
        return self.input_height # + output_height

    def get_output_height(self) -> int:
        #input_height = cast(int, self.input_window.height) + 2  # include frame
        #output_height = cast(int, self.output.height)
        #return input_height + output_height
        return self.output_height

    def copy(self):
        cell_json = deepcopy(self.json)
        cell = Cell(self.notebook, cell_json=cell_json)
        return cell

    def get_output_text(self,output: List[Dict[str, Any]]):
      text="NO DATA"
      #text_ansi = "NO DATA"
      try:
        text_list = []
        height = 0
        out_type = "none"
        if "data" in output:
          out_type = "execute_result"
        elif "output_type" in output:
          out_type = output["output_type"]
        else:
          return("")
        # COMMENTED ON 20220807
        #elif len(output)>0:
        #  if "output_type" in output[0]:
        #    out_type = output[0]["output_type"]
        #    output = output[0]
        #else:
        #  log("[*] cell.get_output_text")
        #log("-- CELL OUTPUT TYPE : " + str(output["output_type"]))
        log("[*] cell.get_output_text ["+out_type+"]")
        #log("[*] cell.get_output_text ["+out_type+"] output: "+str(output))
        if out_type == "stream":
          text = "".join(output["text"])
          height += text.count("\n")
          if output["name"] == "stderr":
            text = "\n".join(lines)
            ## TODO: take terminal width into account
            #lines = text.splitlines()
            #lines = [line + " " * (200 - len(line)) for line in lines]
            #text = self.rich_print(text, style="white on red", end="\n")
            #text = text
        elif out_type == "error":
            text = "\n".join(output["traceback"])
            height += text.count("\n")
        elif out_type == "display_data" or out_type == "execute_result":
            # text = "\n".join(output["data"].get("text/plain", ""))
            #log("[*] cell.get_output_text ["+out_type+"] output: "+str(output))
            if "text/plain" in output["data"]:
                text = "".join(output["data"]["text/plain"]) + "\n"
            elif "text/html" in output["data"]:
                text = "".join(output["data"]["text/html"]) + "\n"
                # from bs4 import BeautifulSoup
                # soup = BeautifulSoup(text)
                # text = soup.get_text()
            height += text.count("\n")
            #else:
            #  text = "".join(output["data"][data_type])
            #log("[*] cell.get_output_text output:" + str(output.keys())+str(output))
            # get("text/plain", ""))
            # text = "\n".join(output["data"].get("text/html", ""))
        #else:
        #  continue
        #text_ansi = ANSI("".join(text_list))
        #cuurent_frame = currentframe()
        #caller_frame = cuurent_frame.f_back
        #filename, lineno, function, code_context, index = getframeinfo(caller_frame)
        #caller_instance = caller_frame.f_locals['self']
        #log(f'caller instance: {caller_instance}')  # → obj
        #log(f'caller from class: {type(caller_instance).__name__}')  # → B
        #log(f'caller from method: {function}')  # → class_B_fun
        #log("[o] cell.get_output: o.k.: " + text_ansi)
        #text_ansi = "".join(text_list)
        #text_list.append(text)
        width=self.calc_output_text_width(text)
        self.output_height=height
        log(f"[o] cell.get_output [{width}x{height}]: [ok]")
      except Exception as e:
        log("[!] cell.get_output: "+str(e))
      return (text, height)

    def input_text_changed(self, _=None):
        log("[*] input text changed")
        self.notebook.dirty = True
        self.notebook.quitting = False
        line_nb = self.input_buffer.count("\n") + 1
        height_keep = self.input_window.height
        self.input_window.height = line_nb
        #if height_keep is not None and line_nb != height_keep:
        #    # height has changed
        #    #self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)
        #    #self.exit_cell()
        #if self.ext_edit is True:
        #    log("-- TEXT: " + self.input_buffer.text)
        #    self.ext_edit = False
        #    self.notebook.edit_mode = False
        #    self.update_json()
        #    self.set_input_readonly()
        #    self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)

    def set_as_markdown(self):
        prev_cell_type = self.json["cell_type"]
        if prev_cell_type != "markdown":
            self.notebook.dirty = True
            self.json["cell_type"] = "markdown"
            #if "outputs" in self.json:
            #    del self.json["outputs"]
            #if "execution_count" in self.json:
            #    del self.json["execution_count"]
            #self.input_prefix.content = FormattedTextControl(text="")
            #self.input_prefix.content = ""
            self.clear_output()
            self.set_input_readonly()
            #if prev_cell_type == "code":
            #    self.input = "" # [ONE_ROW, [ONE_COL, self.input_window], ONE_ROW]
            #self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)
            self.notebook.focus(self.notebook.current_cell_idx)

    def set_as_code(self):
        prev_cell_type = self.json["cell_type"]
        if prev_cell_type != "code":
            self.notebook.dirty = True
            self.json["cell_type"] = "code"
            #self.json["outputs"] = []
            #self.json["execution_count"] = None
            #self.c.scr.addstr(1,0, "In [ ]:")
            #text = self.rich_print("\nIn [ ]:" + self.fold_tag(), style="green")
            #self.input_prefix.content = FormattedTextControl(text=text)
            #self.input_prefix.content = text
            self.set_input_readonly()
            if prev_cell_type == "markdown":
                #self.input = Frame(self.input_window, style="green")
                self.input = self.input_window
                #self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)
                self.notebook.focus(self.notebook.current_cell_idx)

    def set_input_readonly(self, mode="interactive"):
        if mode == "batch":
            return
        if self.json["cell_type"] == "markdown":
            text = self.input_buffer #or "Type *Markdown*"
            #md = Markdown(text)
            #text = self.rich_print(md)[:-1]  # remove trailing "\n"
            #text = text[:-1]  # remove trailing "\n"
        elif self.json["cell_type"] == "code":
            #code = Syntax(
            #    self.input_buffer.text, self.notebook.language, theme="ansi_dark"
            #)
            #text = self.rich_print(code)[:-1]  # remove trailing "\n"
            #text = self.rich_print(self.input_buffer.text)[:-1]  # remove trailing "\n"
            text = self.input_buffer[:-1]  # remove trailing "\n"
        line_nb = text.count("\n") + 1
        #self.input_window.content = FormattedTextControl(text=text)
        #self.input_window.content = text
        #height_keep = self.input_window.height
        #self.input_window.height = line_nb
        #if (
        #    #self.notebook.app is not None
        #    and height_keep is not None
        #    and line_nb != height_keep
        #):
            # height has changed
        #self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)
        self.notebook.focus(self.notebook.current_cell_idx)
        #if self.fold:
        #    self.input_window.height = 1

    def clear_output(self):
        #if self.output.height > 0:
        self.notebook.dirty = True
        #    self.output.height = 0
        #    self.output.content = FormattedTextControl(text="")
        #    self.output_prefix.content = FormattedTextControl(text="")
        #    self.output_prefix.height = 0
        #    if self.json["cell_type"] == "code":
        #        self.json["outputs"] = []
        #    #if self.notebook.app:
        #    #    self.notebook.focus(self.notebook.current_cell_idx, update_layout=True)
        #self.c.scr.clear()
        #self.c.scr.refresh()

    def update_json(self):
        src_list = [line + "\n" for line in self.input_buffer.splitlines()]
        # Fixes exit from cell when nothing is typed neither no output with single cell
        if src_list:
            src_list[-1] = src_list[-1][:-1]
            self.json["source"] = src_list

    def call_external_process(self, fname):
        import subprocess
        try:
            subprocess.call(["python3", fname])
        except subprocess.CalledProcessError as e:
            self.output.content = e.output
            pass
        self.notebook.execution_count += 1
        self.output.content = FormattedTextControl(text="ERROR")

        return self.callback_external_process

    def callback_external_process(self):
        return None

    def run_in_console(self):
      self.clear_output()
      if self.json["cell_type"] == "code":
        code = self.input_buffer.strip()
        if code:
          if self not in self.notebook.executing_cells.values():
            self.notebook.dirty = True
            executing_text = code
            fname = "tmp_nbt_"
            # import libraries for random
            from random import randint
            from os import remove
            # generate random filename
            for i in range(1, 16):
              fname += chr(randint(97, 122))
            fname += ".py"
            f = open(fname, "w")
            f.write(executing_text)
            f.close()
            #remove(fname)
            return(fname)
            #from prompt_toolkit.application.run_in_terminal import (
            #    run_in_terminal,
            #)
            #run_in_terminal(self.call_external_process(fname), in_executor=True)

    async def run(self):
        log("[o] cell.run: executing code")
        #self.notebook.valid = 0
        #self.notebook.get_bottom_bar_text("exec")
        if self.notebook.mode != "batch":
          self.notebook.c.scr.addstr(self.notebook.c.he-1,0,self.notebook.get_bottom_bar_text("exec"))
          self.notebook.c.scr.refresh()
        try:
            #self.c.scr.clear()
            self.clear_output()
            #self.c.scr.clear()
            if self.json["cell_type"] == "code":
                code = self.input_buffer.strip()
                if code:
                    if self not in self.notebook.executing_cells.values():
                        self.notebook.dirty = True
                        #executing_text = self.rich_print(
                        #    "\nIn [*]:" + self.fold_tag(), style="green"
                        #)
                        #self.input_prefix.content = FormattedTextControl(
                        #    text=ANSI(executing_text)
                        #)
                        self.notebook.execution_count += 1
                        execution_count = self.notebook.execution_count
                        msg_id = uuid4().hex
                        self.notebook.msg_id_2_execution_count[msg_id] = execution_count
                        self.notebook.executing_cells[execution_count] = self
                        # log execution status
                        if self.notebook.kd:
                          self.notebook.kd.log = self.notebook.debug
                        # self.notebook.kd.log = True
                        # test for existence of kernel process sometimes the process
                        # won't start when using the --run parameter so let's be sure
                        # there is one
                        if self.notebook.kd:
                            if not hasattr(self.notebook.kd, "kernel_process"):
                                await self.notebook.kd.start()
                                log("[i] cell.run: starting kernel process")
                        # this is added to eliminate hangs during execution
                        try:
                            await self.notebook.kd.execute(
                                self.input_buffer, msg_id=msg_id
                            )
                        except Exception as e:
                            # print("EXCEPTION DURING EXECUTION")
                            self.notebook.kernel_status = "Exception " + str(e)
                            return
                        del self.notebook.executing_cells[execution_count]
                        #self.c.scr.addstr(1,0,f"In [{execution_count}]:")
                        #text = self.rich_print(
                        #    f"\nIn [{execution_count}]:" + self.fold_tag(),
                        #    style="green",
                        #)
                        #self.input_prefix.content = FormattedTextControl(
                        #    text=text
                        #)
                        self.json["execution_count"] = execution_count
                        #if self.notebook.app:
                        #    self.notebook.app.invalidate()
                        self.notebook.valid = 0
                else:
                    self.clear_output()
            else:
                self.clear_output()
        except Exception as e:
            print("RUN PROBLEM " + str(e))
