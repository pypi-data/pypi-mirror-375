from typing import Any, Optional, List, Dict, Tuple, Callable, Union

r"""High level functions that deal with the generation of the disassembled text lines.

This file also contains definitions for the syntax highlighting.
Finally there are functions that deal with anterior/posterior user-defined lines. 
    
"""

class user_defined_prefix_t:
    def __delattr__(self, name: Any) -> Any:
        r"""Implement delattr(self, name)."""
        ...
    def __dir__(self) -> Any:
        r"""Default dir() implementation."""
        ...
    def __disown__(self) -> Any:
        ...
    def __eq__(self, value: Any) -> Any:
        r"""Return self==value."""
        ...
    def __format__(self, format_spec: Any) -> Any:
        r"""Default object formatter.
        
        Return str(self) if format_spec is empty. Raise TypeError otherwise.
        """
        ...
    def __ge__(self, value: Any) -> Any:
        r"""Return self>=value."""
        ...
    def __getattribute__(self, name: Any) -> Any:
        r"""Return getattr(self, name)."""
        ...
    def __getstate__(self) -> Any:
        r"""Helper for pickle."""
        ...
    def __gt__(self, value: Any) -> Any:
        r"""Return self>value."""
        ...
    def __hash__(self) -> Any:
        r"""Return hash(self)."""
        ...
    def __init__(self, args: Any) -> Any:
        ...
    def __init_subclass__(self) -> Any:
        r"""This method is called when a class is subclassed.
        
        The default implementation does nothing. It may be
        overridden to extend subclasses.
        
        """
        ...
    def __le__(self, value: Any) -> Any:
        r"""Return self<=value."""
        ...
    def __lt__(self, value: Any) -> Any:
        r"""Return self<value."""
        ...
    def __ne__(self, value: Any) -> Any:
        r"""Return self!=value."""
        ...
    def __new__(self, args: Any, kwargs: Any) -> Any:
        r"""Create and return a new object.  See help(type) for accurate signature."""
        ...
    def __reduce__(self) -> Any:
        r"""Helper for pickle."""
        ...
    def __reduce_ex__(self, protocol: Any) -> Any:
        r"""Helper for pickle."""
        ...
    def __repr__(self) -> Any:
        ...
    def __setattr__(self, name: Any, value: Any) -> Any:
        r"""Implement setattr(self, name, value)."""
        ...
    def __sizeof__(self) -> Any:
        r"""Size of object in memory, in bytes."""
        ...
    def __str__(self) -> Any:
        r"""Return str(self)."""
        ...
    def __subclasshook__(self, object: Any) -> Any:
        r"""Abstract classes can override this to customize issubclass().
        
        This is invoked early on by abc.ABCMeta.__subclasscheck__().
        It should return True, False or NotImplemented.  If it returns
        NotImplemented, the normal algorithm is used.  Otherwise, it
        overrides the normal algorithm (and the outcome is cached).
        
        """
        ...
    def __swig_destroy__(self, object: Any) -> Any:
        ...
    def get_user_defined_prefix(self, ea: ida_idaapi.ea_t, insn: insn_t, lnnum: int, indent: int, line: str) -> None:
        r"""This callback must be overridden by the derived class. 
                
        :param ea: the current address
        :param insn: the current instruction. if the current item is not an instruction, then insn.itype is zero.
        :param lnnum: number of the current line (each address may have several listing lines for it). 0 means the very first line for the current address.
        :param indent: see explanations for gen_printf()
        :param line: the line to be generated. the line usually contains color tags. this argument can be examined to decide whether to generate the prefix.
        """
        ...

def COLSTR(str: Any, tag: Any) -> Any:
    r"""
    Utility function to create a colored line
    :param str: The string
    :param tag: Color tag constant. One of SCOLOR_XXXX
    
    """
    ...

def add_extra_cmt(args: Any) -> bool:
    ...

def add_extra_line(args: Any) -> bool:
    ...

def add_pgm_cmt(args: Any) -> bool:
    ...

def add_sourcefile(ea1: ida_idaapi.ea_t, ea2: ida_idaapi.ea_t, filename: str) -> bool:
    ...

def calc_bg_color(ea: ida_idaapi.ea_t) -> bgcolor_t:
    r"""Get background color for line at 'ea' 
            
    :returns: RGB color
    """
    ...

def calc_prefix_color(ea: ida_idaapi.ea_t) -> color_t:
    r"""Get prefix color for line at 'ea' 
            
    :returns: Line prefix colors
    """
    ...

def create_encoding_helper(args: Any) -> encoder_t:
    ...

def del_extra_cmt(ea: ida_idaapi.ea_t, what: int) -> bool:
    ...

def del_sourcefile(ea: ida_idaapi.ea_t) -> bool:
    ...

def delete_extra_cmts(ea: ida_idaapi.ea_t, what: int) -> None:
    ...

def generate_disasm_line(ea: ida_idaapi.ea_t, flags: int = 0) -> str:
    ...

def generate_disassembly(ea: Any, max_lines: Any, as_stack: Any, notag: Any, include_hidden: Boolean = False) -> Any:
    r"""Generate disassembly lines (many lines) and put them into a buffer
    
    :param ea: address to generate disassembly for
    :param max_lines: how many lines max to generate
    :param as_stack: Display undefined items as 2/4/8 bytes
    :param notag: remove color tags
    :param include_hidden: automatically unhide hidden objects
    :returns: tuple(most_important_line_number, list(lines)) : Returns a tuple containing
              the most important line number and a list of generated lines
    :returns: None on failure
    """
    ...

def get_extra_cmt(ea: ida_idaapi.ea_t, what: int) -> int:
    ...

def get_first_free_extra_cmtidx(ea: ida_idaapi.ea_t, start: int) -> int:
    ...

def get_sourcefile(ea: ida_idaapi.ea_t, bounds: range_t = None) -> str:
    ...

def install_user_defined_prefix(args: Any) -> bool:
    ...

def requires_color_esc(c: Any) -> Any:
    r"""Is the given char a color escape character?
    
    """
    ...

def tag_addr(ea: ida_idaapi.ea_t) -> str:
    r"""Insert an address mark into a string. 
            
    :param ea: address to include
    """
    ...

def tag_advance(line: str, cnt: int) -> int:
    r"""Move pointer to a 'line' to 'cnt' positions right. Take into account escape sequences. 
            
    :param line: pointer to string
    :param cnt: number of positions to move right
    :returns: moved pointer
    """
    ...

def tag_remove(nonnul_instr: str) -> str:
    r"""Remove color escape sequences from a string. 
            
    :returns: length of resulting string, -1 if error
    """
    ...

def tag_skipcode(line: str) -> int:
    r"""Skip one color code. This function should be used if you are interested in color codes and want to analyze all of them. Otherwise tag_skipcodes() function is better since it will skip all colors at once. This function will skip the current color code if there is one. If the current symbol is not a color code, it will return the input. 
            
    :returns: moved pointer
    """
    ...

def tag_skipcodes(line: str) -> int:
    r"""Move the pointer past all color codes. 
            
    :param line: can't be nullptr
    :returns: moved pointer, can't be nullptr
    """
    ...

def tag_strlen(line: str) -> ssize_t:
    r"""Calculate length of a colored string This function computes the length in unicode codepoints of a line 
            
    :returns: the number of codepoints in the line, or -1 on error
    """
    ...

def update_extra_cmt(ea: ida_idaapi.ea_t, what: int, str: str) -> bool:
    ...

COLOR_ADDR: int  # 40
COLOR_ADDR_SIZE: int  # 16
COLOR_ALTOP: int  # 22
COLOR_ASMDIR: int  # 27
COLOR_AUTOCMT: int  # 4
COLOR_BG_MAX: int  # 13
COLOR_BINPREF: int  # 20
COLOR_CHAR: int  # 10
COLOR_CNAME: int  # 37
COLOR_CODE: int  # 5
COLOR_CODNAME: int  # 26
COLOR_COLLAPSED: int  # 39
COLOR_CREF: int  # 14
COLOR_CREFTAIL: int  # 16
COLOR_CURITEM: int  # 9
COLOR_CURLINE: int  # 10
COLOR_DATA: int  # 6
COLOR_DATNAME: int  # 6
COLOR_DCHAR: int  # 30
COLOR_DEFAULT: int  # 1
COLOR_DEMNAME: int  # 8
COLOR_DNAME: int  # 7
COLOR_DNUM: int  # 31
COLOR_DREF: int  # 15
COLOR_DREFTAIL: int  # 17
COLOR_DSTR: int  # 29
COLOR_ERROR: int  # 18
COLOR_ESC: str  # 
COLOR_EXTERN: int  # 8
COLOR_EXTRA: int  # 21
COLOR_FG_MAX: int  # 40
COLOR_HIDLINE: int  # 11
COLOR_HIDNAME: int  # 23
COLOR_IMPNAME: int  # 34
COLOR_INSN: int  # 5
COLOR_INV: str  # 
COLOR_KEYWORD: int  # 32
COLOR_LIBFUNC: int  # 3
COLOR_LIBNAME: int  # 24
COLOR_LOCNAME: int  # 25
COLOR_LUMFUNC: int  # 12
COLOR_LUMINA: int  # 52
COLOR_MACRO: int  # 28
COLOR_NUMBER: int  # 12
COLOR_OFF: str  # 
COLOR_ON: str  # 
COLOR_OPND1: int  # 41
COLOR_OPND2: int  # 42
COLOR_OPND3: int  # 43
COLOR_OPND4: int  # 44
COLOR_OPND5: int  # 45
COLOR_OPND6: int  # 46
COLOR_OPND7: int  # 47
COLOR_OPND8: int  # 48
COLOR_PREFIX: int  # 19
COLOR_REG: int  # 33
COLOR_REGCMT: int  # 2
COLOR_REGFUNC: int  # 4
COLOR_RESERVED1: int  # 51
COLOR_RPTCMT: int  # 3
COLOR_SEGNAME: int  # 35
COLOR_SELECTED: int  # 2
COLOR_STRING: int  # 11
COLOR_SYMBOL: int  # 9
COLOR_UNAME: int  # 38
COLOR_UNKNAME: int  # 36
COLOR_UNKNOWN: int  # 7
COLOR_VOIDOP: int  # 13
E_NEXT: int  # 2000
E_PREV: int  # 1000
GDISMF_ADDR_TAG: int  # 2
GDISMF_AS_STACK: int  # 1
GDISMF_REMOVE_TAGS: int  # 4
GDISMF_UNHIDE: int  # 8
GENDSM_FORCE_CODE: int  # 1
GENDSM_MULTI_LINE: int  # 2
GENDSM_REMOVE_TAGS: int  # 4
GENDSM_UNHIDE: int  # 8
PALETTE_SIZE: int  # 53
SCOLOR_ADDR: str  # (
SCOLOR_ALTOP: str  # 
SCOLOR_ASMDIR: str  # 
SCOLOR_AUTOCMT: str  # 
SCOLOR_BINPREF: str  # 
SCOLOR_CHAR: str  # 

SCOLOR_CNAME: str  # %
SCOLOR_CODNAME: str  # 
SCOLOR_COLLAPSED: str  # '
SCOLOR_CREF: str  # 
SCOLOR_CREFTAIL: str  # 
SCOLOR_DATNAME: str  # 
SCOLOR_DCHAR: str  # 
SCOLOR_DEFAULT: str  # 
SCOLOR_DEMNAME: str  # 
SCOLOR_DNAME: str  # 
SCOLOR_DNUM: str  # 
SCOLOR_DREF: str  # 
SCOLOR_DREFTAIL: str  # 
SCOLOR_DSTR: str  # 
SCOLOR_ERROR: str  # 
SCOLOR_ESC: str  # 
SCOLOR_EXTRA: str  # 
SCOLOR_FG_MAX: str  # (
SCOLOR_HIDNAME: str  # 
SCOLOR_IMPNAME: str  # "
SCOLOR_INSN: str  # 
SCOLOR_INV: str  # 
SCOLOR_KEYWORD: str  #  
SCOLOR_LIBNAME: str  # 
SCOLOR_LOCNAME: str  # 
SCOLOR_MACRO: str  # 
SCOLOR_NUMBER: str  # 
SCOLOR_OFF: str  # 
SCOLOR_ON: str  # 
SCOLOR_OPND1: str  # )
SCOLOR_OPND2: str  # *
SCOLOR_OPND3: str  # +
SCOLOR_OPND4: str  # ,
SCOLOR_OPND5: str  # -
SCOLOR_OPND6: str  # .
SCOLOR_PREFIX: str  # 
SCOLOR_REG: str  # !
SCOLOR_REGCMT: str  # 
SCOLOR_RPTCMT: str  # 
SCOLOR_SEGNAME: str  # #
SCOLOR_STRING: str  # 
SCOLOR_SYMBOL: str  # 	
SCOLOR_UNAME: str  # &
SCOLOR_UNKNAME: str  # $
SCOLOR_UTF8: str  # 2
SCOLOR_VOIDOP: str  # 
SWIG_PYTHON_LEGACY_BOOL: int  # 1
VEL_CMT: int  # 2
VEL_POST: int  # 1
annotations: _Feature  # _Feature((3, 7, 0, 'beta', 1), None, 16777216)
cvar: swigvarlink
ida_idaapi: module
weakref: module