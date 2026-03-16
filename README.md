# WhatsApp Bot Local

Aplicação desktop em Tkinter para equipes técnicas confirmarem agendamentos via WhatsApp Web, oferecendo interface guiada, leitura automática de planilhas Excel e envio assíncrono de mensagens com template personalizável.

## Índice
- [Recursos principais](#recursos-principais)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e configuração](#instalação-e-configuração)
- [Fluxo típico de uso](#fluxo-típico-de-uso)
- [Formato da planilha de agendamentos](#formato-da-planilha-de-agendamentos)
- [Personalizando o texto](#personalizando-o-texto)
- [Diagnóstico e erros comuns](#diagnóstico-e-erros-comuns)
- [Estrutura do projeto](#estrutura-do-projeto)

## Recursos principais
- Interface lateral e painel principal estilizados com cores inspiradas no WhatsApp para acompanhar o status de cada envio.
- Seleção guiada da planilha Excel, leitura das datas disponíveis e carregamento do lote de clientes para a data escolhida.
- Tabela com listramento automático, destaque dos envios concluídos e contador que mostra quantos registros estão carregados.
- Envio assíncrono de mensagens por meio de `BotService`, que mantém a sessão do Selenium ativa e atualiza o status assim que o WhatsApp confirma o envio.
- Geração automática da mensagem a partir de `message_templates.py` com placeholders para nome, protocolo, endereço e data.

## Arquitetura
- `app/main.py`: monta toda a interface (sidebar, tabela, barra de ações) e orquestra os eventos de seleção de arquivo, carregamento de dados e envio das mensagens.
- `app/planilha_manager.py`: lê a planilha com cache inteligente, normaliza colunas por heurísticas (ex: reconhece “Data/Hora do Agendamento”, “Cliente”, “Telefone”, “Protocolo”, “Endereço” etc.), formata telefones nacionais e monta registros prontos para a UI.
- `app/service.py`: expõe `BotService`, que inicializa o `WhatsAppSender`, gera a mensagem e dispara um worker em thread para avisar o callback sobre sucesso ou falha.
- `app/whatsapp_sender.py`: controla o Selenium Chrome, reaproveitando o perfil do usuário (em `%LOCALAPPDATA%\MeuBotWhatsApp\User Data` no Windows ou `~/.local/share/meubotwhatsapp/User Data` no Linux) e acessando a URL direta do WhatsApp Web para evitar prompts.
- `app/message_templates.py`: centraliza o texto enviado ao cliente para facilitar ajustes de tom, branding ou idioma.

## Pré-requisitos
- Python 3.10 ou superior (o Tkinter já faz parte da stdlib).
- Google Chrome instalado e versão compatível com o ChromeDriver.
- ChromeDriver disponível no PATH ou na mesma pasta do script.
- Bibliotecas listadas em `requirements.txt` (`selenium`, `openpyxl`, `pandas`).

## Instalação e configuração
1. Crie um ambiente virtual e ative-o.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Verifique se o `chromedriver` compatível com o Chrome está acessível (use `chromedriver --version` para conferir).
4. Opcional: deixe o navegador fechado e, no primeiro envio, escaneie o QR Code ao abrir o WhatsApp Web para registrar o login (o perfil é salvo em `MeuBotWhatsApp/User Data`).

## Fluxo típico de uso
1. Execute `python -m app.main` (ou `python app/main.py`) para abrir a interface.
2. Clique em “Selecionar Arquivo” e escolha a planilha.
3. Após o carregamento automático das datas, selecione a data desejada e clique em “Carregar Agendamentos”.
4. Escolha um cliente clicando na linha correspondente e pressione “Enviar Mensagem”.
5. O botão fica desabilitado durante o envio e o status muda para indicar sucesso ou falha.

## Formato da planilha de agendamentos
- A leitura usa `pandas.read_excel(..., header=1)`, então a linha de cabeçalho deve estar na segunda linha (linha 2 do Excel). A primeira linha pode conter instruções ou título do documento.
- Colunas reconhecidas (com flexibilidade de nome):
  - Data: “Data/Hora do Agendamento”, “Data”, “Agendamento”, “Data Agendamento”, “Hora”.
  - Cliente: “Cliente”, “Nome”, “Nome Cliente”, “Nome do Cliente”.
  - Telefone: “Telefone Celular”, “Telefone”, “Celular”, “Whatsapp”, “Contato”.
  - Protocolo: “Nº. Ordem Serviço”, “Protocolo”, “Ordem Serviço”, “OS”, “Nº Ordem”.
  - Endereço: “Endereço”, “Logradouro”, “Rua”.
  - Número: “Número”, “Num”, “Nº”.
- O gerenciador formata telefones brasileiros (adiciona DDD 83 quando necessário e prefixa o 55).
- Os registros exibidos no grid trazem protocolo, nome, telefone, endereço montado e data formatada como `dd/mm/YYYY HH:MM`.
- Há um exemplo em `data/exemplo.xlsx` para referência de layout.

## Personalizando o texto
- Edite `app/message_templates.py` para mudar o corpo do SMS/WhatsApp. O helper `gerar_mensagem_fallback` recebe nome, data, protocolo e endereço.
- Mantenha o `.strip()` no final para evitar linhas em branco e preserve a marcação Markdown (negrito, listas, atendimentos).
- Se quiser criar variações por tipo de serviço, basta adicionar novas funções e trocar a chamada em `BotService._worker`.

## Diagnóstico e erros comuns
- **QR Code expira**: feche o app, execute novamente e escaneie o QR Code exibido pelo Chrome. O perfil é reutilizado no próximo envio.
- **Data não aparece**: confira se a planilha tem dados no formato de data e se nenhuma coluna foi renomeada manualmente após a primeira leitura (o cache evita releitura se o `mtime` não mudar).
- **Telefone inválido**: o botão ignora registros cujo número não contenha pelo menos um dígito. Verifique se a coluna de telefone tem valores numéricos ou strings.
- **Erro ao enviar**: o status fica com ponto vermelho, e o console (terminal) mostra o erro de Selenium. Reinicie o app e, se necessário, limpe `MeuBotWhatsApp/User Data` para forçar um novo login.

## Estrutura do projeto
- `app/`: código principal; subdividido em `main.py`, `service.py`, `planilha_manager.py`, `whatsapp_sender.py` e `message_templates.py`.
- `data/`: planilhas de exemplo. Substitua `exemplo.xlsx` por sua base real ou use este arquivo como template.
- `build/` & `dist/`: scripts e artefatos gerados caso você crie um instalador/com a `WhatsAppBotLocal.spec`.


