from PyQt5.Qt import qApp
from PyQt5.QtCore import QObject, QDir
from PyQt5.QtWidgets import QMessageBox,QGraphicsOpacityEffect
import os
import sys
from ctypes import cdll
from transparentIDA.idafontconfig import IdaFontConfig

PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
IDA_DIR = os.path.abspath(os.path.join(PLUGIN_DIR, '..', '..'))
RESOURCES_DIR = os.path.join(PLUGIN_DIR, 'transparentIDA')

def apply_patch():
    p = cdll.LoadLibrary(os.path.join(RESOURCES_DIR, "patch_ida.dll"))
    p.patch()

def preprocess_stylesheet(qss, abs_theme_dir):
    qss = qss.replace('<IDADIR>', QDir.fromNativeSeparators(IDA_DIR))
    qss = qss.replace('<SKINDIR>', QDir.fromNativeSeparators(abs_theme_dir))

    def replace_keyword(x, keyword, kind):
        cfg = IdaFontConfig(kind)
        prefix = '<{}_FONT_'.format(keyword)

        x = x.replace(prefix + 'FAMILY>', cfg.family)
        x = x.replace(prefix + 'STYLE>', ' italic' if cfg.italic else '')
        x = x.replace(prefix + 'WEIGHT>', ' bold' if cfg.bold else '')
        x = x.replace(prefix + 'SIZE>', '{} pt'.format(cfg.size))

        return x

    qss = replace_keyword(qss, 'DISASSEMBLY', 'disas')
    qss = replace_keyword(qss, 'HEXVIEW', 'hexview')
    qss = replace_keyword(qss, 'DEBUG_REGISTERS', 'debug_regs')
    qss = replace_keyword(qss, 'TEXT_INPUT', 'text_input')
    qss = replace_keyword(qss, 'OUTPUT_WINDOW', 'output_wnd')
    return qss

def apply_stylesheet(abs_theme_dir,qss_file):
    try:
        with open(os.path.join(abs_theme_dir, qss_file)) as f:
            qss = f.read()
    except IOError as exc:
        print('Unable to load stylesheet.')
        return
    qss = preprocess_stylesheet(qss, abs_theme_dir)
    qApp.setStyleSheet(qss)
    print('Skin file successfully applied!')


def apply_text_rows():
    c = qApp.allWidgets()
    for i in c:
        if i.metaObject().className() == 'IDADockWidget':
            i.setStyleSheet('background-color:transparent;')
        elif i.metaObject().className() == 'TextArrows':
            opacityEffect = QGraphicsOpacityEffect()
            i.setGraphicsEffect(opacityEffect)
            opacityEffect.setOpacity(0.3)

apply_stylesheet(RESOURCES_DIR,'stylesheet.qss')
apply_patch()
apply_text_rows()