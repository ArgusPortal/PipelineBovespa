import os
import time
import subprocess
import glob
import sys
import platform
import shutil
import datetime

def check_dependencies():
    """
    Check and fix package dependencies to avoid version incompatibility issues
    """
    try:
        import pandas as pd
        import numpy as np
        print(f"✅ Dependencies loaded successfully: numpy {np.__version__}, pandas {pd.__version__}")
    except ValueError as e:
        if "numpy.dtype size changed" in str(e):
            print("⚠️ Detected NumPy/pandas version incompatibility. Attempting to fix...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "numpy==1.23.5"])
            subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "pandas==1.5.3"])
            print("🔄 Dependencies reinstalled. Please restart the script.")
            sys.exit(1)
        else:
            print(f"❌ Unexpected error importing dependencies: {e}")
            sys.exit(1)

# First check dependencies before importing other modules
check_dependencies()

# Now import the rest of the modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
import pandas as pd
import requests
import zipfile
import io
import json

def get_chrome_version():
    """Get installed Chrome version using Windows Registry"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        return winreg.QueryValueEx(key, "version")[0]
    except Exception as e:
        print(f"⚠️ Could not detect Chrome version via registry: {str(e)}")
        try:
            # Fallback method using command line
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            result = subprocess.check_output(
                f'wmic datafile where name="{chrome_path}" get Version /value',
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return result.split('=')[1]
        except Exception as e2:
            print(f"❌ Fallback version detection failed: {str(e2)}")
            return None

def download_chromedriver(chrome_version, download_path):
    """Download compatible ChromeDriver from Chrome for Testing repository"""
    try:
        # Get the major version
        major_version = chrome_version.split('.')[0]
        print(f"🔍 Chrome major version: {major_version}")
        
        # Get the latest compatible version
        response = requests.get(f"https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json")
        response.raise_for_status()
        versions_data = response.json()
        
        # Find the latest stable version for this major version
        milestone_key = f"{major_version}"
        if milestone_key not in versions_data["milestones"]:
            raise ValueError(f"No ChromeDriver found for major version {major_version}")
        
        version_info = versions_data["milestones"][milestone_key]
        chromedriver_version = version_info["version"]
        print(f"✅ Found compatible ChromeDriver version: {chromedriver_version}")
        
        # Find the Windows download URL
        download_url = None
        for download in version_info["downloads"]["chromedriver"]:
            if download["platform"] == "win32":
                download_url = download["url"]
                break
        
        if not download_url:
            raise ValueError("No Windows download found for ChromeDriver")
        
        print(f"⬇️ Downloading ChromeDriver from: {download_url}")
        response = requests.get(download_url)
        response.raise_for_status()
        
        # Save and extract the zip file
        zip_path = os.path.join(download_path, "chromedriver.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        
        # Find the chromedriver.exe in the extracted files
        chromedriver_path = None
        for root, dirs, files in os.walk(download_path):
            if 'chromedriver.exe' in files:
                chromedriver_path = os.path.join(root, 'chromedriver.exe')
                break
        
        if not chromedriver_path:
            raise FileNotFoundError("chromedriver.exe not found in downloaded files")
        
        print(f"✅ ChromeDriver installed at: {chromedriver_path}")
        return chromedriver_path
        
    except Exception as e:
        print(f"❌ Failed to download ChromeDriver: {str(e)}")
        print("\n💡 Manual solution:")
        print("1. Download ChromeDriver from: https://googlechromelabs.github.io/chrome-for-testing/")
        print(f"2. Select version matching your Chrome ({chrome_version})")
        print("3. Extract chromedriver.exe to:", download_path)
        return None

def download_file_colab_fixed():
    """
    Baixa um arquivo do site da B3 usando Google Chrome,
    converte para Parquet e retorna ambos os caminhos de arquivo
    """
    is_windows = platform.system() == 'Windows'
    
    # Define base project directory - always use project path
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Always use data/raw within the project directory
    base_download_path = os.path.join(project_dir, "data", "raw")
    
    # Create base download directory if it doesn't exist
    os.makedirs(base_download_path, exist_ok=True)
    print(f"📂 Using base download directory: {base_download_path}")
    
    # Initial download will go to this temporary location
    temp_download_path = os.path.join(base_download_path, "temp")
    os.makedirs(temp_download_path, exist_ok=True)
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Suppress Chrome logging messages
    chrome_options.add_argument("--log-level=3")  # Only show fatal errors
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if os.name == 'nt':  # Windows
        # Redirect browser process stdout and stderr to null
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        os.environ['WDM_LOG_LEVEL'] = '0'  # Silence webdriver-manager logs
    
    # Set download preferences to temporary location
    prefs = {
        "download.default_directory": temp_download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Obter versão do Chrome
    chrome_version = get_chrome_version() if is_windows else None
    print(f"🔍 Chrome version: {chrome_version or 'Not detected'}")

    print("🚀 Configuring ChromeDriver...")
    driver = None
    
    try:
        if is_windows and chrome_version:
            print("🔄 Downloading ChromeDriver for Windows")
            chromedriver_path = download_chromedriver(chrome_version, temp_download_path)
            
            if chromedriver_path:
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ WebDriver initialized with manually installed ChromeDriver.")
            else:
                raise Exception("Manual ChromeDriver installation failed")
        else:
            # Tentar inicialização padrão para Linux ou quando a detecção falha
            print("🔄 Trying standard WebDriver initialization")
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ WebDriver initialized successfully.")
        
    except Exception as e:
        print(f"❌ WebDriver initialization failed: {e}")
        print("\nTroubleshooting suggestions:")
        print("1. Install ChromeDriver manually from:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        print("2. Make sure Chrome is installed and up to date")
        return None, None

    try:
        # --- Navigate to page ---
        print("🌐 Accessing IBOVESPA page on B3...")
        driver.get("https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br")
        
        # Wait for page load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "segment"))
        )
        print("📄 Page loaded successfully")

        # --- Select segment ---
        print("🔽 Selecting 'Setor de Atuação' segment...")
        
        # Handle overlays and clicks
        def select_segment():
            segment_dropdown = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "segment"))
            )
            
            try:
                segment_dropdown.click()
                return True
            except ElementClickInterceptedException:
                print("⚠️ Standard click intercepted, using JavaScript click")
                driver.execute_script("arguments[0].click();", segment_dropdown)
                return True
            except Exception:
                return False
        
        # Retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            print(f"↻ Attempt {attempt+1}/{max_retries} to select segment")
            if select_segment():
                break
            
            # Check for blocking overlay
            try:
                overlay = driver.find_element(By.CLASS_NAME, 'backdrop')
                driver.execute_script("arguments[0].style.display = 'none';", overlay)
                print("👋 Overlay removed")
            except:
                pass
            time.sleep(2)
        else:
            raise TimeoutException("Failed to select segment after multiple attempts")
        
        # Select specific option
        sector_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="segment"]/option[2]'))
        )
        sector_option.click()
        print("✅ Segment selected")
        time.sleep(3)  # Wait for page update

        # --- Download file ---
        print("💾 Locating and clicking download link...")
        download_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="divContainerIframeB3"]/div/div[1]/form/div[2]/div/div[2]/div/div/div[1]/div[2]/p/a'))
        )
        
        # List existing files before download
        existing_files = set(glob.glob(os.path.join(temp_download_path, "*")))
        print(f"📂 Existing files: {len(existing_files)} files")
        
        # Click download link
        download_link.click()
        print(f"⬇️ Download started at {time.strftime('%H:%M:%S')}")
        start_time = time.time()

        # --- Wait for download completion ---
        print("⏳ Waiting for download to complete...")
        
        # Wait for new file to appear
        max_wait = 300  # 5-minute timeout
        downloaded_file = None
        last_size = 0
        stable_count = 0
        
        while time.time() - start_time < max_wait:
            current_files = set(glob.glob(os.path.join(temp_download_path, "*")))
            new_files = current_files - existing_files
            
            # Check partial downloads
            partial_files = [f for f in new_files if f.endswith('.crdownload')]
            completed_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            if completed_files:
                # Prioritize IBOVDia.csv if exists
                ibov_files = [f for f in completed_files if "IBOVDia" in f]
                if ibov_files:
                    candidate = ibov_files[0]
                else:
                    candidate = completed_files[0]
                
                current_size = os.path.getsize(candidate)
                
                # Check if size is stable
                if current_size > 0:
                    if current_size == last_size:
                        stable_count += 1
                        print(f"📊 File size stable: {current_size} bytes ({stable_count}/3)")
                    else:
                        stable_count = 0
                        print(f"📈 File growing: {current_size} bytes")
                    
                    last_size = current_size
                    
                    # Consider download complete if size stable for 3 checks
                    if stable_count >= 3:
                        downloaded_file = candidate
                        print(f"✅ Download complete! Final size: {current_size} bytes")
                        break
                else:
                    print(f"⚠️ File found but empty: {candidate}")
            
            if partial_files:
                partial_file = partial_files[0]
                try:
                    size = os.path.getsize(partial_file)
                    print(f"⏱️ Partial download: {size} bytes")
                except:
                    print("⏱️ Partial download in progress")
            
            elif not new_files:
                elapsed = int(time.time() - start_time)
                print(f"🕒 Waiting for download to start... ({elapsed}s)")
            
            time.sleep(2)
        else:
            # Final check after timeout
            current_files = set(glob.glob(os.path.join(temp_download_path, "*")))
            new_files = current_files - existing_files
            completed_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            if completed_files:
                candidate = completed_files[0]
                if os.path.getsize(candidate) > 0:
                    downloaded_file = candidate
                    print(f"✅ File downloaded after timeout: {candidate}")
                else:
                    raise Exception(f"Downloaded file is empty: {candidate}")
            else:
                raise Exception(f"Download timeout after {max_wait} seconds - No file downloaded")
        
        # Extract date from the filename (format: IBOVDia_DD-MM-YY)
        file_basename = os.path.basename(downloaded_file)
        
        # Handle different possible date formats in filenames
        try:
            if "_" in file_basename:
                # Try to extract date from IBOVDia_28-07-25 format
                date_part = file_basename.split("_")[1].split(".")[0]
                
                # Convert from DD-MM-YY to YYYY-MM-DD format
                day, month, short_year = date_part.split("-")
                year = f"20{short_year}"  # Assuming 20XX for the year
                iso_date = f"{year}-{month}-{day}"
            else:
                # If no date in filename, use today's date
                today = datetime.datetime.now()
                iso_date = today.strftime("%Y-%m-%d")
                
            print(f"📅 Extracted date: {iso_date}")
        except Exception as e:
            print(f"⚠️ Could not extract date from filename: {e}")
            # Fallback to today's date
            today = datetime.datetime.now()
            iso_date = today.strftime("%Y-%m-%d")
            
        # Create date directory structure
        date_directory = os.path.join(base_download_path, f"date={iso_date}")
        os.makedirs(date_directory, exist_ok=True)
        print(f"📁 Created date directory: {date_directory}")
        
        # Move the file to the date directory
        final_csv_path = os.path.join(date_directory, file_basename)
        shutil.move(downloaded_file, final_csv_path)
        print(f"📦 Moved CSV to: {final_csv_path}")
            
        # --- Convert to Parquet ---
        print("\n🧪 Starting Parquet conversion...")
        parquet_filename = os.path.basename(final_csv_path).replace('.csv', '.parquet')
        parquet_path = os.path.join(date_directory, parquet_filename)
        
        try:
            print(f"📄 Trying to read file: {final_csv_path}")
            df = pd.read_csv(
                final_csv_path, 
                sep=';', 
                encoding='latin-1', 
                decimal=',',
                engine='python',
                on_bad_lines='skip'
            )
            
            if df.empty:
                raise ValueError("Empty DataFrame after reading CSV")
                
            print(f"📊 CSV loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Save as Parquet in date directory
            df.to_parquet(parquet_path)
            print(f"💾 Parquet file saved: {parquet_path}")
            
            # Size comparison
            csv_size = os.path.getsize(final_csv_path) / 1024 / 1024
            parquet_size = os.path.getsize(parquet_path) / 1024 / 1024
            print(f"📦 Size comparison: CSV={csv_size:.2f} MB → Parquet={parquet_size:.2f} MB")
            
            return final_csv_path, parquet_path
            
        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
            return final_csv_path, None

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        screenshot_path = os.path.join(temp_download_path, "error_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved as '{screenshot_path}'")
        return None, None
    finally:
        if driver:
            driver.quit()
            print(f"🚪 WebDriver closed at {time.strftime('%H:%M:%S')}")

def wait_for_download_completion(download_dir, existing_files, max_wait=300):
    """Waits for file download to complete and returns the downloaded file path"""
    start_time = time.time()
    downloaded_file = None
    last_size = 0
    stable_count = 0
    
    while time.time() - start_time < max_wait:
        # Get current files and identify new ones
        current_files = set(glob.glob(os.path.join(download_dir, "*")))
        new_files = current_files - existing_files
        
        # Check for partial and completed downloads
        partial_files = [f for f in new_files if f.endswith('.crdownload') or f.endswith('.tmp')]
        completed_files = [f for f in new_files if not (f.endswith('.crdownload') or f.endswith('.tmp'))]
        
        # If there are completed files, check size stability
        if completed_files:
            # Prioritize IBOVDia.csv if exists
            ibov_files = [f for f in completed_files if "IBOVDia" in f]
            if ibov_files:
                candidate = ibov_files[0]
            else:
                candidate = completed_files[0]
            
            current_size = os.path.getsize(candidate)
            
            # Check if size is stable
            if current_size > 0:
                if current_size == last_size:
                    stable_count += 1
                    print(f"📊 File size stable: {current_size} bytes ({stable_count}/3)")
                else:
                    stable_count = 0
                    print(f"📈 File growing: {current_size} bytes")
                
                last_size = current_size
                
                # Consider download complete if size stable for 3 checks
                if stable_count >= 3:
                    downloaded_file = candidate
                    print(f"✅ Download complete! Final size: {current_size} bytes")
                    break
            else:
                print(f"⚠️ File found but empty: {candidate}")
        
        if partial_files:
            partial_file = partial_files[0]
            try:
                size = os.path.getsize(partial_file)
                print(f"⏱️ Partial download: {size} bytes")
            except:
                print("⏱️ Partial download in progress")
        
        elif not new_files:
            elapsed = int(time.time() - start_time)
            print(f"🕒 Waiting for download to start... ({elapsed}s)")
        
        time.sleep(2)
    else:
        # Final check after timeout
        current_files = set(glob.glob(os.path.join(download_dir, "*")))
        new_files = current_files - existing_files
        completed_files = [f for f in new_files if not f.endswith('.crdownload')]
        
        if completed_files:
            candidate = completed_files[0]
            if os.path.getsize(candidate) > 0:
                downloaded_file = candidate
                print(f"✅ File downloaded after timeout: {candidate}")
            else:
                raise Exception(f"Downloaded file is empty: {candidate}")
        else:
            raise Exception(f"Download timeout after {max_wait} seconds - No file downloaded")
    
    # Return the downloaded file path
    return downloaded_file


if __name__ == "__main__":
    csv_path, parquet_path = download_file_colab_fixed()

    if csv_path and parquet_path:
        print("\n🎉 Process completed successfully!")
        print(f"CSV path: {csv_path}")
        print(f"Parquet path: {parquet_path}")
    elif csv_path:
        print("\n⚠️ CSV downloaded but conversion failed")
        print(f"CSV path: {csv_path}")
    else:
        print("\n❌ Process failed")