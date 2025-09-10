from colored import fg, attr 
from itertools import cycle
from .version import __version__
from telethon.utils import parse_phone

def banner():
    banner_txt = '''\
 █████╗ ██████╗ ██╗   ██╗██╗ ██████╗ 
██╔══██╗██╔══██╗██║   ██║██║██╔═══██╗
███████║██║  ██║██║   ██║██║██║   ██║
██╔══██║██║  ██║╚██╗ ██╔╝██║██║   ██║
██║  ██║██████╔╝ ╚████╔╝ ██║╚██████╔╝
╚═╝  ╚═╝╚═════╝   ╚═══╝  ╚═╝ ╚═════╝ 
    '''
    border_color=fg(124)
    colors=cycle([129,128,127,126,125,124])
    border='{}║{}'.format(border_color,fg(0))
    
    text=''
    first_line=''
    end_line=''
    max_length=0
    for line in banner_txt.split("\n"):
        if line.strip():
            if not first_line:
                length=len(line)
                if length > max_length:
                    max_length=length
                    
            c=next(colors)
            line=f"{fg(c)}{line:<{max_length}}{fg(0)}"
            text+=f"{border} {line} {border}\n"

    first_line  ='{}╔{}╗{}\n'.format(border_color,"═"*(max_length+2),fg(0))
    end_line    ='{}╚{}╝{}\n'.format(border_color,"═"*(max_length+2),fg(0))
    logo= f"{first_line}{text}{end_line}"

    _name=f'Advio {__version__}'

    logo+="{}{}{}\n".format(border_color,"▄"*(max_length+4),fg(0))
    logo+=f"{border_color}▌{fg(14)}{_name:<{max_length-14}}{border_color}▐{fg(48)} ABBAS BACHARI {border_color}▐\n"
    logo+="{}{}{}\n".format(border_color,"▀"*(max_length+4),fg(0))

    
    logo+=f"  {attr('bold')+fg(70)}{'Support Channel':<{max_length-15}}{fg(1)}:{attr(0)+attr('bold')+fg(80)} @COIN98{attr(0)}"
    logo+="\n\n"
      
    
    print(logo)
    return logo


