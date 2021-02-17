# id_converter

If you're using multiple MySQL servers having the same tables, ideally, the scenario is easily supposed when you must add servers to manage the increasing workload such as growth of your business.

Table 1 on server1

| Data1 | Data2 | ID | Name |
| --- | --- | --- | --- |
| def | vef | 1 | corp2 |
| klm | efg | 2 | enter3 |
| pqr | xyz | 3 | service4 |

Table 1 on server2

| Data1 | Data2 | ID | Name |
| --- | --- | --- | --- |
| abc | def | 1 | corp1 |
| opq | rsu | 2 | enter2 |
| ghi | lmn | 3 | service3 |

After adding many MySQL servers, you'll face the difficulty to manage them. And then, you'll possibly find [Citus](https://www.citusdata.com) or [Azure Database for PostgreSQL Hyperscale (Citus)](https://docs.microsoft.com/en-us/azure/postgresql/hyperscale/). With Hyperscale (Citus), you don't need to care about the burden to manage the increasing workload. Only what you need to do is just adding 'worker nodes'.

But, you must merge the tables like above and specify a 'shard key', ideally, 'tenant ID', 'account ID', and so on.

This script can convert a local ID to a global unique ID in CSV.

`# id_converter.py server1_table1.csv server1_table1_new.csv -c 2`

Converted Table 1 from server1

| Data1 | Data2 | ID | Name |
| --- | --- | --- | --- |
| def | vef | 1 | corp2 |
| klm | efg | 2 | enter3 |
| pqr | xyz | 3 | service4 |

Yes, it looks nothing was changed.

`# id_converter.py server2_table1.csv server2_table1_new.csv -c 2`

Converted Table 1 from server2

| Data1 | Data2 | ID | Name |
| --- | --- | --- | --- |
| abc | def | 4 | corp1 |
| opq | rsu | 5 | enter2 |
| ghi | lmn | 6 | service3 |

Yeah, this table was successfully converted!

The script keeps a mapping rule in 'id_mapping' file after converting. So, it can convert other tables as follows.

Table 2 on server1

| ID | Data1 | Data2 | No | Name |
| --- | --- | --- | --- | --- |
| 1 | def | vef | 1 | corp2 |
| 2 | klm | efg | 2 | enter3 |
| 3 | pqr | xyz | 3 | service4 |

Table 2 on server2

| ID | Data1 | Data2 | No | Name |
| --- | --- | --- | --- | --- |
| 1 | abc | def | 1 | corp1 |
| 2 | opq | rsu | 2 | enter2 |
| 3 | ghi | lmn | 3 | service3 |

`# id_converter.py server1_table2.csv server1_table2_new.csv -c 0`

Converted Table 2 from server1

| ID | Data1 | Data2 | No | Name |
| --- | --- | --- | --- | --- |
| 1 | def | vef | 1 | corp2 |
| 2 | klm | efg | 2 | enter3 |
| 3 | pqr | xyz | 3 | service4 |

`# id_converter.py server2_table2.csv server2_table2_new.csv -c 0`

Converted Table 2 from server2

| ID | Data1 | Data2 | No | Name |
| --- | --- | --- | --- | --- |
| 4 | abc | def | 1 | corp1 |
| 5 | opq | rsu | 2 | enter2 |
| 6 | ghi | lmn | 3 | service3 |

Restore the tables on [Azure Database for MySQL](https://azure.microsoft.com/en-us/services/mysql/) with converted CSVs using your favorite mysql client. And [pgloader](https://pgloader.io) will be useful to migrate from MySQL to PostgreSQL Hyperscale (Citus).

```
# cat com.load
load database
    from mysql://User:Password@mysql_server_name.mysql.database.azure.com/your_db
    into pgsql://User:Password@pgsql_server_name-c.postgres.database.azure.com/your_db?sslmode=require
```

`pgloader com.load`

Don't forget to execute `SELECT create_distributed_table('table1', 'id')`.
