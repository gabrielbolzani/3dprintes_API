# Elegoo Saturn Home Assistant Integration

Este repositório contém uma integração customizada para o **Home Assistant** que permite monitorar impressoras **Elegoo Saturn 3 Ultra** diretamente no seu dashboard.

## 🚀 Funcionalidades

- **Configuração Simples**: Adicione sua impressora via interface do Home Assistant (Config Flow) usando apenas Nome e IP.
- **Monitoramento em Tempo Real**:
  - Status da máquina (Idle, Printing, Paused, Error).
  - Progresso da impressão em porcentagem.
  - Camada atual e Total de camadas.
  - Nome do arquivo em impressão.
  - Tempo restante estimado.
- **Protocolo Direto**: Comunicação via UDP (porta 3000) sem necessidade de APIs intermediárias.

## 🛠️ Como Instalar

1.  Baixe a pasta `custom_components/elegoo_saturn`.
2.  Copie a pasta para dentro do diretório `custom_components` da sua instalação do Home Assistant.
3.  Reinicie o Home Assistant.
4.  Vá em **Configurações > Dispositivos e Serviços > Adicionar Integração**.
5.  Pesquise por **Elegoo Saturn 3 Ultra**.
6.  Configure o nome e o IP da sua impressora.

## 📁 Estrutura do Projeto

- `custom_components/elegoo_saturn/`: Contém todo o código da integração.
  - `client.py`: Interface de comunicação com a impressora.
  - `sensor.py`: Definição de sensores para o HA.
  - `config_flow.py`: Lógica de configuração via interface.

---
*Desenvolvido por Gabriel Bolzani*
