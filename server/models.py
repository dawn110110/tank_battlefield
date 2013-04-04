#!/usr/bin/env python
import peewee as pw

DATABASE = 'site.db'
database = pw.SqliteDatabase(DATABASE)

class BaseModel(pw.Model):
    class Meta:
        database = database


class User(BaseModel):
    id = pw.PrimaryKeyField()
    username = pw.CharField()
    pwd = pw.CharField()
    email = pw.CharField()
    join_date = pw.DateTimeField()

    class Meta:
        order_by = ('username',)

class Battle(BaseModel):
    id = pw.PrimaryKeyField()
    pa = pw.ForeignKeyField(User)
    pb = pw.ForeignKeyField(User)
    start = pw.DateTimeField()
    end = pw.DateTimeField()
    winner = pw.ForeignKeyField(User)
    log = pw.TextField()


