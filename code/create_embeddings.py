import oracledb
import sys
import oci
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean
import constants
import database_connections
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_4")



def create_connection_to_ocigenai(connection):

    cursor_query =            """
        declare
            jo json_object_t;
        begin

          
            jo := json_object_t();
            jo.put('user_ocid','""" + constants.user_ocid + """' );
            jo.put('tenancy_ocid','"""+constants.tenancy_ocid + """');
            jo.put('compartment_ocid','"""+constants.compartment_ocid + """');
            jo.put('fingerprint','"""+ constants.fingerprint + """');
            dbms_vector_chain.create_credential(
                credential_name   => 'OCI_CRED',
                params            => json(jo.to_string));
        end;
        """

    try:
        cursor = connection.cursor()
        cursor.execute(cursor_query)
        cursor.close()
        print("Credentials created.")
    except Exception as ex:
        print("error is ... {ex}".format(ex=ex))
        cursor.close()
        raise


def create_table(connection, org):
    cursor = connection.cursor()
    print("... in create table ... ")
    try:
        cursor.execute("""
        begin
            execute immediate 'drop table {test}_web_embeddings';
            exception when others then if sqlcode <> -942 then raise; end if;
        end;""".format(test = org))
    except Exception as e:
        print("Error dropping table for {org} and error is {e}".format(org=org, e=e))
    try:
        cursor.execute("""
            create table {org}_web_embeddings (
                id number,
                content varchar2(4000),
                vec vector(1024, float32),
                source_url varchar2(4000),
                primary key (id)
            )""".format(org=org))
    except Exception as e:
        print("Error while creating table for {org} and error is {e}".format(org=org, e=e))

def parse_and_chunk_url_text(source_url):
    formatted_url = source_url.strip()
    chunks = []
    try:
        elements = partition_html(url=formatted_url, headers=constants.headers, skip_headers_and_footers=True)
    except Exception as e:
        print("Error while attempting to crawl {site} and error is {error}".format(site=formatted_url, error=e))
    else:
        chunks = chunk_by_title(elements)
    finally:
        return chunks


# Data Preperation - Embedding
def create_knowledge_base_from_client_content(connection, org, contents):
    cursor = connection.cursor()
    create_table(connection, org = org)
    print("creating embeddings for {org}".format(org=org))
    len_of_contents = len(contents)
    print("len of contents is ", len_of_contents)
    start = 0
    cursor_index = 0
    while start < len_of_contents:
        embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
        content_subsets = contents[start:start+96]
        inputs = []
        for subset in content_subsets:
            if subset:
                inputs.append(subset)
        embed_text_detail.inputs = inputs
        embed_text_detail.truncate = embed_text_detail.TRUNCATE_END
        embed_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.embed-english-v3.0")
        embed_text_detail.compartment_id = constants.compartment_ocid
        embed_text_detail.input_type = embed_text_detail.INPUT_TYPE_SEARCH_DOCUMENT

        try:
            embed_text_response = constants.generative_ai_inference_client.embed_text(embed_text_detail)
        except Exception as e:
            print("Error while creating embeddings ", e)
            embeddings = []
        else:
            embeddings = embed_text_response.data.embeddings
        print(len(inputs))
        for i in range(len(inputs)):
            insert_data(cursor, cursor_index, inputs[i], list(embeddings[i]), constants.webpage, org)
            cursor_index = cursor_index + 1
        start = start + 96
    connection.commit()
    cursor.close()
    connection.close()


def insert_data(cursor,id, chunk, vec, source_url, org):
    cursor.setinputsizes(None,4000, oracledb.DB_TYPE_VECTOR, 4000)
    try:  
        cursor.execute("insert into {org}_web_embeddings values (:1, :2, :3, :4)".format(org=org), [id,chunk,vec, source_url])
    except Exception as e:
        print("Error while inserting table and error is {e}".format( e=e))

if __name__ == "__main__":
    print("..")
    demo_user = constants.demo_user
    demo_passwd = constants.demo_passwd
    connection, dsn = database_connections.create_db_connection(demo_user, demo_passwd)
    # Below is an optional step. It is required if 3rd party providers are used for generating embeddings
    # create_connection_to_ocigenai(connection)
    create_table(connection,constants.org)
    # get chunked text
    organized_content = parse_and_chunk_url_text(constants.webpage)
    contents = []

    for chunk in organized_content:
        text = chunk.text
        text = clean(text, extra_whitespace=True)
        contents.append(text)
    
    create_knowledge_base_from_client_content(connection, constants.org, contents)

