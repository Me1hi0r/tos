from pathlib import Path

from clickhouse_driver import Client
from clickhouse_migrations.clickhouse_cluster import ClickhouseCluster

cluster = ClickhouseCluster('tos-click', 'default', '')
cluster.migrate('metric.tos', Path('/service/app/migrations'), cluster_name=None, create_db_if_no_exists=True, multi_statement=True)
print('migration complete')
