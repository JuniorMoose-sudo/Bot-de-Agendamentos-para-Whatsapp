import os
import sys
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_profile_path() -> str:
    """
    Retorna um caminho seguro para o perfil no diretório de dados do usuário.
    Essa pasta contém tokens sensíveis e não deve ser compartilhada ou versionada.
    """
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "MeuBotWhatsApp", "User Data")

    base = os.path.expanduser("~")
    return os.path.join(base, ".local", "share", "meubotwhatsapp", "User Data")

class WhatsAppSender:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.profile_path = get_profile_path()


    #  INICIALIZAÇÃO DO SELENIUM (UMA VEZ SÓ)

    def initialize_driver(self):
        if self.driver and self.is_logged_in:
            return True

        chrome_options = webdriver.ChromeOptions()

        os.makedirs(self.profile_path, exist_ok=True)

        chrome_options.add_argument(f"--user-data-dir={self.profile_path}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")

        # Melhora muito a velocidade no Windows
        chrome_options.page_load_strategy = "eager"

        # Usando o ChromeDriver
        self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.get("https://web.whatsapp.com")
        print("Aguardando login no WhatsApp Web...")

        try:
            # A forma correta de verificar o login é esperar por um elemento
            # que só aparece DEPOIS que o QR code é escaneado e a interface principal carrega.
            # O seletor foi ajustado para ser mais específico e evitar falsos positivos.
            WebDriverWait(self.driver, 90).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            self.is_logged_in = True
            print("WhatsApp conectado!")
            return True
        except Exception:
            print("Login não detectado em 90 segundos. Você escaneou o QR Code? Fechando navegador.")
            self.close()
            return False


    #  ENVIO DE MENSAGEM

    # O método enviar_mensagem foi ajustado para usar a URL direta do web.whatsapp.com, que é mais estável e evita o prompt para abrir o aplicativo de desktop, que causava o erro "no such window".

    def enviar_mensagem(self, telefone, mensagem):
        if not self.driver or not self.is_logged_in:
            # Esse erro é crítico e indica que o aplicativo não está pronto para enviar mensagens.
            print("ERRO: Driver não inicializado ou login não efetuado.")
            raise ConnectionError("O WhatsApp não está conectado. Tente reiniciar o aplicativo.")

        telefone_str = str(telefone).strip()
        telefone_limpo = "".join(filter(str.isdigit, telefone_str))

        if not telefone_limpo:
            print("Telefone inválido.")
            return False

        if not telefone_limpo.startswith("55"):
            telefone_limpo = "55" + telefone_limpo

        msg_codificada = urllib.parse.quote(mensagem)

        # A URL direta do web.whatsapp.com é mais estável e evita o prompt
        # para abrir o aplicativo de desktop, que causa o erro "no such window".
        url = f"https://web.whatsapp.com/send?phone={telefone_limpo}&text={msg_codificada}"

        # Armazena a janela principal antes de qualquer ação
        main_window = self.driver.current_window_handle

        try:
            self.driver.get(url)

            # Espera o botão ENVIAR
            # O seletor foi ajustado para ser mais específico e robusto.
            botao = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]/..'))
            )

            botao.click()
            # Aumentar o tempo de espera para garantir que a mensagem seja processada
            # antes de iniciar a próxima navegação.
            time.sleep(2)

            print(f"Mensagem enviada para {telefone_limpo}")
            return True
        except Exception as e:
            print(f"Falha ao enviar para {telefone_limpo}: {e}")
            return False
        finally:
            # Com a URL direta, o WhatsApp Web geralmente carrega na mesma aba,
            self.driver.switch_to.window(self.driver.window_handles[0])

    #  FECHAR DRIVER

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.is_logged_in = False
