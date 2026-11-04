# Publicação GitHub Pages

O repositório `elianecpereirat-stack/o-natal-que-pintamos-juntos` foi conectado e sua visibilidade pública está autorizada. A branch `gh-pages` recebe somente os arquivos estáticos publicados, na raiz, preservando a pasta `public/` e o código-fonte no `main`.

Na conta GitHub proprietária, abrir Settings → Pages. Em Build and deployment, selecionar Source: **Deploy from a branch**, Branch: **gh-pages**, Folder: **/ (root)** e clicar **Save**. Não selecionar GitHub Actions nem main, pois a página de entrada do main fica na pasta public.

Depois que o GitHub confirmar a publicação, o endereço esperado é `https://elianecpereirat-stack.github.io/o-natal-que-pintamos-juntos/`. Este endereço não deve ser considerado ativo sem a confirmação e um teste de acesso público. O código QR será gerado em etapa posterior.

Para atualizar o site, primeiro gerar o HTML com `python3 scripts/build_site.py` e salvar o main canônico. Depois publicar a árvore de `public/` em um novo commit normal na branch gh-pages, sem force-push nem reescrever seu histórico.
