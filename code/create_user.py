import oracledb
import sys
import oci
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean
import constants
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_4")
print" ... 


def create_db_connection(username, userpwd):
    print(" in create_db_connection")
    host = constants.host
    port = 1521
    service_name = constants.service_name
    dsn = f'{username}/{userpwd}@{host}:{port}/{service_name}'
    connection = oracledb.connect(dsn)
    print(dsn)
    print(" exiting create_db_connection")
    return connection, dsn
sada

def create_demo_user(conn, demo_user, demo_passwd):
    print(" in creating demo user")
    try:
        cursor = conn.cursor()
        cursor.execute(
        """
        begin
        -- drop user
        begin
            execute immediate 'drop user """ + demo_user + """ cascade';
        exception
            when others then
                dbms_output.put_line('Error setting up user.');
        end;
        execute immediate 'create user """+ demo_user+ """ identified by """+ demo_passwd +""" ';
        execute immediate 'grant connect, unlimited tablespace, create credential, create procedure, create any index to """+demo_user +"""';
        execute immediate 'create or replace directory DEMO_PY_DIR as ''/scratch/hroy/view_storage/hroy_devstorage/demo/orachain''';
        execute immediate 'grant read, write on directory DEMO_PY_DIR to public';
        execute immediate 'grant create mining model to """+demo_user +""" ';
        execute immediate 'grant  create table, create any table to """+demo_user + """';

        -- network access
        begin
            DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
                host => '*',
                ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                                principal_name => ' """+demo_user+ """',
                                principal_type => xs_acl.ptype_db));
        end;
    end;
    """
    )
        print("User setup done!")
        cursor.close()
        conn.close()
    except Exception as e:
        print("User setup failed! ... error -- ",e)
        cursor.close()
        conn.close()
        sys.exit(1)
    print(" exiting creating demo user")

def __main__():
    print("..")
    admin_username=constants.admin_username
    admin_userpwd = constants.admin_userpwd
    connection, dsn = create_db_connection(admin_username, admin_userpwd)
    demo_user = constants.demo_user
    demo_passwd = constants.demo_passwd
    create_demo_user(connection,demo_user,demo_passwd) 