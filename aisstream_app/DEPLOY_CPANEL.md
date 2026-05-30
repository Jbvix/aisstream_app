# Deploy cPanel (Git Version Control)

O cPanel 126 só permite **Deploy HEAD Commit** / push automático se:

1. Existir um **`.cpanel.yml` válido** na raiz do repositório (já incluído neste projeto).
2. A **working tree estiver limpa** — sem alterações locais não commitadas.

## Erro: «The system cannot deploy»

Quase sempre é a condição (2): ficheiros em `data/users/default/` alterados pela app em produção (sync Praticagem, estatísticas AIS, etc.).

### Correcção imediata no servidor (Terminal cPanel ou SSH)

```bash
cd ~/aisstream_app
# Ajuste o caminho se o Git Version Control mostrar outro diretório.

git status
```

Se aparecerem ficheiros modificados que **não** quer perder, faça backup antes:

```bash
cp data/users/default/saa_maneuvers.json /tmp/saa_maneuvers.bak
cp data/users/default/tug_geofence_stats.json /tmp/tug_geofence_stats.bak
```

Depois limpe a árvore (escolha uma opção):

**Opção A — descartar alterações locais a esses ficheiros (repor o último commit):**

```bash
git restore data/users/default/saa_maneuvers.json data/users/default/tug_geofence_stats.json
# ou, se ainda estiverem tracked numa versão antiga:
git checkout -- data/users/default/
```

**Opção B — guardar tudo num stash e voltar ao HEAD limpo:**

```bash
git stash push -u -m "antes deploy cPanel"
```

Volte ao **Git Version Control → Gerenciar** e use **Update from Remote** (se aplicável) e depois **Deploy HEAD Commit**.

### Depois do commit que deixa de versionar `saa_maneuvers.json` e `tug_geofence_stats.json`

Esses dois ficheiros passam a ser **ignorados pelo Git**: a app continua a gravá-los em disco, mas o Git **não** os marca como modificados, pelo que a árvore fica limpa para o cPanel.

Faça `git pull` no servidor. Se o `git pull` avisar de ficheiros locais, use `git stash` uma última vez e repita o pull.

## `.cpanel.yml` e `DEPLOYPATH`

O ficheiro define `DEPLOYPATH=/home/c62gtwye66po/aisstream_app`. Deve coincidir com o **caminho real do clone** na conta (ver na lista «Repository Path»). Se o utilizador cPanel for outro, altere `DEPLOYPATH` no `.cpanel.yml` **no repositório** e faça commit.

## `geofences.json`

Continua versionado. Se também ficar «sujo» no servidor e bloquear deploy, use `git restore data/users/default/geofences.json` (após backup) ou `git stash`.
