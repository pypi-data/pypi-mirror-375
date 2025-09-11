#
# PROGRAM: CONJUNO
# MODULE : cell
#

import curses
from conjuno.log import log

cmatu=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,199,252,233,226,228,224,229,231,234,235,232,239,238,236,196,197,201,230,198,244,246,242,251,249,255,214,220,162,163,165,8359,402,225,237,243,250,241,209,170,186,191,8976,172,189,188,161,171,187,9617,9618,9619,9474,9508,9569,9570,9558,9557,9571,9553,9559,9565,9564,9563,9488,9492,9524,9516,9500,9472,9532,9566,9567,9562,9556,9577,9574,9568,9552,9580,9575,9576,9572,9573,9561,9560,9554,9555,9579,9578,9496,9484,9608,9604,9612,9616,9600,945,223,915,960,931,963,181,964,934,920,937,948,8734,966,949,8745,8801,177,8805,8804,8992,8993,247,8776,176,8729,183,8730,8319,178,9632,160]

class Curses():

    he : int
    wi : int
    #def __init__(self):
    #    self._init_curses()
    pads: list
    term: str
    max_colors: int
    clrs: list

    def __init__(self):
        PEH = 10 # [ pad efficiency max allocatted pad size ]
        PEW = 3 # [ pad efficiency max allocatted pad size ]
        self.clrs = {}
        self.max_colors = 1
        self.init_curses()
        self.pads = []
        self.pads.append(self.new_pad(self.he*PEH,self.wi*PEW))
        self.pads.append(self.new_pad(self.he*PEH,self.wi*PEW))
        self.pads.append(self.new_pad(self.he,self.wi))

    def get_env_var(self,p_var):
        ret = ""
        try:
          ret = os.environ[p_var]
        except:
          pass
        return(ret)

    def end_curses(self):
        # turn on cursor
        curses.curs_set(1)
        # turn on new line
        curses.nl()
        # turn on keys echoing
        curses.echo()
        # end the curses
        curses.endwin()

    def init_curses(self):
        # try to get TERM evironment variable
        self.term = self.get_env_var("TERM")
        #print(str(self.term))
        # init curses
        self.scr = curses.initscr()
        # detect ctrl keys
        self.scr.keypad(1)
        # we want colors
        curses.start_color()
        # no new lines
        curses.nonl()
        # no echoing of keypresses
        curses.noecho()
        # get screen size
        self.he, self.wi = self.scr.getmaxyx()
        # hide the cursor
        #try:
        curses.curs_set(0)
        #except:
        #  pass
        if "xterm" in self.term or "screen" in self.term:
          curses.curs_set(0)
        else:
          self.scr.move(0,self.wi-1)
        #self.scr.clear()
        #self.scr.move(0,0)
        #self.scr.move(self.he-1,0)
        #self.scr.addstr("[o]")
        #self.scr.refresh()
        #self.scr.getch()

    def prn(self,y,x,pstr):
        #self.init_curses()
        #self._init_curses()
        self.scr.addstr(y,x,pstr)

    def new_pad(self,rows,cols):
      pad = curses.newpad(rows, cols) # lines, cols
      return(pad)

    def pad_prn(self,padno,y,x,pstr):
      self.pads[padno].addstr(y,x,pstr)

    def pad_refresh(self,padno,y,x,ry,rx,szy,szx):
      try:
        self.pads[padno].refresh(y,x,ry,rx,szy,szx)
      except Exception as e:
        log("[!] Problem refreshing pad: "+str(padno))


    # translate our color code to curses colors
    def curs_col(self,scol):
      if scol == "Bk":
        rc = curses.COLOR_BLACK
      elif scol == "Re":
        rc = curses.COLOR_RED
      elif scol == "Gr":
        rc = curses.COLOR_GREEN
      elif scol == "Ye":
        rc = curses.COLOR_YELLOW
      elif scol == "Ma":
        rc = curses.COLOR_MAGENTA
      elif scol == "Bl":
        rc = curses.COLOR_BLUE
      elif scol == "Cy":
        rc = curses.COLOR_CYAN
      elif scol == "Wh":
        rc = curses.COLOR_WHITE
      return(rc)


    # init curses color based on foreground, background and attribute
    def init_clr(self,fg,bg,attr):
      self.max_colors+=1
      cfg = self.curs_col(fg)
      cbg = self.curs_col(bg)
      curses.init_pair(self.max_colors, cfg, cbg)
      if attr == "hi":
        self.clrs[attr+fg+bg] = curses.color_pair(self.max_colors) | curses.A_BOLD
      elif attr == "lo":
        self.clrs[attr+fg+bg] = curses.color_pair(self.max_colors) | curses.A_DIM
      #elif attr == "hb":
      #  clrs[attr+fg+bg] = curses.color_pair(max_colors) | curses.REVERSE 
      else:
        self.clrs[attr+fg+bg] = curses.color_pair(self.max_colors)

    def get_term_size(self):
      self.he, self.wi = self.scr.getmaxyx()

    # get the two chars color code
    def get_col(self,iattr):
      mia = iattr % 10
      if   mia == 0: col = "Bk"
      elif mia == 1: col = "Re"
      elif mia == 2: col = "Gr"
      elif mia == 3: col = "Ye"
      elif mia == 4: col = "Bl"
      elif mia == 5: col = "Ma"
      elif mia == 6: col = "Cy"
      elif mia == 7: col = "Wh"
      return(col)

    def render_ans(self, pad, ans, width=80, height=25, shift_y=0):
      # display ans variables
      cx = 0
      cy = 0
      # escape sequence state
      stat = ""
      attr = ""
      inten = "me"
      fgcol = "Wh"
      bgcol = "Bk"
      curcol = "meWhBk"
      lp = 0 # last printed row
      # init base color
      if curcol not in self.clrs:
        self.init_clr(fgcol,bgcol,inten)
      # main ansi loop
      for c in ans:
        # new line move to new line
        if c == ord("\n"): # 0x0a
          cy += 1
          cx = 0
          continue
        # linefeed go to first column
        elif c == ord("\r"): # 0x0d
          cx = 0
          continue
        # set state to start of escape sequence
        elif c == 27:
          stat = "E"
          continue  
        # set state to graphical escape sequence
        if stat == "E":
          if c == ord("["):
            stat = "ES"
            continue
        # graphical escape sequence
        elif stat == "ES":
          # cursor movement escape sequence
          if c == ord("C"):
            ia = int(attr)
            cx+=ia
            attr=""
            stat=""
            continue
          # read escape character numeric attribute
          elif c >= ord("0") and c <= ord("9"):
            attr += chr(c)
            continue
          # escape character terminator
          elif c == ord(";") or c == ord("m"):
            # get integer attribute
            ia = int(attr)
            # reset color to default
            if ia == 0:
              inten = "me"
              fgcol = "Wh"
              bgcol = "Bk"
            # hight intensity attribute
            elif ia == 1:
              inten = "hi" 
            # foreground colors
            elif (ia >= 30 and ia <= 37) or (ia >= 90 and ia <= 97):
              fgcol = self.get_col(ia)
            # background colors
            elif (ia >= 40 and ia <= 47) or (ia >= 100 and ia <= 107):
              bgcol = self.get_col(ia)
            # get current color code
            curcol = inten + fgcol + bgcol
            # initialize the color if it isn't not ready
            if curcol not in self.clrs:
              self.init_clr(fgcol,bgcol,inten)
            # debug
            # pad.addstr(cy,int(cx*2)+80,str(ia),clrs[curcol])
            attr=""
            # reset escape sequence state
            if c == ord("m"):
              stat = ""
            continue
        # some ansi's assume we will handle end of line
        if cx >= width:
          cy+=1 
          cx=0
        try:
          #if out_type == "utf8":
          # ans colors output
          pad.addstr(cy,cx,chr(cmatu[c]),self.clrs[curcol])
          #pad.addstr(cy,cx,chr(cmatu[c]),curses.COLOR_WHITE)
          #else:
          #  pad.addstr(cy,cx,chr(c),clrs[curcol])
          cx+=1
        except Exception as e:
          # debug
          ocx=cx
          ocy=cy
          log("[!] console.render_ans "+str(e))
          #pad.move(0,0)
          #scr.addstr(str(e)+" "+str(cy)+" "+str(cx))
          ##scr.move(ocy,ocy)
          #pad.getch()
          pass
      #scr.move(0,0)
      #prn(str(shift_y) + " " + sys.argv[1],"hiWhBk")
      return(cy)

