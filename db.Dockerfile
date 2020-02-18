FROM mysql:8.0
WORKDIR /
# Fix "Authentication plugin 'caching_sha2_password' cannot be loaded" error in MySQL 8.0
COPY fixs/db_cnf/custom.cnf /etc/mysql/conf.d/custom.cnf