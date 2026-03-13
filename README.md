# CME QRCode

Este é o sistema de gestão de materiais e kits cirúrgicos com integração AGHU.

## Configuração

Variáveis de ambiente suportadas (padrões entre parênteses):

- `DJANGO_SECRET_KEY` (gerada automaticamente para desenvolvimento)
- `DJANGO_DEBUG` (`True`/`False`)
- `DJANGO_ALLOWED_HOSTS` (lista separada por espaços)
- `DATABASE_URL` ou as variáveis abaixo para o banco principal:
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `AGHU_USE_DB` (`True`/`False`)
- `AGHU_DB_NAME`, `AGHU_DB_USER`, `AGHU_DB_PASSWORD`, `AGHU_DB_HOST`, `AGHU_DB_PORT`
- `AGHU_BASE_URL`, `AGHU_TIMEOUT`

Um arquivo `.env` na raiz pode ser usado em conjunto com pacotes como
`python-dotenv` para carregar esses valores.

O projeto usa PostgreSQL em produção e SQLite em memória durante testes.

## Dependências

Instale usando pip no ambiente virtual:

```bash
pip install -r requirements.txt
```

Certifique-se de ter `psycopg2` para a conexão com o AGHU.

## Execução

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O servidor atenderá em `http://localhost:8000/`; acesse `/login/` para entrar.

## Estrutura

- `materiais/` – app principal com modelos, views e templates.
- `aghu_service.py` – conexão direta ao banco AGHU via psycopg2.
- `views_kitpaciente.py` – fluxo moderno de processos.
- `views.py` – código legado, ainda mantido por compatibilidade.

## Melhorias planejadas

- remover completamente o código legado (`views.py`, `ChecklistItem`)
- migrar configuração sensível para variáveis de ambiente
- adicionar autenticação mais forte e CSRF em todas as APIs
- escrever testes de integração com PostgreSQL real

