"""
Script para diagnosticar problemas com importações no projeto PipelineBovespa.
Este script verifica o ambiente Python e tenta resolver problemas comuns com importações.
"""
import sys
import os
import subprocess
import platform
import site
import importlib.util

def print_section(title):
    """Imprime um título de seção formatado."""
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)

def check_environment():
    """Verifica o ambiente Python atual."""
    print_section("INFORMAÇÕES DO AMBIENTE PYTHON")
    
    # Versão do Python
    print(f"Versão do Python: {sys.version}")
    print(f"Executável do Python: {sys.executable}")
    
    # Verificar se está em um ambiente virtual
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"Em ambiente virtual: {'Sim' if in_venv else 'Não'}")
    
    if in_venv:
        print(f"Ambiente virtual: {sys.prefix}")
    
    # Listar caminhos do Python
    print("\nCaminhos do Python (sys.path):")
    for i, path in enumerate(sys.path):
        print(f"  {i+1}. {path}")
    
    # Diretórios de pacotes do site
    print("\nDiretórios de pacotes do site:")
    for path in site.getsitepackages():
        print(f"  - {path}")

def check_package(package_name):
    """Verifica se um pacote está instalado e disponível."""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'Desconhecida')
            location = getattr(spec, 'origin', 'Desconhecida')
            print(f"[OK] {package_name}: INSTALADO (Versão: {version}, Local: {location})")
            return True
        except ImportError as e:
            print(f"[AVISO] {package_name}: INSTALADO MAS COM ERRO DE IMPORTAÇÃO ({e})")
            return False
    else:
        print(f"[ERRO] {package_name}: NÃO INSTALADO OU NÃO ENCONTRADO")
        return False

def check_packages():
    """Verifica pacotes relevantes para o projeto."""
    print_section("VERIFICAÇÃO DE PACOTES")
    packages = [
        "selenium", 
        "webdriver_manager",
        "pandas",
        "numpy",
        "pyarrow",
        "boto3"  # Added boto3 to the verification
    ]
    
    missing_packages = []
    for package in packages:
        if not check_package(package):
            missing_packages.append(package)
    
    return missing_packages

def fix_packages(packages):
    """Tenta instalar pacotes faltantes."""
    if not packages:
        return True
    
    print_section("INSTALANDO PACOTES FALTANTES")
    print("Tentando instalar os pacotes necessários...")
    
    success = True
    for package in packages:
        try:
            print(f"Instalando {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            
            # Verificar a instalação
            if check_package(package):
                print(f"[OK] {package} instalado com sucesso")
            else:
                print(f"[AVISO] {package} não pôde ser verificado após a instalação")
                success = False
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Falha ao instalar {package}: {e}")
            success = False
    
    return success

def fix_path_issues():
    """Tenta resolver problemas de path para o projeto."""
    print_section("CORRIGINDO PROBLEMAS DE PATH")
    
    # Obter o diretório do projeto
    project_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"Diretório do projeto: {project_dir}")
    
    # Verificar se o diretório do projeto está no sys.path
    if project_dir not in sys.path:
        print(f"Adicionando {project_dir} ao sys.path")
        sys.path.insert(0, project_dir)
        with open(os.path.join(project_dir, "sitecustomize.py"), "w") as f:
            f.write(f"""
# Este arquivo é carregado automaticamente pelo Python ao iniciar
# Ele adiciona o diretório do projeto ao sys.path
import sys
import os

# Adicionar diretório do projeto ao path
project_dir = {repr(project_dir)}
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)
""")
        print("[OK] Criado arquivo sitecustomize.py para corrigir path em carregamentos futuros")
    else:
        print("[OK] O diretório do projeto já está no sys.path")
    
    # Criar arquivo .env com PYTHONPATH
    with open(os.path.join(project_dir, ".env"), "w") as f:
        f.write(f"PYTHONPATH={project_dir}\n")
    print("[OK] Criado arquivo .env com PYTHONPATH definido")
    
    # Criar/atualizar arquivo .vscode/settings.json se estiver usando VS Code
    vscode_dir = os.path.join(project_dir, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    
    settings_file = os.path.join(vscode_dir, "settings.json")
    settings = {}
    
    # Carregar configurações existentes se o arquivo existir
    if os.path.exists(settings_file):
        import json
        try:
            with open(settings_file, "r") as f:
                settings = json.load(f)
        except:
            pass
    
    # Atualizar configurações
    if "python.analysis.extraPaths" not in settings:
        settings["python.analysis.extraPaths"] = []
    
    if project_dir not in settings["python.analysis.extraPaths"]:
        settings["python.analysis.extraPaths"].append(project_dir)
    
    # Verificar se já existe uma referência ao interpretador Python
    if "python.defaultInterpreterPath" not in settings:
        settings["python.defaultInterpreterPath"] = sys.executable
    
    # Salvar configurações
    import json
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)
    
    print(f"[OK] Configurações do VS Code atualizadas: {settings_file}")
    
    return True

def create_test_script():
    """Cria um script de teste para verificar as importações."""
    print_section("CRIANDO SCRIPT DE TESTE")
    
    test_file = os.path.join(os.path.dirname(__file__), "test_imports.py")
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("""# Script para testar importações
import sys
print(f"Python: {sys.version}")
print(f"Executável: {sys.executable}")

print("\\nTestando importações:")
try:
    import selenium
    print(f"[OK] selenium {selenium.__version__}")
except ImportError as e:
    print(f"[ERRO] Erro ao importar selenium: {e}")

try:
    import webdriver_manager
    print(f"[OK] webdriver_manager {webdriver_manager.__version__}")
except ImportError as e:
    print(f"[ERRO] Erro ao importar webdriver_manager: {e}")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    print("[OK] Todas as classes necessárias do selenium e webdriver_manager")
except ImportError as e:
    print(f"[ERRO] Erro ao importar classes específicas: {e}")

# Verificar WebDriverWait (import correto)
try:
    from selenium.webdriver.support.wait import WebDriverWait
    print("[OK] WebDriverWait importado corretamente")
except ImportError as e:
    print(f"[ERRO] Erro ao importar WebDriverWait: {e}")

# Verificar boto3
try:
    import boto3
    print(f"[OK] boto3 {boto3.__version__}")
except ImportError as e:
    print(f"[ERRO] Erro ao importar boto3: {e}")

print("\\nCaminhos do Python:")
for path in sys.path:
    print(f"  - {path}")
""")
    
    print(f"[OK] Script de teste criado: {test_file}")
    print(f"   Execute-o com: {sys.executable} {test_file}")
    
    return test_file

def main():
    print_section("DIAGNÓSTICO DE IMPORTAÇÕES DO PIPELINE BOVESPA")
    
    print("Executando verificações do ambiente...")
    check_environment()
    
    print("\nVerificando pacotes necessários...")
    missing_packages = check_packages()
    
    if missing_packages:
        print(f"\nPacotes faltantes: {', '.join(missing_packages)}")
        fix_packages(missing_packages)
    
    print("\nCorrigindo possíveis problemas de path...")
    fix_path_issues()
    
    test_file = create_test_script()
    
    print_section("RESUMO E PRÓXIMOS PASSOS")
    print("""
Para resolver problemas de importação no seu IDE (VS Code, PyCharm, etc.):

1. Reinicie o seu IDE após as alterações feitas por este script
2. Verifique se você está usando o interpretador Python correto no IDE
3. Execute o script de teste para confirmar que as importações funcionam:""")
    print(f"   {sys.executable} {test_file}")
    
    print("""
4. Se ainda houver problemas, tente:
   - Desativar e reativar seu ambiente virtual (se estiver usando)
   - Reindexar os pacotes no seu IDE (específico para cada IDE)
   - Verificar se há conflitos entre diferentes versões do Python

Se você estiver usando o VS Code:
1. Pressione Ctrl+Shift+P
2. Digite "Python: Select Interpreter"
3. Selecione o interpretador que tem selenium e webdriver_manager instalados
""")

if __name__ == "__main__":
    main()
