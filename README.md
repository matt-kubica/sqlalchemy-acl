# SQLAlchemy Acces List

## Virtual Environment
To initialize virtual env run following command in project root, `pipenv` required
```bash
$ pipenv shell
```


## Create Database
To create sqlite db according to model defined in `api.py` use `create_db.py` script
```bash
$ python create_db.py
```


## Testing API 
Easiest way to test without running flask development server is to open python interactive shell
```bash
$ python
```


Example of usage
```python
>>> import api
>>>
>>> ex1 = api.Wage(user='Pan prezes', amount=100000)
>>> ex2 = api.Wage(user='Manager', amount=15000)
>>> ex3 = api.Wage(user='Intern', amount=1000)
>>> api.db.session.add(ex1)
>>> api.db.session.add(ex2)
>>> api.db.session.add(ex3)
>>> 
>>> api.Wage.query.all()
[<Wage 1:Pan prezes:100000>, <Wage 2:Manager:15000>, <Wage 3:Intern:1000>]
>>> 
>>> api.db.session.commit()
```

## ACLQuery
For now class **acl.ACLQuery** extends **BaseQuery**, but without newly implemented methods or overrides
