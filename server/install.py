#!/usr/bin/env python
import models as m


def create_tables():
    m.User.create_table()
    m.Battle.create_table()
    print 'ok'

def main():
    try:
        create_tables()
    except:
        ans = 'xx'
        while ans not in ['yes', 'no']:
            ans = raw_input("table exist, delete them?[yes/no]")

        if ans == 'yes':
            m.User.drop_table()
            m.Battle.drop_table()
        else:
            print 'create_table failed'
            return
        create_tables()

if __name__ == "__main__":
    main()

