
import oci
# string identifier
org = ""  
# Profile name in config file 
CONFIG_PROFILE = "DEFAULT"
# Location of the config file in compute instance
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
# Public IP address of database in step 2.7
host = ''
# Service name from step 2.6 
service_name = ''
# Gather this information from your tenancy
user_ocid='ocid1.user.oc1'
tenancy_ocid='ocid1.tenancy.oc1'
compartment_ocid='ocid1.compartment.oc1'
fingerprint = ''
# Webpage that you're interested in querying
webpage='https://en.wikipedia.org/wiki/Oracle_Corporation'
# Update these usernames and passwords
admin_username="SYSTEM"
admin_userpwd = ""****""

demo_user = "User"
demo_passwd = "****"



# Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"}


