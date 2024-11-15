# 3D Printers API
#### Este é um projeto de API para gerenciamento de impressoras 3D. Atualmente, o foco da implementação está na comunicação com máquinas de resina Elegoo Saturn 3 Ultra, com funcionalidades para obter informações da impressora e seu status. No futuro, o projeto será expandido para suportar outras máquinas de impressão 3D, como as de filamento (FDM) e outras marcas.

## 🚧 Status do Projeto
Este projeto ainda não está completamente pronto e está em fase de desenvolvimento. Até o momento, ele oferece suporte para a máquina Elegoo Saturn 3 Ultra com algumas operações básicas. Em breve, serão implementadas funcionalidades para suporte a outros tipos de máquinas, como impressoras de filamento (FDM) e outras marcas.

## Funcionalidades Implementadas
Atualmente, a API oferece os seguintes endpoints:

#### Operações Gerais
- /general_operations/add_printer: Adicionar uma nova impressora 3D ao sistema.
- /general_operations/get_printers: Obter uma lista de todas as impressoras registradas.
- /general_operations/remove_printer_by_nickname: Remover uma impressora com base no seu apelido. (Ainda nao está funcionando)
#### Operações com Impressoras Elegoo
- /elegoo_operations/get_printer_info: Obter informações detalhadas sobre a impressora.
- /elegoo_operations/get_printer_status: Obter o status atual da impressora. (Arquivo que está sendo impresso, tempo decorrido, tempo estimado, porcentagem, e previsão de finalização)

### 🚀 Instalação e Execução
Para executar este projeto localmente, siga as etapas abaixo.

(Será implementado para funcionar com o docker)
