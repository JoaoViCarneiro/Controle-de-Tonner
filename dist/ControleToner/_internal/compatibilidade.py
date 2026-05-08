"""
compatibilidade.py
Detecta versão do Windows e aplica correções necessárias
"""

import platform
import sys
import os
import ctypes


class WindowsCompatibilidade:
    """Gerencia compatibilidade com diferentes versões do Windows"""

    def __init__(self):
        self.versao = self.detectar_versao()
        self.nome = self.get_nome_versao()
        self.is_windows_7 = self.versao.startswith('6.1')
        self.is_windows_8 = self.versao.startswith('6.2') or self.versao.startswith('6.3')
        self.is_windows_10 = self.versao.startswith('10.0')
        self.is_windows_11 = self.versao.startswith('10.0') and self.is_windows_11_real()

    def detectar_versao(self):
        """Detecta versão real do Windows"""
        try:
            # Método mais preciso usando ctypes
            class OSVERSIONINFOEXW(ctypes.Structure):
                _fields_ = [('dwOSVersionInfoSize', ctypes.c_ulong),
                            ('dwMajorVersion', ctypes.c_ulong),
                            ('dwMinorVersion', ctypes.c_ulong),
                            ('dwBuildNumber', ctypes.c_ulong),
                            ('dwPlatformId', ctypes.c_ulong),
                            ('szCSDVersion', ctypes.c_wchar * 128),
                            ('wServicePackMajor', ctypes.c_ushort),
                            ('wServicePackMinor', ctypes.c_ushort),
                            ('wSuiteMask', ctypes.c_ushort),
                            ('wProductType', ctypes.c_byte),
                            ('wReserved', ctypes.c_byte)]

            os_version = OSVERSIONINFOEXW()
            os_version.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEXW)
            handle = ctypes.windll.kernel32.GetVersionExW(ctypes.byref(os_version))

            if handle:
                return f"{os_version.dwMajorVersion}.{os_version.dwMinorVersion}"
        except:
            pass

        # Fallback para platform
        return platform.release()

    def is_windows_11_real(self):
        """Detecta se é realmente Windows 11"""
        try:
            # Windows 11 tem build >= 22000
            build = int(platform.version().split('.')[-1])
            return build >= 22000
        except:
            return False

    def get_nome_versao(self):
        """Retorna nome amigável da versão"""
        if self.is_windows_11:
            return "Windows 11"
        elif self.is_windows_10:
            return "Windows 10"
        elif self.is_windows_8:
            return "Windows 8/8.1"
        elif self.is_windows_7:
            return "Windows 7"
        else:
            return f"Windows {self.versao}"

    def aplicar_correcoes(self):
        """Aplica correções específicas para cada versão"""
        print(f"🖥️  Detectado: {self.nome}")

        if self.is_windows_7:
            self.corrigir_windows_7()
        elif self.is_windows_8:
            self.corrigir_windows_8()
        elif self.is_windows_10:
            self.corrigir_windows_10()
        elif self.is_windows_11:
            self.corrigir_windows_11()

    def corrigir_windows_7(self):
        """Correções específicas para Windows 7"""
        print("🔧 Aplicando correções para Windows 7...")

        # Desabilitar efeitos visuais avançados
        os.environ['TK_SILENCE_DEPRECATION'] = '1'

        # Forçar modo de compatibilidade
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(0)
        except:
            pass

    def corrigir_windows_8(self):
        """Correções para Windows 8/8.1"""
        print("🔧 Aplicando correções para Windows 8...")
        # Windows 8 geralmente funciona bem com as configurações padrão
        pass

    def corrigir_windows_10(self):
        """Otimizações para Windows 10"""
        print("🔧 Otimizando para Windows 10...")
        try:
            # Habilitar DPI awareness para telas de alta resolução
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    def corrigir_windows_11(self):
        """Otimizações para Windows 11"""
        print("🔧 Otimizando para Windows 11...")
        try:
            # Windows 11 suporta DPI awareness nível 2
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            pass


# Singleton para uso global
detector = WindowsCompatibilidade()