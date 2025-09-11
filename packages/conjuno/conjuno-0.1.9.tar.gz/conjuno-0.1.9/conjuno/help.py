#
# PROGRAM: CONJUNO
# VERSION: 08/2022
# MODULE : help
#

help_txt = r"""```
------------------------------------------

       CONSOLE JUPYTER NOTEBOOK

------------------------------------------
   _______ _______ ______ 
  |   _   |   _   |   _  \
  |.  1___|.  |   |.  |   |
  |.  |___|.  |   |.  |   |
  |:  1   |:  1   |:  |   |
  |::.. . |::.. . |::.|   | SOLE
  `-------`-------`--- --- `
   _______ ___ ___ ______  _______
  |   _   |   Y   |   _  \|   _   |
  |___|   |.  |   |.  |   |.  |   |
  |.  |   |.  |   |.  |   |.  |   |
  |:  1   |:  1   |:  |   |:  1   |
  |::.. . |::.. . |::.|   |::.. . |
  `-------`-------`--- ---`-------'
      PYTER           TEBOOK

  CONJUNO 0.0.2

------------------------------------------
  
  Usage while in the conjuno :
  
  e     - open input cell in vim [1]
  enter - runs current cell
  q     - quits the program
  j     - go to next cell
  k     - go to previous cell
  a     - append cell before current cell
  x     - cuts the current cell
  s     - saves the notebook

------------------------------------------

  Command line parameters:

  -d, --debug
    turns on kernel debug messages

  -k kernel_type, --kernel kernel_type
    runs conjuno with specified kernel

  -n, --no-kernel
    runs conjuno with no kernel

  -v, --version
    displays the current program version 

------------------------------------------

  [1] uses tmp.txt in current directory

------------------------------------------

  Note: This is de facto modified nbterm.
        The difference is it uses only
        ncurses.

------------------------------------------

  This is highly EXPERIMENTAL software.
  I take no responsibility nor even implied 
  responsibility for any damage, harm or any 
  consequences caused by use of this 
  software. The software found here is
  provided as it is without any liability, 
  guarantees or support.

  The software here is provided ONLY 
  for research purposes.

------------------------------------------
"""


class Help:

    help_mode: bool
    help_text: str
    help_window: None
    help_line: int

    def show_help(self):
        self.help_mode = True
        #self.help_text = rich_print(md)
        #self.help_window = Window(
        #    content=FormattedTextControl(text=ANSI(self.help_text))
        #)
        #self.app.layout = Layout(self.help_window)
        self.help_line = 0

    def scroll_help_up(self):
        if self.help_line > 0:
            self.help_line -= 1
            text = "\n".join(self.help_text.split("\n")[self.help_line :])  # noqa
            #self.help_window.content = FormattedTextControl(text=ANSI(text))

    def scroll_help_down(self):
        if self.help_line < self.help_text.count("\n"):
            self.help_line += 1
            text = "\n".join(self.help_text.split("\n")[self.help_line :])  # noqa
            #self.help_window.content = FormattedTextControl(text=ANSI(text))

    def quit_help(self):
        self.help_mode = False
        self.update_layout()
        #self.help_text = rich_print(md, self.console)
        #self.help_window = Window(
        #    content=FormattedTextControl(text=ANSI(self.help_text))
        #)
