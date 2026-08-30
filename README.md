# Controle de Toner

Aplicação desktop para **controle de máquinas de impressão, registro de trocas de toner, acompanhamento de rendimento, histórico por cor e geração de relatórios em PDF e Excel**.

O projeto foi desenvolvido em Python com interface gráfica baseada em [CustomTkinter](https://customtkinter.tomschimansky.com/), persistência local em [SQLite](https://www.sqlite.org/), exportação para PDF com [fpdf2](https://py-pdf.github.io/fpdf2/) e planilhas Excel com [openpyxl](https://openpyxl.readthedocs.io/).

> **Status do projeto:** funcional, com foco em uso local no Windows. Antes de utilizar em ambiente crítico, consulte a seção [Limitações conhecidas e recomendações](#limita%C3%A7%C3%B5es-conhecidas-e-recomenda%C3%A7%C3%B5es).

## Sumário

- [Visão geral](#vis%C3%A3o-geral)

- [Principais funcionalidades](#principais-funcionalidades)

- [Tecnologias utilizadas](#tecnologias-utilizadas)

- [Arquitetura](#arquitetura)

- [Estrutura do projeto](#estrutura-do-projeto)

- [Requisitos](#requisitos)

- [Instalação para desenvolvimento](#instala%C3%A7%C3%A3o-para-desenvolvimento)

- [Execução](#execu%C3%A7%C3%A3o)

- [Como utilizar](#como-utilizar)

- [Banco de dados](#banco-de-dados)

- [Backup e restauração](#backup-e-restaura%C3%A7%C3%A3o)

- [Limpeza completa dos dados](#limpeza-completa-dos-dados)

- [Geração de relatórios](#gera%C3%A7%C3%A3o-de-relat%C3%B3rios)

- [Compilação do executável](#compila%C3%A7%C3%A3o-do-execut%C3%A1vel)

- [Criação do instalador](#cria%C3%A7%C3%A3o-do-instalador)

- [Distribuição e atualização](#distribui%C3%A7%C3%A3o-e-atualiza%C3%A7%C3%A3o)

- [Solução de problemas](#solu%C3%A7%C3%A3o-de-problemas)

- [Boas práticas de uso](#boas-pr%C3%A1ticas-de-uso)

- [Limitações conhecidas e recomendações](#limita%C3%A7%C3%B5es-conhecidas-e-recomenda%C3%A7%C3%B5es)

- [Roadmap](#roadmap)

- [Contribuição](#contribui%C3%A7%C3%A3o)

- [Licença](#licen%C3%A7a)

- [Referências](#refer%C3%AAncias)

## Visão geral

O **Controle de Toner** foi criado para centralizar o acompanhamento do consumo de suprimentos de impressoras. Cada máquina pode possuir um ou mais toners ativos, de acordo com seu tipo, e cada toner instalado recebe um registro individual com cor, data de instalação, contador inicial, custo, observação e, quando finalizado, data de retirada e contador final.

O sistema calcula automaticamente o total de páginas produzidas por toner e o custo aproximado por página. O rendimento de referência utilizado atualmente é de **14.500 impressões por toner**. Registros abaixo desse valor são destacados na interface e nos relatórios.

A aplicação é local e utiliza um arquivo SQLite armazenado na pasta de documentos do usuário. Não há servidor, API ou banco de dados remoto configurado no projeto atual.

## Principais funcionalidades

### Cadastro de máquinas

Permite cadastrar e atualizar máquinas com nome, modelo, tipo e contador atual. Os tipos disponíveis são:

| Tipo | Cores disponíveis |
| --- | --- |
| `P&B` | Preto |
| `Colorida` | Preto, Ciano, Magenta e Amarelo |
| `Mista` | Preto, Ciano, Magenta e Amarelo |

O contador da máquina representa o maior valor conhecido para aquele equipamento e é usado como referência durante o registro de novas trocas.

### Registro simplificado de troca

O fluxo de troca ocorre em uma única tela. O usuário seleciona a máquina e a cor, informa a data, o contador atual, o custo e uma observação opcional.

Quando já existe um toner ativo da mesma cor, o sistema tenta finalizar o registro anterior utilizando o contador informado e instala o novo toner. Quando não existe toner anterior, o registro é tratado como primeira instalação daquela cor.

O sistema também alerta quando o toner finalizado apresenta rendimento inferior à meta configurada.

### Histórico geral

Exibe os toners finalizados, suas datas, contadores, total de impressões, custo e custo por página. Os dados podem ser filtrados conforme a máquina e o período selecionado.

### Histórico por cor

Organiza o histórico individualmente por cor e apresenta indicadores como:

- quantidade de toners utilizados;

- média de impressões;

- total de impressões;

- custo total;

- menor e maior rendimento;

- custo médio por toner;

- custo médio por página.

### Relatórios

A aplicação gera relatórios nos seguintes formatos:

| Formato | Características |
| --- | --- |
| PDF | Tabela de rendimento, totais, custo por página e destaques de baixo rendimento. |
| Excel | Uma aba por máquina, formatação de valores, totais e indicadores estatísticos. |

Os relatórios podem ser gerados para uma máquina específica ou para todas as máquinas com registros finalizados no período informado.

## Tecnologias utilizadas

| Tecnologia | Uso |
| --- | --- |
| Python 3.10 ou superior | Linguagem principal. |
| CustomTkinter | Interface gráfica moderna baseada em Tkinter. |
| SQLite | Banco de dados local. |
| fpdf2 | Geração de relatórios PDF. |
| openpyxl | Geração de arquivos Excel. |
| Pillow | Manipulação de ícones e imagens. |
| PyInstaller | Criação do executável Windows. |
| Inno Setup | Criação do instalador Windows. |

## Arquitetura

O projeto segue uma arquitetura desktop monolítica com separação básica entre interface, persistência, modelos e relatórios.

```
main.py
   |
   v
gui_app.py  --->  database_operations.py  --->  database.py  --->  SQLite
   |                         |
   |                         +--> models.py
   |
   +--> relatorios.py
   +--> calendar_widget.py
   +--> compatibilidade.py
```

### Fluxo de inicialização

1. `main.py` identifica a plataforma do sistema operacional.

1. Em Windows, tenta aplicar ajustes de compatibilidade.

1. O módulo `gui_app.py` é importado.

1. A pasta de dados é criada, caso ainda não exista.

1. O banco SQLite e suas tabelas são inicializados.

1. A janela principal é aberta e os dados das máquinas são carregados.

### Fluxo de uma troca

```
Selecionar máquina
       |
Selecionar cor
       |
Validar data, contador e custo
       |
Localizar toner ativo da mesma cor
       |
Finalizar toner anterior, se existir
       |
Cadastrar novo toner
       |
Atualizar contador da máquina
       |
Exibir confirmação e alerta de rendimento
```

## Estrutura do projeto

```
Controle de Toner/
├── main.py                    # Ponto de entrada da aplicação
├── gui_app.py                 # Interface gráfica e fluxos de usuário
├── database.py                # Inicialização, caminhos e backups do SQLite
├── database_operations.py     # Consultas e operações de negócio
├── models.py                  # Dataclasses do domínio
├── relatorios.py              # Exportação para PDF e Excel
├── calendar_widget.py         # Widget de seleção de datas
├── compatibilidade.py         # Ajustes de compatibilidade entre plataformas
├── limpar_dados.py            # Utilitário destrutivo de limpeza total
├── converter_icone.py         # Conversão/geração de ícone
├── icone.ico                  # Ícone da aplicação
├── build.bat                  # Script de compilação com PyInstaller
├── ControleToner.spec         # Configuração do PyInstaller
├── installer_setup.iss        # Script do instalador Inno Setup
├── build/                     # Artefatos temporários de compilação
├── dist/                      # Aplicação empacotada pelo PyInstaller
└── instalador_final/          # Instalador compilado
```

Os diretórios `build/`, `dist/` e `instalador_final/` são artefatos de distribuição. Para manter um repositório limpo, recomenda-se não versionar esses diretórios, salvo quando houver uma política explícita de distribuição de binários.

## Requisitos

Para executar a partir do código-fonte, recomenda-se:

- Windows 10 ou superior;

- Python 3.10 ou superior;

- `pip` atualizado;

- permissões de leitura e escrita na pasta de documentos do usuário;

- aproximadamente 100 MB livres para dependências, ambiente e artefatos de build.

O projeto foi preparado principalmente para Windows. Há trechos de compatibilidade para Linux e macOS, mas a validação operacional principal deve ser feita em Windows.

## Instalação para desenvolvimento

### 1. Clonar o repositório

```bash
git clone https://github.com/JoaoViCarneiro/Controle-de-Tonner
cd Controle-de-Tonner
```


### 2. Criar um ambiente virtual

No Windows PowerShell:

```
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Prompt de Comando:

```
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

O projeto atual instala as dependências no `build.bat`. Para desenvolvimento, execute:

```bash
python -m pip install --upgrade pip
python -m pip install customtkinter fpdf2 openpyxl Pillow
```

Para gerar executáveis:

```bash
python -m pip install pyinstaller
```

> **Recomendação:** crie um arquivo `requirements.txt` com versões fixadas antes de utilizar o projeto em equipe ou em processos automatizados de build.

## Execução

Com o ambiente virtual ativado, execute:

```bash
python main.py
```

Também é possível iniciar diretamente o módulo da interface:

```bash
python gui_app.py
```

A primeira execução cria automaticamente o banco e as pastas de dados. Caso o Windows bloqueie a execução, verifique as permissões da pasta do projeto, do ambiente virtual e da pasta de documentos do usuário.

## Como utilizar

### Cadastrar uma máquina

1. Abra a aba **Máquinas**.

1. Informe o nome da impressora.

1. Informe o modelo, se disponível.

1. Selecione o tipo da máquina.

1. Informe o contador inicial ou mantenha `0`.

1. Clique em **Salvar Máquina**.

Para atualizar uma máquina, selecione-a na tabela, altere os dados e salve novamente.

### Registrar uma troca

1. Abra a aba **Registrar Troca**.

1. Selecione a máquina.

1. Selecione a cor do toner.

1. Informe a data no formato `DD/MM/AAAA`.

1. Informe o contador atual da máquina.

1. Informe o custo do toner.

1. Inclua uma observação, se necessário.

1. Clique em **Registrar Troca**.

O contador informado deve ser maior ou igual ao maior contador previamente registrado para a máquina. Quando houver toner ativo da mesma cor, o novo contador deve ser maior que o contador inicial do toner anterior.

### Consultar o histórico

Utilize a aba **Histórico** para consultar os registros finalizados. Para uma análise detalhada por cor, utilize **Histórico por Cor**.

### Exportar um relatório

1. Abra a aba **Relatórios**.

1. Selecione uma máquina ou a opção **Todas**.

1. Informe opcionalmente as datas inicial e final.

1. Escolha **Gerar PDF** ou **Gerar Excel**.

1. Escolha o local de salvamento quando solicitado.

Somente toners finalizados aparecem nos relatórios de rendimento.

## Banco de dados

O sistema utiliza SQLite e cria o arquivo no seguinte caminho lógico:

```
Documentos/ControleToner/dados.db
```

No Windows, a pasta `Documentos` é localizada por meio da API do sistema, com fallback para o diretório `Documents` do usuário. Em outros sistemas, é utilizado `~/Documents/ControleToner`.

### Tabela `maquinas`

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | INTEGER | Identificador autoincremental. |
| `nome` | TEXT | Nome da máquina. |
| `modelo` | TEXT | Modelo da impressora. |
| `tipo` | TEXT | `P&B`, `Colorida` ou `Mista`. |
| `contador_atual` | INTEGER | Maior contador conhecido. |
| `data_cadastro` | TIMESTAMP | Data de criação do registro. |

### Tabela `toners_individual`

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | INTEGER | Identificador autoincremental. |
| `maquina_id` | INTEGER | Máquina associada. |
| `cor` | TEXT | `Preto`, `Ciano`, `Magenta` ou `Amarelo`. |
| `data_instalacao` | DATE | Data de instalação. |
| `data_retirada` | DATE | Data de finalização/retirada. |
| `contador_inicial` | INTEGER | Contador na instalação. |
| `contador_final` | INTEGER | Contador na retirada. |
| `custo` | REAL | Custo do toner. |
| `observacao` | TEXT | Observação livre. |
| `data_registro` | TIMESTAMP | Data de inclusão no banco. |

O banco possui índices para `maquina_id` e para o par de datas de instalação/retirada.

## Backup e restauração

O sistema cria backups automáticos no primeiro dia do mês, quando o aplicativo é aberto, na pasta:

```
Documentos/ControleToner/backups/
```

São mantidos até 12 backups automáticos. Também existe a função de backup manual no módulo `database.py`.

Para proteger os dados, recomenda-se:

1. fechar a aplicação antes de copiar o banco manualmente;

1. copiar `dados.db` e a pasta `backups` para um local externo;

1. manter múltiplas versões históricas;

1. testar periodicamente a abertura de uma cópia do banco;

1. nunca substituir o banco original sem criar um backup adicional.

### Restauração manual básica

1. Feche o Controle de Toner.

1. Faça uma cópia do arquivo atual `dados.db`.

1. Escolha um backup válido na pasta `backups`.

1. Copie o backup para `Documentos/ControleToner/dados.db`.

1. Inicie novamente a aplicação.

A restauração manual deve ser realizada com cautela. Em ambiente de produção, prefira criar uma rotina de restauração assistida e validar a integridade do arquivo antes de substituí-lo.

## Limpeza completa dos dados

O arquivo `limpar_dados.py` contém um utilitário que remove:

- o banco de dados;

- todos os registros de máquinas;

- todos os registros de toner;

- a pasta de backups;

- os relatórios exportados.

Execute somente quando tiver certeza de que deseja reiniciar o sistema:

```bash
python limpar_dados.py
```

O utilitário exige a digitação de `LIMPAR` para confirmar a operação e tenta criar um backup antes da remoção. Ainda assim, faça uma cópia externa manual antes de utilizá-lo.

> **Atenção:** a limpeza é destrutiva e não deve ser executada em uma instalação com dados importantes sem backup validado.

## Geração de relatórios

O módulo `relatorios.py` disponibiliza duas funções principais:

```python
from relatorios import gerar_relatorio_pdf, gerar_relatorio_excel
```

### PDF

```python
gerar_relatorio_pdf(
    rendimentos,
    maquina_nome,
    periodo,
    caminho_destino="relatorio.pdf"
 )
```

### Excel

```python
gerar_relatorio_excel(
    dados_maquinas,
    periodo,
    caminho_destino="relatorio.xlsx"
)
```

Os relatórios destacam visualmente registros abaixo do rendimento esperado e calculam o custo por página com base no custo do toner dividido pelo número de impressões registradas.

## Compilação do executável

O projeto inclui o script `build.bat`, que instala dependências, remove builds anteriores e gera uma distribuição `onedir` com PyInstaller.

No Windows, a partir da pasta do projeto:

```
build.bat
```

O executável será gerado em:

```
dist\ControleToner\ControleToner.exe
```

O modo `onedir` gera uma pasta com o executável e suas dependências, em vez de um único arquivo. Isso tende a facilitar a inicialização e o diagnóstico da distribuição.

### Compilação manual equivalente

```
python -m PyInstaller ^
  --onedir ^
  --windowed ^
  --name="ControleToner" ^
  --icon=icone.ico ^
  --add-data="database.py;." ^
  --add-data="database_operations.py;." ^
  --add-data="models.py;." ^
  --add-data="relatorios.py;." ^
  --add-data="calendar_widget.py;." ^
  --add-data="compatibilidade.py;." ^
  --add-data="limpar_dados.py;." ^
  --hidden-import=customtkinter ^
  --hidden-import=fpdf ^
  --hidden-import=openpyxl ^
  --hidden-import=PIL ^
  --hidden-import=sqlite3 ^
  --collect-all=customtkinter ^
  main.py
```

## Criação do instalador

O arquivo `installer_setup.iss` contém a configuração do instalador para [Inno Setup](https://jrsoftware.org/isinfo.php).

Pré-requisitos:

- Windows;

- Inno Setup instalado;

- build do PyInstaller concluído em `dist\ControleToner\`;

- arquivo `icone.ico` disponível.

Passos:

1. Abra `installer_setup.iss` no Inno Setup.

1. Confirme os caminhos do executável e do ícone.

1. Compile o script.

1. Teste o instalador em uma máquina Windows limpa.

1. Teste a atualização mantendo uma cópia do banco.

O instalador cria atalhos no menu Iniciar e, opcionalmente, na área de trabalho.

## Distribuição e atualização

Antes de distribuir uma nova versão:

1. faça backup do banco de produção;

1. valide a versão em uma máquina limpa;

1. teste cadastro, troca, histórico e relatórios;

1. confirme que o instalador não substitui ou remove `dados.db`;

1. teste o processo de atualização sobre uma instalação existente;

1. registre a versão no instalador e nas notas de release;

1. mantenha uma cópia da versão anterior para rollback.

O banco deve ser tratado como dado do usuário, não como arquivo descartável da aplicação.

## Solução de problemas

### A aplicação não abre

Confirme se o Python está instalado, se o ambiente virtual está ativado e se as dependências foram instaladas:

```bash
python --version
python -m pip show customtkinter fpdf2 openpyxl Pillow
```

Execute pelo terminal para visualizar mensagens de erro:

```bash
python main.py
```

### O ícone não aparece

Verifique se `icone.ico` está na pasta esperada e se o executável foi recompilado após a inclusão do arquivo.

### O relatório não é salvo

Confirme se o usuário possui permissão de escrita no destino escolhido. Evite diretórios protegidos pelo Windows e teste uma pasta dentro de `Documentos`.

### O histórico parece incompleto

Os relatórios de rendimento exibem somente toners com `data_retirada` preenchida. Toners ainda ativos não aparecem nesses relatórios.

### Os dados parecem ter desaparecido

Não execute novamente `limpar_dados.py`. Feche o aplicativo, localize `Documentos/ControleToner/backups/` e preserve todos os arquivos antes de tentar qualquer restauração.

### O contador foi rejeitado

O sistema impede registrar um contador menor que o maior contador conhecido para a máquina. Verifique o contador exibido no formulário e confirme se o valor foi digitado corretamente.

## Boas práticas de uso

Registre a troca no momento em que o toner for instalado ou retirado. Use sempre a leitura real do contador da máquina e mantenha um padrão para as observações, como fornecedor, número da nota fiscal ou motivo da substituição.

Evite cadastrar a mesma impressora mais de uma vez. Utilize nomes identificáveis e consistentes, preferencialmente combinando setor, localização e modelo. Faça backups periódicos fora do computador local e valide ao menos uma cópia antes de confiar nela para restauração.

## Limitações conhecidas e recomendações

A versão atual possui alguns pontos que devem ser tratados antes de uso em cenário de alta criticidade:

| Prioridade | Ponto | Recomendação |
| --- | --- | --- |
| Crítica | A troca de toner é executada em etapas de persistência separadas. | Encapsular fechamento e instalação em uma única transação com `commit`/`rollback`. |
| Crítica | As chaves estrangeiras do SQLite não são habilitadas explicitamente em cada conexão. | Executar `PRAGMA foreign_keys = ON` na fábrica de conexões. |
| Alta | O banco aceita datas inválidas, custos negativos e contadores negativos. | Validar no domínio e adicionar restrições `CHECK` no esquema. |
| Alta | A interface localiza máquinas por nome, que não é único. | Trabalhar com IDs internamente e adicionar identificador único adequado. |
| Alta | A exclusão de máquina pode remover o histórico ou deixar registros órfãos. | Preferir arquivamento/exclusão lógica e exigir backup antes da operação. |
| Média | O backup automático só ocorre quando o programa é aberto no primeiro dia do mês. | Adicionar backup manual assistido, validação de integridade e destino externo. |
| Média | Há tratamento genérico de exceções e muitos `print`. | Usar logging estruturado e exceções específicas. |
| Média | Não há manifesto formal de dependências. | Criar `requirements.txt` ou `pyproject.toml` com versões fixadas. |
| Média | Não foram identificados testes automatizados de domínio e persistência. | Criar testes unitários e de integração com banco temporário. |
| Média | O instalador concede permissões amplas para os diretórios de dados. | Revisar `everyone-full` e aplicar o menor privilégio possível. |

Essas limitações não impedem o uso inicial em um computador controlado, mas devem ser consideradas no planejamento de produção.

## Roadmap

### Curto prazo

- Implementar troca atômica em uma única transação.

- Habilitar chaves estrangeiras em todas as conexões.

- Validar datas com `datetime.strptime`.

- Rejeitar custos e contadores inválidos.

- Corrigir a seleção de máquinas para utilizar IDs.

- Criar manifesto formal de dependências.

### Médio prazo

- Adicionar testes automatizados.

- Criar backup e restauração assistidos.

- Implementar exclusão lógica ou arquivamento.

- Centralizar configurações e caminhos.

- Substituir mensagens de console por logging.

- Adicionar localização/setor e identificador patrimonial da máquina.

### Longo prazo

- Implementar usuários, permissões e auditoria.

- Registrar fornecedor, nota fiscal e lote do toner.

- Permitir metas de rendimento configuráveis por modelo e cor.

- Criar indicadores de custo por setor e período.

- Avaliar sincronização corporativa com banco centralizado.

## Contribuição

Contribuições são bem-vindas. Para propor uma alteração:

1. faça um fork do repositório;

1. crie uma branch descritiva;

1. implemente a alteração acompanhada de testes;

1. confirme que a aplicação inicia e que os fluxos principais continuam funcionando;

1. atualize o README quando houver mudança de comportamento;

1. abra um Pull Request descrevendo o problema, a solução e os testes realizados.

Exemplo:

```bash
git checkout -b feat/backup-restauracao
git add .
git commit -m "feat: adiciona fluxo assistido de restauração"
git push origin feat/backup-restauracao
```

### Convenção sugerida de commits

| Prefixo | Uso |
| --- | --- |
| `feat:` | Nova funcionalidade. |
| `fix:` | Correção de defeito. |
| `refactor:` | Refatoração sem alteração funcional intencional. |
| `docs:` | Documentação. |
| `test:` | Testes. |
| `build:` | Empacotamento e distribuição. |
| `chore:` | Manutenção geral. |

## Licença

Este projeto ainda não declara uma licença de código aberto. Antes de publicar o repositório publicamente, escolha e adicione um arquivo `LICENSE`, como MIT, Apache-2.0 ou outra licença compatível com a finalidade do projeto.

> Sem um arquivo de licença, o código não deve ser presumido como livre para reutilização, modificação ou distribuição.

## Referências

- [Python — Documentação oficial](https://docs.python.org/3/)

- [CustomTkinter — Documentação](https://customtkinter.tomschimansky.com/)

- [SQLite — Documentação oficial](https://www.sqlite.org/docs.html)

- [SQLite — Foreign Key Support](https://www.sqlite.org/foreignkeys.html)

- [fpdf2 — Documentação](https://py-pdf.github.io/fpdf2/)

- [openpyxl — Documentação](https://openpyxl.readthedocs.io/)

- [PyInstaller — Manual](https://pyinstaller.org/en/stable/)

- [Inno Setup — Site oficial](https://jrsoftware.org/isinfo.php)
