# O Natal que Pintamos Juntos — guia colorido

Guia público das 19 referências coloridas do livro de Eliane Tomás, com versões em português brasileiro e inglês americano. A URL principal permanece igual para o QR Code: navegadores em inglês recebem `/en/`; os demais recebem português. O seletor PT | EN permite a escolha manual, que fica guardada no navegador. A detecção usa a preferência de idioma do navegador, sem GPS ou localização geográfica.

O guia não inclui as páginas em preto e branco, autenticação nem dados pessoais. O repositório-fonte e as imagens destinam-se à publicação pública por autorização da autora; a ausência de licença aberta não transforma as ilustrações em domínio público.

## Estrutura

`public/` é o site estático completo. `public/data/scenes.json` registra a ordem, títulos, páginas e caminhos originais; `public/data/scenes.en.json` contém os títulos em inglês americano. `templates/index.html` e `templates/index.en.html` contêm os textos e layouts de cada idioma. `public/site.css` e `public/app.js` cuidam da aparência, da ampliação acessível e do compartilhamento localizado. `scripts/build_site.py` gera as duas páginas, metadados canônicos e sitemap usando apenas Python padrão.

`site-settings.json` guarda a URL pública e o campo `amazonEnglishUrl`. Deixe esse campo vazio até a listagem inglesa estar disponível; depois inclua ali o link HTTPS da Amazon e gere novamente o site.

## Desenvolvimento

Depois de editar os títulos, os templates ou os metadados, execute `python3 scripts/build_site.py`. Para visualizar, execute `python3 -m http.server 3000 --bind 0.0.0.0 --directory public`. A página funciona com JavaScript desativado: as ilustrações podem ser abertas e baixadas pelos links regulares, embora a detecção automática de idioma dependa de JavaScript.

## GitHub Pages

Publicar somente o conteúdo de `public/` na raiz da branch de publicação Pages e manter `.nojekyll`. Os caminhos dos assets são relativos para suportar sites de projeto em `https://<conta>.github.io/<repositório>/`. Não há backend, banco nem configuração secreta. Não renomear o repositório ou remover a branch de publicação depois de imprimir o QR sem preservar um redirecionamento durável.

## Fontes e imagens

Nunito e Fredoka são hospedadas localmente, com as licenças OFL em `public/assets/fonts/`. As miniaturas WebP preservam proporção e conteúdo das artes; os downloads são os PNGs originais aprovados. A seleção usa cena 1 v3, cena 12 v4, cena 16 v5 e a referência piloto da cena 6. Não incluir biografias familiares privadas, credenciais, PDFs de produção ou versões rejeitadas das cenas no repositório público.
