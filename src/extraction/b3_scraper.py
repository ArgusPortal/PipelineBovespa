import os
import time
import subprocess
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

def download_file_colab_fixed():
    """
    Baixa um arquivo do site da B3 usando Google Chrome no Colab,
    converte para Parquet e retorna ambos os caminhos de arquivo
    """
    print("🔧 Instalando Google Chrome...")

    # Verificar se o Google Chrome já está instalado
    chrome_installed = False
    try:
        # Tentar obter a versão do Chrome
        chrome_version = subprocess.check_output(['google-chrome', '--version'], stderr=subprocess.STDOUT)
        print(f"✅ Google Chrome já instalado - Versão: {chrome_version.decode().strip()}")
        chrome_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Google Chrome não encontrado, procedendo com instalação...")
        chrome_installed = False

    # Instalar Google Chrome apenas se necessário
    if not chrome_installed:
        print("🔧 Instalando Google Chrome...")
        subprocess.run(['apt-get', 'update'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['dpkg', '-i', 'google-chrome-stable_current_amd64.deb'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['apt-get', 'install', '-f', '-y'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Verificar se a instalação foi bem-sucedida
        try:
            chrome_version = subprocess.check_output(['google-chrome', '--version'])
            print(f"✅ Google Chrome instalado com sucesso - Versão: {chrome_version.decode().strip()}")
        except Exception as e:
            print(f"❌ Falha na instalação do Google Chrome: {e}")
            raise

    # Configurar opções do Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Definir caminho de download
    download_path = "/content/raw_data"
    os.makedirs(download_path, exist_ok=True)
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    print("🚀 Configurando ChromeDriver...")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ WebDriver inicializado com sucesso.")
    except Exception as e:
        print(f"❌ Falha na inicialização do WebDriver: {e}")
        return None, None

    try:
        # --- Navegar até a página ---
        print("🌐 Acessando a página do IBOVESPA da B3...")
        driver.get("https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br")
        
        # Aguardar carregamento completo da página
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "segment"))
        )
        print("📄 Página carregada com sucesso")

        # --- Selecionar segmento ---
        print("🔽 Selecionando o segmento 'Setor de Atuação'...")
        
        # Lidar com sobreposições usando múltiplas estratégias
        def select_segment():
            try:
                # Tentar clique padrão
                segment_dropdown = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "segment"))
                )
                segment_dropdown.click()
                return True
            except ElementClickInterceptedException:
                # Usar clique via JavaScript como fallback
                print("⚠️ Clique padrão interceptado, usando clique JavaScript")
                driver.execute_script("arguments[0].click();", segment_dropdown)
                return True
            except Exception:
                return False
        
        # Mecanismo de repetição com tratamento de sobreposições
        max_retries = 3
        for attempt in range(max_retries):
            print(f"↻ Tentativa {attempt+1}/{max_retries} de selecionar segmento")
            if select_segment():
                break
            
            # Verificar se há sobreposição bloqueando
            try:
                overlay = driver.find_element(By.CLASS_NAME, 'backdrop')
                driver.execute_script("arguments[0].style.display = 'none';", overlay)
                print("👋 Sobreposição removida")
            except:
                pass
            time.sleep(2)
        else:
            raise TimeoutException("Falha ao selecionar segmento após múltiplas tentativas")
        
        # Selecionar opção específica
        sector_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="segment"]/option[2]'))
        )
        sector_option.click()
        print("✅ Segmento selecionado")
        time.sleep(3)  # Aguardar atualização da página

        # --- Baixar arquivo ---
        print("💾 Localizando e clicando no link de download...")
        download_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[2]/div/div[2]/div/div/div[1]/div[2]/p/a'))
        )
        
        # Listar arquivos existentes antes do download
        existing_files = set(glob.glob(os.path.join(download_path, "*")))
        print(f"📂 Arquivos existentes: {len(existing_files)} arquivos")
        
        # Clicar no link de download
        download_link.click()
        print(f"⬇️ Download iniciado às {time.strftime('%H:%M:%S')}")
        start_time = time.time()

        # --- Aguardar conclusão do download ---
        print("⏳ Aguardando conclusão do download...")
        
        # Aguardar novo arquivo aparecer
        max_wait = 300  # Timeout de 5 minutos
        downloaded_file = None
        last_size = 0
        stable_count = 0
        
        while time.time() - start_time < max_wait:
            # Obter arquivos atuais e identificar novos
            current_files = set(glob.glob(os.path.join(download_path, "*")))
            new_files = current_files - existing_files
            
            # Verificar downloads parciais
            partial_files = [f for f in new_files if f.endswith('.crdownload')]
            completed_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            # Se houver arquivos completos, verificar tamanho
            if completed_files:
                # Priorizar IBOVDia.csv se existir
                ibov_files = [f for f in completed_files if "IBOVDia" in f]
                if ibov_files:
                    candidate = ibov_files[0]
                else:
                    candidate = completed_files[0]
                
                current_size = os.path.getsize(candidate)
                
                # Verificar se o tamanho está estável por 3 verificações consecutivas
                if current_size > 0:
                    if current_size == last_size:
                        stable_count += 1
                        print(f"📊 Tamanho do arquivo estável: {current_size} bytes ({stable_count}/3)")
                    else:
                        stable_count = 0
                        print(f"📈 Arquivo aumentando: {current_size} bytes")
                    
                    last_size = current_size
                    
                    # Se o tamanho não mudar por 3 verificações, considerar download completo
                    if stable_count >= 3:
                        downloaded_file = candidate
                        print(f"✅ Download completo! Tamanho final: {current_size} bytes")
                        break
                else:
                    print(f"⚠️ Arquivo encontrado mas vazio: {candidate}")
            
            # Se houver arquivos parciais, mostrar progresso
            if partial_files:
                partial_file = partial_files[0]
                try:
                    size = os.path.getsize(partial_file)
                    print(f"⏱️ Download parcial: {size} bytes")
                except:
                    print("⏱️ Download parcial em progresso")
            
            # Se ainda não houver arquivos, mostrar status de espera
            elif not new_files:
                elapsed = int(time.time() - start_time)
                print(f"🕒 Aguardando início do download... ({elapsed}s)")
            
            time.sleep(2)
        else:
            # Verificação final após timeout
            current_files = set(glob.glob(os.path.join(download_path, "*")))
            new_files = current_files - existing_files
            completed_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            if completed_files:
                candidate = completed_files[0]
                if os.path.getsize(candidate) > 0:
                    downloaded_file = candidate
                    print(f"✅ Arquivo baixado após timeout: {candidate}")
                else:
                    raise Exception(f"Arquivo baixado está vazio: {candidate}")
            else:
                raise Exception(f"Timeout de download após {max_wait} segundos - Nenhum arquivo baixado")
        
        # --- Converter para Parquet ---
        print("\n🧪 Iniciando conversão para Parquet...")
        parquet_path = downloaded_file.replace('.csv', '.parquet')
        
        try:
            # Corrigir problema de formatação do CSV
            # Usar engine python e ignorar erros de formatação
            df = pd.read_csv(
                downloaded_file, 
                sep=';', 
                encoding='latin-1', 
                decimal=',',
                engine='python',
                on_bad_lines='skip'  # Ignorar linhas com problemas de formatação
            )
            
            # Verificar se o DataFrame foi carregado corretamente
            if df.empty:
                raise ValueError("DataFrame vazio após leitura do CSV")
                
            print(f"📊 CSV carregado com sucesso: {df.shape[0]} linhas, {df.shape[1]} colunas")
            
            # Salvar como Parquet
            df.to_parquet(parquet_path)
            print(f"💾 Arquivo Parquet salvo: {parquet_path}")
            
            # Comparação de tamanhos
            csv_size = os.path.getsize(downloaded_file) / 1024 / 1024
            parquet_size = os.path.getsize(parquet_path) / 1024 / 1024
            print(f"📦 Comparação de tamanhos: CSV={csv_size:.2f} MB → Parquet={parquet_size:.2f} MB")
            
            # Remover CSV original após conversão (opcional)
            # os.remove(downloaded_file)
            # print(f"🗑️ CSV original removido")
            
            return downloaded_file, parquet_path
            
        except Exception as e:
            print(f"❌ Falha na conversão: {str(e)}")
            return downloaded_file, None

    except Exception as e:
        print(f"❌ Ocorreu um erro: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        print("📸 Captura de tela salva como 'error_screenshot.png'")
        return None, None
    finally:
        driver.quit()
        print(f"🚪 WebDriver fechado às {time.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    csv_path, parquet_path = download_file_colab_fixed()

    if csv_path and parquet_path:
        print("\n🎉 Processo concluído com sucesso!")
        print(f"Caminho do CSV: {csv_path}")
        print(f"Caminho do Parquet: {parquet_path}")
    elif csv_path:
        print("\n⚠️ CSV baixado mas conversão falhou")
        print(f"Caminho do CSV: {csv_path}")
    else:
        print("\n❌ Processo falhou")
