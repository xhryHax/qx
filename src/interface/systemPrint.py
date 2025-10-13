
from datetime import datetime
from threading import Lock


lock = Lock()
class Color:
    
    RESET            = '\033[0m'         # 重置所有属性，恢复正常显示

    BOLD             = '\033[1m'         # 粗体/高亮度显示
    DIM              = '\033[2m'         # 暗淡/低亮度显示
    ITALIC           = '\033[3m'         # 斜体显示
    UNDERLINE        = '\033[4m'         # 下划线
    BLINK_SLOW       = '\033[5m'         # 慢速闪烁效果
    INVERT           = '\033[7m'         # 反显效果（前景背景颜色互换）
    HIDDEN           = '\033[8m'         # 隐藏文字（隐形效果）
    STRIKETHROUGH    = '\033[9m'         # 删除线效果
    NO_BOLD          = '\033[21m'        # 取消粗体效果
    NO_DIM           = '\033[22m'        # 取消暗淡效果（同时取消粗体）
    NO_ITALIC        = '\033[23m'        # 取消斜体效果
    NO_UNDERLINE     = '\033[24m'        # 取消下划线效果
    NO_BLINK         = '\033[25m'        # 取消闪烁效果
    NO_INVERT        = '\033[27m'        # 取消反显效果
    NO_HIDDEN        = '\033[28m'        # 取消隐藏效果
    NO_STRIKETHROUGH = '\033[29m'        # 取消删除线效果

    BLACK            = '\033[30m'        # 黑色文字
    RED              = '\033[31m'        # 红色文字
    GREEN            = '\033[32m'        # 绿色文字
    YELLOW           = '\033[33m'        # 黄色文字
    BLUE             = '\033[34m'        # 蓝色文字
    MAGENTA          = '\033[35m'        # 洋红色/紫色文字
    CYAN             = '\033[36m'        # 青色/蓝绿色文字
    WHITE            = '\033[37m'        # 白色文字
    BRIGHT_BLACK     = '\033[90m'        # 亮黑色/灰色文字
    BRIGHT_RED       = '\033[91m'        # 亮红色文字
    BRIGHT_GREEN     = '\033[92m'        # 亮绿色文字
    BRIGHT_YELLOW    = '\033[93m'        # 亮黄色文字
    BRIGHT_BLUE      = '\033[94m'        # 亮蓝色文字
    BRIGHT_MAGENTA   = '\033[95m'        # 亮洋红色文字
    BRIGHT_CYAN      = '\033[96m'        # 亮青色文字
    BRIGHT_WHITE     = '\033[97m'        # 亮白色文字



def length(text:str) -> int:
    textLength = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff' or char == '：':
            textLength += 2
        else:
            textLength += 1
    return textLength


def systemPrintInfo(infoText:str) -> None:
    with lock:
        print(f'{Color.BRIGHT_CYAN}{datetime.now()} {Color.MAGENTA}system info -> {Color.GREEN}default: ' \
                f'{infoText}{Color.RESET}\n' \
                f'{Color.STRIKETHROUGH}{' '*(length(infoText)+52)}{Color.RESET}', flush=True)


def systemPrintWarningInfo(infoText:str, warningText:str) -> None:
    with lock:
        print(f'{Color.BRIGHT_CYAN}{datetime.now()} {Color.MAGENTA}system info -> {Color.YELLOW}warning:\n' \
                f'警告信息：{infoText} {Color.BRIGHT_YELLOW}\n' \
                f'警告细节：{warningText}{Color.RESET}\n' \
                f'{Color.STRIKETHROUGH}{' '*(length(warningText) + 10)}{Color.RESET}', flush=True)


def systemPrintErrorInfo(infoText:str, errorText:str) -> None:
    with lock:
        print(f'{Color.BRIGHT_CYAN}{datetime.now()} {Color.MAGENTA}system info -> {Color.RED} error :\n' \
                f'错误信息：{infoText} {Color.BRIGHT_RED}\n' \
                f'错误细节：{errorText}{Color.RESET}\n' \
                f'{Color.STRIKETHROUGH}{' '*(length(errorText) + 10)}{Color.RESET}', flush=True)


