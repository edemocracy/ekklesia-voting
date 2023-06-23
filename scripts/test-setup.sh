#!/usr/bin/env bash
tmpdir=$(mktemp -d)
socketdir=${1:-$tmpdir}
echo "Using database temp dir $tmpdir"
export LC_ALL='en_US.UTF-8'
pg_ctl -D $tmpdir init
pg_ctl start -D $tmpdir -o "-k $socketdir -h ''"
createdb -h $socketdir test_ekklesia_voting
echo "Loading test database..."
psql -h $socketdir test_ekklesia_voting -f tests/test_db.sql
doit
echo "export EKKLESIA_VOTING_TEST_DB_URL=\"postgresql+psycopg2:///test_ekklesia_voting?host=$socketdir\""
