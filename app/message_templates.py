from datetime import datetime

def gerar_mensagem_fallback(nome, data, protocolo, endereco):
    return f"""
Prezado(a) {nome},
Aqui é da Proxxima Telecom.

Estamos confirmando o seu agendamento para atendimento técnico.

📋 **Detalhes do Agendamento**
• Protocolo: {protocolo}
• Endereço: {endereco}
• Data e Hora: {data}

Para confirmar ou reagendar, responda:
*1* — ✅ Confirmar este agendamento  
*2* — 📅 Selecionar nova data e horário  

📍 **Informações Importantes**
- Nossa equipe chegará no horário agendado.
- Caso não possa receber o técnico, pedimos aviso prévio para reagendamento.

Agradecemos pela confiança!

Atenciosamente,  
Equipe Técnica — Proxxima Telecom
""".strip()
