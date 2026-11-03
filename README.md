# O Natal que Pintamos Juntos — guia colorido

Guia público das 19 referências coloridas do livro de Eliane Tomás. Não inclui páginas em preto e branco, autenticação, dados pessoais, nem QR code nesta etapa. O repositório-fonte e as imagens nele incluídas destinam-se à publicação pública por autorização da autora. Ausência de licença aberta não transforma as ilustrações em domínio público.

## Estrutura

`public/` é o site estático completo, incluindo HTML pronto e assets. `public/data/scenes.json` registra ordem, títulos, páginas e caminhos. `templates/index.html` contém o layout e o texto editorial; `public/site.css` e `public/app.js` cuidam da aparência e da ampliação acessível. `scripts/build_site.py` gera o HTML completo com Python padrão, sem dependências de Node. `scripts/prepare_assets.py` prepara cópias web a partir das artes originais e não é executado na hospedagem. `site-settings.json` guarda somente a URL pública real, quando confirmada, para os metadados de compartilhamento.

## Desenvolvimento

Depois de editar os títulos, o template ou os metadados, executar `python3 scripts/build_site.py`. Para visualizar: `python3 -m http.server 3000 --bind 0.0.0.0 --directory public`. O site também funciona com JavaScript desativado: as imagens podem ser abertas e baixadas pelos links regulares.

## GitHub Pages

Todos os caminhos de assets são relativos para suportar sites de projeto em `https://<conta>.github.io/<repositorio>/`. Publicar somente o conteúdo de `public/` na raiz da branch de publicação Pages e manter o arquivo `.nojekyll`. Não há backend, banco ou configuração secreta. Só configurar o endereço canônico e o QR depois de confirmar a URL publicada. Não renomear o repositório ou remover a branch de publicação após imprimir o QR sem preservar um redirecionamento durável.

## Fontes e imagens

Nunito e Fredoka são hospedadas localmente, com as licenças OFL em `public/assets/fonts/`. As miniaturas WebP preservam a proporção e o conteúdo das artes; os downloads são os PNGs originais aprovados. A seleção usa cena 1 v3, cena 12 v4, cena 16 v5 e a referência piloto da cena 6. Não incluir biografias familiares privadas, credenciais, PDFs de produção ou versões rejeitadas das cenas no repositório público.
