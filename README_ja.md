# id_converter

もし同じテーブルを持つ複数のMySQLサーバを使っているなら、典型的には、顧客が増えて負荷が重くなったのに対処するためにサーバを追加で立てる、というシナリオです。

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

で、たくさんのMySQLサーバを追加した後で、それを管理するのが大変ということに気づく、と。そうすると、[Citus](https://www.citusdata.com) とか [Azure Database for PostgreSQL Hyperscale (Citus)](https://docs.microsoft.com/ja-jp/azure/postgresql/hyperscale/)というのがあることに気づくかも知れません。Hyperscale (Citus)を使うと、増加するワークロードを管理する面倒臭い仕事から解放されます。しないとならないのは「ワーカーノード」の追加だけです。

ですが、上のようなデータを持ってるテーブルをマージして、「シャードキー」、典型的には「tenant ID」とか「account ID」のような「シャードキー」を指定しないとなりません。

このスクリプトは、CSV中の「ローカルな」IDを「グローバル」でユニークなIDに変換します。

`# id_converter.py server1_table1.csv server1_table1_new.csv -c 2`

Converted Table 1 from server1

| Data1 | Data2 | ID | Name |
| --- | --- | --- | --- |
| def | vef | 1 | corp2 |
| klm | efg | 2 | enter3 |
| pqr | xyz | 3 | service4 |

このテーブルには変化がありません。

`# id_converter.py server2_table1.csv server2_table1_new.csv -c 2`

Converted Table 1 from server2

| Data1 | Data2 | ID | Name |
| --- | --- | --- | --- |
| abc | def | 4 | corp1 |
| opq | rsu | 5 | enter2 |
| ghi | lmn | 6 | service3 |

はい、こちらはIDが書き換えられたのが分かりますね。

このスクリプトはファイル名に含まれる「サーバ名」とCSV中の「ID」をキーとする新しいIDへのマッピングを、「id_mapping」というファイルに保存します。なので、上の作業をした後で、Table 2のCSVを変換すると以下のようになります。

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

使い慣れたMySQLクライアントを使って、[Azure Database for MySQL](https://azure.microsoft.com/en-us/services/mysql/)に変換後のCSVをリストアします。さらに、[pgloader](https://pgloader.io)を使えば、MySQLからPostgreSQL Hyperscale (Citus)への移行は簡単にできます。

```
# cat com.load
load database
    from mysql://User:Password@mysql_server_name.mysql.database.azure.com/your_db
    into pgsql://User:Password@pgsql_server_name-c.postgres.database.azure.com/your_db?sslmode=require
```

`pgloader com.load`

Hyperscaleで`SELECT create_distributed_table('table1', 'id')`を実行するのを忘れないようにしてくださいね。
