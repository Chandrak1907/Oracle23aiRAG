import oracledb
import sys
import oci
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean
import constants
import database_connections
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_23_4")


# Perform RAG
import array
def answer_user_question(db_connection, org, query):
    question_list = []
    question_list.append(query)
    embed_text_response = generate_embeddings_for_question(question_list)
    question_vector = embed_text_response.data.embeddings[0]
    question_vector = array.array('f', question_vector)
    cursor = db_connection.cursor()
    list_dict_docs = []
    #query vector db to search relevant records
    similar_docs = search_data(cursor, [question_vector], list_dict_docs, org=org)
    context_documents = []
    relevant_doc_ids = []
    similar_docs_subset=[]

    
    for result in similar_docs:
        doc_data = result.doc_text
        context_documents.append(doc_data)
        relevant_doc_ids.append(doc_data.split(":")[0])

    for docs in similar_docs:
        current_id = str(docs.doc_id)
        if current_id in relevant_doc_ids:
            similar_docs_subset.append(docs)

    context_document = "\n".join(context_documents)
    prompt_template = '''
    Text: {documents} \n
    Question: {question} \n
    Answer the question based on the text provided and also return the relevant document numbers where you found the answer.
    If the text doesn't contain the answer, reply that the answer is not available.
    '''

    prompt = prompt_template.format(question = query, documents = context_document)
    llm_response_result = query_llm_with_prompt(prompt)
    response = {}
    response['message'] = query
    response['text'] = llm_response_result
    response['documents'] = [{'id': doc.doc_id, 'snippet': doc.doc_text, 'url': doc.url } for doc in similar_docs_subset]
    print(" ============== ")
    print(response)
    print(" ********** ")
    return response

def generate_embeddings_for_question(question_list):
    embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
    embed_text_detail.inputs = question_list
    embed_text_detail.input_type = embed_text_detail.INPUT_TYPE_SEARCH_QUERY
    embed_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.embed-english-v3.0")
    embed_text_detail.compartment_id = constants.compartment_ocid
    embed_text_response = constants.generative_ai_inference_client.embed_text(embed_text_detail)
    return embed_text_response


# Find relevant records from Oracle Vector DB using Dot Product similarity.
def search_data(cursor, query_vec, list_dict_docs, org):
    relevant_docs = []
    cursor.setinputsizes(oracledb.DB_TYPE_VECTOR)
    cursor.execute( """
        select *
        from {org}_web_embeddings
        order by vector_distance(vec, :1, DOT) fetch first 10 rows only
        """.format(org=org),query_vec)

    for row in cursor:
        id = row[0]
        text = row[1]
        url = row[3]
        temp_dict = {id:text}
        list_dict_docs.append(temp_dict)
        doc = Document(id, text, url)
        relevant_docs.append(doc)
    return relevant_docs

class Document():
      doc_id: int
      doc_text: str
      url: str
      def __init__(self, id, text, url) -> None:
            self.doc_id = id
            self.doc_text = text
            self.url = url

def query_llm_with_prompt(prompt):
    cohere_generate_text_request = oci.generative_ai_inference.models.CohereLlmInferenceRequest()
    cohere_generate_text_request.prompt = prompt
    cohere_generate_text_request.is_stream = False
    cohere_generate_text_request.max_tokens = 1000
    cohere_generate_text_request.temperature = 0
    cohere_generate_text_request.top_k = 0
    cohere_generate_text_request.top_p = 0
    generate_text_detail = oci.generative_ai_inference.models.GenerateTextDetails()
    generate_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.command")
    generate_text_detail.compartment_id = constants.compartment_ocid
    generate_text_detail.inference_request = cohere_generate_text_request
    generate_text_response = constants.generative_ai_inference_client.generate_text(generate_text_detail)
    llm_response_result = generate_text_response.data.inference_response.generated_texts[0].text
    return llm_response_result


if __name__ == "__main__":
    print("..")
    demo_user = constants.demo_user
    demo_passwd = constants.demo_passwd
    connection, dsn = database_connections.create_db_connection(demo_user, demo_passwd)

    query = "Who founded Oracle?"
    print(answer_user_question(connection, constants.org, query)['text'])