#service.py
import threading
from typing import Callable, Dict, Optional

from message_templates import gerar_mensagem_fallback
from whatsapp_sender import WhatsAppSender

ResultCallback = Callable[[bool, Dict[str, str], Optional[Exception]], None]


class BotService:
    def __init__(self):
        self._sender: Optional[WhatsAppSender] = None
        self._lock = threading.Lock()

    def _get_sender(self) -> WhatsAppSender:
        with self._lock:
            if self._sender is None:
                self._sender = WhatsAppSender()
            return self._sender

    def _reset_sender(self) -> None:
        with self._lock:
            if self._sender:
                try:
                    self._sender.close()
                except Exception:
                    pass
            self._sender = None

    def _ensure_initialized(self) -> WhatsAppSender:
        sender = self._get_sender()
        if not sender.initialize_driver():
            self._reset_sender()
            raise ConnectionError("Falha ao conectar ao WhatsApp Web.")
        return sender

    def enviar_mensagem_async(self, cliente: Dict[str, str], callback: ResultCallback) -> threading.Thread:
        if callback is None:
            raise ValueError("Callback obrigatório para receber o resultado do envio.")

        thread = threading.Thread(target=self._worker, args=(cliente, callback), daemon=True)
        thread.start()
        return thread

    def _worker(self, cliente: Dict[str, str], callback: ResultCallback) -> None:
        try:
            sender = self._ensure_initialized()
            mensagem = gerar_mensagem_fallback(
                cliente["nome"], cliente["data"], cliente["protocolo"], cliente["endereco"]
            )
            sucesso = sender.enviar_mensagem(cliente["telefone"], mensagem)
            callback(success=sucesso, cliente=cliente, error=None)
        except Exception as exc:
            if isinstance(exc, ConnectionError):
                self._reset_sender()
            callback(success=False, cliente=cliente, error=exc)

    def close(self) -> None:
        self._reset_sender()
