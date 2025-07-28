"""
Script para baixar uma versão específica do ChromeDriver compatível com o Chrome atual.
Use este script se estiver enfrentando problemas de compatibilidade entre Chrome e ChromeDriver.
"""
import os
import sys
import zipfile
import requests
import shutil
import platform
import subprocess
import winreg
from pathlib import Path

def print_section(title):
    """Imprime um título de seção formatado."""
    print("\n" + "="*80)
    print(title)
    print("="*80)

def get_chrome_version():
    """Tenta detectar a versão do Chrome instalada no sistema."""
    version = None
    
    system = platform.system()
    
    if system == "Windows":
        try:
            # Tentar detectar a versão pelo registro do Windows
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version = winreg.QueryValueEx(key, "version")[0]
            print(f"Chrome version detected from registry: {version}")
        except Exception:
            pass
            
    if not version:
        # Métodos alternativos de detecção
        try:
            if system == "Windows":
                process = subprocess.run(
                    ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
                    check=True, capture_output=True, text=True
                )
                version = process.stdout.strip().split()[-1]
            elif system == "Linux":
                process = subprocess.run(
                    ['google-chrome', '--version'],
                    check=True, capture_output=True, text=True
                )
                version = process.stdout.strip().split()[-1]
            elif system == "Darwin":  # macOS
                process = subprocess.run(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    check=True, capture_output=True, text=True
                )
                version = process.stdout.strip().split()[-1]
        except Exception as e:
            print(f"Error detecting Chrome version: {e}")
    
    return version

def get_compatible_chromedriver_versions():
    """Retorna uma lista de versões do ChromeDriver conhecidas por serem compatíveis com versões recentes do Chrome."""
    return [
        "114.0.5735.90",  # Boa compatibilidade com Chrome 114-120
        "115.0.5790.170", # Boa compatibilidade com Chrome 115-125
        "120.0.6099.109", # Boa compatibilidade com Chrome 120-130
        "122.0.6261.94",  # Boa compatibilidade com Chrome 122-133
        "123.0.6312.58",  # Boa compatibilidade com Chrome 123-135
        "124.0.6367.8",   # Boa compatibilidade com Chrome 124-136
    ]

def download_specific_chromedriver(version=None):
    """
    Baixa uma versão específica do ChromeDriver.
    
    Args:
        version: Versão específica do ChromeDriver para baixar. Se None, usa a lista de compatíveis.
    """
    print_section("BAIXANDO CHROMEDRIVER ESPECÍFICO")
    
    # Detectar versão do Chrome para informação
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"Versão do Chrome detectada: {chrome_version}")
    else:
        print("Não foi possível detectar a versão do Chrome")
    
    # Se não foi especificada uma versão, usa as compatíveis
    versions_to_try = [version] if version else get_compatible_chromedriver_versions()
    
    # Determinar o diretório para salvar o ChromeDriver
    project_root = Path(__file__).parent
    drivers_dir = project_root / "drivers"
    os.makedirs(drivers_dir, exist_ok=True)
    
    # Determinar o sistema operacional e arquitetura
    system = platform.system().lower()
    if system == "windows":
        platform_name = "win32"
        chromedriver_filename = "chromedriver.exe"
    elif system == "linux":
        platform_name = "linux64"
        chromedriver_filename = "chromedriver"
    elif system == "darwin":
        if platform.machine() == "arm64":
            platform_name = "mac-arm64"
        else:
            platform_name = "mac-x64"
        chromedriver_filename = "chromedriver"
    else:
        print(f"Sistema operacional não suportado: {system}")
        return
    
    success = False
    
    for driver_version in versions_to_try:
        print(f"\nTentando baixar ChromeDriver versão {driver_version}...")
        
        try:
            # URL para o ChromeDriver específico
            download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_{platform_name}.zip"
            print(f"URL de download: {download_url}")
            
            # Baixar o arquivo
            response = requests.get(download_url)
            
            if response.status_code == 200:
                # Salvar e extrair o arquivo
                zip_path = drivers_dir / "chromedriver_temp.zip"
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                
                # Extrair o chromedriver do zip
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    # As estruturas dos arquivos ZIP do ChromeDriver mudaram ao longo do tempo
                    chromedriver_files = [f for f in zip_ref.namelist() if os.path.basename(f) == chromedriver_filename]
                    if not chromedriver_files:
                        chromedriver_files = [f for f in zip_ref.namelist() if chromedriver_filename in f]
                    
                    if chromedriver_files:
                        # Extrair o arquivo do chromedriver
                        chromedriver_zip_path = chromedriver_files[0]
                        extracted_path = drivers_dir / chromedriver_filename
                        
                        # Remover arquivo existente se houver
                        if os.path.exists(extracted_path):
                            os.remove(extracted_path)
                        
                        # Extrair o novo chromedriver
                        with zip_ref.open(chromedriver_zip_path) as source, open(extracted_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        
                        # Tornar o chromedriver executável em sistemas Unix
                        if system != "windows":
                            os.chmod(extracted_path, 0o755)
                        
                        print(f"ChromeDriver extraído para: {extracted_path}")
                        print(f"ChromeDriver versão {driver_version} baixado com sucesso!")
                        success = True
                        break
                    else:
                        print(f"Não foi possível encontrar o chromedriver no arquivo ZIP")
                
                # Remover o arquivo ZIP temporário
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            else:
                print(f"Falha ao baixar ChromeDriver: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Erro ao baixar/extrair ChromeDriver: {e}")
    
    if success:
        print("\nChrome Driver baixado com sucesso e está pronto para uso!")
        print(f"Local: {drivers_dir / chromedriver_filename}")
    else:
        print("\nNão foi possível baixar nenhuma versão compatível do ChromeDriver.")
        print("Por favor, baixe manualmente em: https://chromedriver.chromium.org/downloads")
        print(f"E coloque o arquivo na pasta: {drivers_dir}")

if __name__ == "__main__":
    # Verificar se foi passada uma versão específica
    version = None
    if len(sys.argv) > 1:
        version = sys.argv[1]
    
    download_specific_chromedriver(version)
