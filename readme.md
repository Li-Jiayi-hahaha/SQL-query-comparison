# SQL Query Comparison

This is a backup version of our group project.
orignal contributor:
@botbw
@king159
@Li-Jiayi-hahaha
@WYing333

## Set up for database

move `cz4031-volume` to the root directory of the project

``` bash
docker pull postgres:15
docker run -d -p 5432:5432 -v $PWD/cz4031-volume:/var/lib/postgresql/data --name postgresql -e POSTGRES_PASSWORD=cz4031 postgres:15
```

## Set up for python environment

``` bash
conda install -c conda-forge psycopg2
pip install PyQt6
conda install -c conda-forge sqlparse
pip install networkx
pip install matplotlib
```

`debug mode` in VScode

``` json
{
    "name": "cz4031",
    "type": "python",
    "request": "launch",
    "program": "project.py",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

```
python project.py --host "localhost" --port "5432" --database "postgres" --user "postgres" --password "cz4031"
```
