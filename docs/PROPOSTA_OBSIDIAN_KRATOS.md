# Proposta de Integração: KRATOS + Obsidian.md (cPanel + Supabase Storage)

Este documento apresenta a proposta estratégica e o tutorial para integrar o ecossistema **KRATOS** (Posições AIS, Programação da Praticagem-RJ, Maré e Vento) com o **Obsidian** utilizando o **cPanel** (para processamento) e o **Supabase Storage** (como repositório de sincronização em nuvem).

Esta abordagem **não utiliza o Railway**, aproveitando o seu servidor cPanel atual para rodar o backend e o plano gratuito do Supabase para fazer o sincronismo das notas com o Obsidian.

---

## 1. Visão Geral e Arquitetura (cPanel + Supabase)

Para evitar a necessidade de montar discos de rede e simplificar o acesso em qualquer dispositivo, utilizaremos o **Supabase Storage** como a ponte de dados:

1.  **Processamento no cPanel:** O KRATOS continua rodando no cPanel. Ele mantém o WebSocket do AIS conectado e faz a sincronização da Praticagem.
2.  **Upload para o Supabase:** Sempre que as posições ou manobras mudam, o KRATOS gera as notas Markdown e faz o upload direto para um **Bucket de Armazenamento no Supabase (Supabase Storage)**.
3.  **Sincronização com o Obsidian (Remotely Save):** No seu Obsidian local (computador ou celular), você instala o plugin gratuito **Remotely Save** configurado com as chaves S3 do seu Supabase. O plugin sincroniza os arquivos automaticamente.

```text
+-----------------------+      Markdown Upload      +-----------------------+
|  KRATOS no cPanel     | ------------------------> |   Supabase Storage    |
| (FastAPI + Scrapers)  |                           |  (Bucket S3-Compat)   |
+-----------------------+                           +-----------------------+
                                                                ^
                                                                | Sincronia
                                                                v
                                                    +-----------------------+
                                                    |    Obsidian Local     |
                                                    | (Plugin RemotelySave) |
                                                    +-----------------------+
```

---

## 2. Modelagem das Notas (Nós e Conexões)

As notas geradas no Supabase conterão links bidirecionais (`[[Nome da Nota]]`) para formar as conexões no grafo do Obsidian:

*   **Manobra:** Contém calado, LOA, Boca, status, POB e links para `[[Navio]]`, `[[Berço]]`, `[[Dia]]` e `[[Empresa]]`.
*   **Navio:** Histórico de manobras e link para localização atual.
*   **Rebocador:** Velocidade, rumo e link para o berço/geofence atual (ex.: `[[Base Brasco]]`).
*   **Condição Diária:** Informações compiladas de vento e maré interligadas com as manobras do dia.

---

## 3. Planejamento de Sprints (Fases de Desenvolvimento)

### 🚀 Sprint 1: Conexão com Supabase Storage e Exportador Base
*   **Objetivo:** Configurar o cPanel para se conectar ao Supabase Storage e enviar arquivos Markdown básicos.
*   **Entregas:**
    *   Variáveis de ambiente no `.env`: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_S3_ACCESS_KEY`, `SUPABASE_S3_SECRET_KEY`, `SUPABASE_BUCKET`.
    *   Módulo Python `obsidian_supabase.py` no backend para criar e subir as notas no bucket.

### 🚀 Sprint 2: Motor de Links & Grafos Ricos
*   **Objetivo:** Enriquecer as notas com conexões bidirecionais (Manobra ↔ Navio ↔ Berço ↔ Rebocador ↔ Dia/Clima) e tags de visualização.
*   **Entregas:**
    *   Geração de notas ricas interligadas.
    *   Tags estruturadas (ex.: `#kratos/rebocador/saam`).
    *   Integração de maré real e vento nas notas diárias.

### 🚀 Sprint 3: Automatização do Sincronismo no cPanel
*   **Objetivo:** Configurar o envio automático das notas e interface no painel.
*   **Entregas:**
    *   Gatilho automático no backend a cada sincronização da Praticagem e a cada ciclo de dados AIS.
    *   Botão **"Sincronizar Obsidian (Supabase)"** no Dashboard do KRATOS.

### 🚀 Sprint 4: Tutorial de Configuração do Remotely Save e Casos de Uso
*   **Objetivo:** Homologação final, tutorial de configuração do plugin e uso do Graph View.

---

## 4. Tutorial de Configuração do Sincronismo (Obsidian + Supabase)

### Passo 1: Obter Credenciais S3 no Supabase
1. No painel do seu projeto Supabase, acesse **Storage** e crie um Bucket privado chamado `kratos-vault`.
2. Acesse **Project Settings** -> **API** e anote a sua `Project URL` e a chave `service_role` (que dão acesso de escrita ao cPanel).
3. Vá para as configurações de Storage e copie a **S3 Connection URL** e credenciais de chaves de acesso S3 (Access Key ID e Secret Access Key).

### Passo 2: Instalar o Plugin Remotely Save no Obsidian
1. No Obsidian, vá em **Settings** -> **Community plugins** -> **Browse** e procure por **Remotely Save**.
2. Instale e ative o plugin.

### Passo 3: Configurar o Remotely Save
1. Nas configurações do *Remotely Save*:
   *   **Sync Method:** Escolha **S3 or S3-compatible**.
   *   **Endpoint:** Insira a URL do Endpoint S3 do Supabase (ex.: `https://[project-id].supabase.co/storage/v1/s3`).
   *   **Region:** Deixe como `us-east-1` (ou a região do seu projeto Supabase).
   *   **Bucket Name:** `kratos-vault`.
   *   **Access Key ID** e **Secret Access Key:** Insira as credenciais geradas no painel do Supabase.
2. Defina o intervalo de sincronização automática para **5 minutos**.

### Passo 4: Configurar o Grafo (Graph View)
1. Pressione `Ctrl + G` no Obsidian.
2. Em **Groups**, adicione cores para as tags geradas:
   *   `tag:#kratos/rebocador/saam` → **Verde**
   *   `tag:#kratos/rebocador/concorrente` → **Vermelho**
   *   `tag:#kratos/manobra` → **Roxo**
   *   `tag:#kratos/navio/comercial` → **Azul**
   *   `tag:#kratos/berço` → **Amarelo**
