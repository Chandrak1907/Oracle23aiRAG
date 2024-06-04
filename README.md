Generative AI has big impact on how enterprises conduct business. Oracle offers multiple products to build a Gen AI application such as retrieval augmented generation (RAG).
Here is the sample [notebook](https://github.com/langchain-ai/langchain/blob/master/cookbook/oracleai_demo.ipynb) on langchain and a [blog](https://blogs.oracle.com/ai-and-datascience/post/how-to-build-a-rag-solution-using-oci-generative-ai) that explains how RAG solution can be implemented using Oracle's new database offering Oracle23ai to store embedding vectors.

If you are new to Oracle23ai, there are chances that you might encounter issues connecting to database using python. This documentation provides step-by-step procedure to implement the RAG solution using python3.9 to extract & store the contents of a webpage and create embeddings to store in oracle23ai. 

1. Login to Oracle cloud using the credentials provided by the adminstrator
2. Provision an Click on menu on top left - Oracle Database - and select "Oracle Base Database"
    
    2.1 In 'DB System Information' page, you'll be asked select shape, storage, to add/generate/paste SSH Keys and create/select VCN
    
    2.2 In 'Database information' page, Click 'Database image' and select version '23ai'
    
    2.3 Once Database is provisioned, click on the Database provisioned in 'Databases' secton (Overview Oracle Base Database -> DB Systems -> DB System Details)
    
    2.4 Click on Pluggable Databases. Read more about difference between Container Database (CDB) and Pluggable Database [here](https://docs.oracle.com/en/database/oracle/oracle-database/21/cncpt/CDBs-and-PDBs.html#GUID-C3B11701-F23A-4781-91EE-C907F0AF2527)
    
    2.5 Select 'DB Connection' 
    
    2.6 Copy the  'Connection String' from 'Easy Connect' Format to a notepad or text editor and keep it handy. ![Screenshot is here](/Documentation/image001.png)

    2.7 Navigate to Oracle Base Database -> DB Systems -> DB System Details -> Nodes, copy the 'Public IP address' to a notepad or text editor and keep it handy. ![Screenshot is here](/Documentation/image002.png)

    


3. If you're using a mac, there are limitations to connect to Oracle23ai database. So, recommend you to provision a [Linux compute instance](https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/launchinginstance.htm) 

4. [Install miniconda in this compute instance](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

5. Create a python environment for python version 3.9 or later. Below command will create a python environment named py39 using the environment.yml file located [here](./code/environment.yml)

    ``` conda env create -f environment.yml ```

6. Download Oracle InstantClient Basic for Linux x86-64 from https://download.oracle.com/otn_software/linux/instantclient/2340000/instantclient-basic-linux.x64-23.4.0.24.05.zip

    ``` curl https://download.oracle.com/otn_software/linux/instantclient/2340000/instantclient-basic-linux.x64-23.4.0.24.05.zip --output instantclient.zip ```
7. Unzip it in an opt directory using sudo
    ```
    sudo mkdir -p /opt/oracle  
    cd /opt/oracle  
    sudo unzip /opt/oracle/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip 
    ```

8. Install a linux package libaio1 

    ``` sudo apt-get install libaio1 ```
9.  Add the path the  external variable LD_LIBRARY_PATH by adding below line to .bashrc file

    ```  export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_8:$LD_LIBRARY_PATH  ```
10. After saving the .bashrc file, source it:
    ```source ~/.bashrc ```

11. Follow steps in this [link](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstallhtm#InstallingCLI__oraclelinux8) and install python-cli 

12. Create a config file using ```oci setup config```

13. Update VCN to allow traffic through ports 1521 and 9200. This is required to connect to 23ai Database.

14. Update 'constants.py' file in 'code' folder with all required information

15. Run 'python code/create_user.py' to create non-admin user in the database

16. Run 'python code/create_embeddings.py' to create embeddings of the webpage that you want to index

17. Run 'python code/generate_answers.py' to generate answers to your question