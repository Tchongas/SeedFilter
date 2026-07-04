# Seed Filter

Filter de seeds do [Aero](https://github.com/AeroAstroid/GoATS-filter), mas com uma UI e outras coisinhas.

## INSTALAR

1. Baixe a última versão e extraia o `.zip`.
2. Certifique-se de que o **Python 3.x** está instalado e adicionado ao PATH.
3. Clique duas vezes em **`RUNME.bat`** na pasta extraída.
4. Ele vai abrir, e criar um atalho na Área de Trabalho. ou nao, as vezes nao consegue

O `RUNME.bat` instala o único pacote Python necessário (`ttkbootstrap`) caso esteja faltando, abre o app e cria um atalho na Área de Trabalho.

> Se estiver compilando a partir do código-fonte, clone o repositório e execute `git submodule update --init --recursive` para baixar o Cubiomes e o SFMT.

## Funcionalidades

- **UI** — ative as estruturas que você quer e configure cada uma.
- **Presets** — salve suas configurações e importe presets de outras pessoas como uma string de números.
- **Filtros de loot** — exija quantidades mínimas de ferro, ouro, diamantes, esmeraldas, TNT, comida e mais para estruturas compatíveis.
- **Posição personalizada do stronghold** — procure um stronghold próximo a coordenadas específicas do Nether, com uma margem configurável.

## Como usar

1. Abra o app
2. Navegue pelas abas (**General**, **Overworld**, **Nether**, **End**, **Spawn**) e ative os filtros desejados.
3. Configure
4. Escolha a versão do Minecraft na barra superior.
5. Clique em **Generate & Run**.
6. As seeds compatíveis são exibidas.
7. O arquivo com as seeds pode ser acessado clicando em **Tools** > **Open Data Folder** e abrindo o arquivo `seedinfo.txt`.

Use **Save / Import** no menu de presets para guardar ou compartilhar configurações.

## Compilando a partir do código-fonte

O núcleo de busca de seeds é escrito em C e usa a biblioteca Cubiomes. Se você alterar o código C, recompile:

```cmd
cd SeedFilter
compile.bat
```

A interface em Python não precisa ser recompilada.

## Dependências

- **Python 3.x** — para a interface.
- **gcc** — para compilar o buscador de seeds em C (TDM-GCC, MinGW ou MSYS2 no Windows).
- **Java 17+** — apenas se quiser usar o lava checker legado.
- **ttkbootstrap** — usado pela interface para estilização.

Bibliotecas principais:
- [Cubiomes](https://github.com/cubitect/cubiomes) — geração do mundo e das estruturas.
- [SFMT](https://github.com/MersenneTwister-Lab/SFMT) — Mersenne Twister rápido orientado a SIMD.

## Compartilhamento

Você pode compactar a pasta inteira e enviar para outra pessoa. Quem receber só precisa de:

- Windows
- Python 3.x
- Conexão com a internet na primeira execução (para o `RUNME.bat` instalar o `ttkbootstrap`)

O `RUNME.bat` cria o atalho na Área de Trabalho na primeira execução.