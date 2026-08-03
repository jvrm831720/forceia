-- Cria o database usado pela Evolution API (roda so no primeiro start do volume)
SELECT 'CREATE DATABASE evolution'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'evolution')\gexec
