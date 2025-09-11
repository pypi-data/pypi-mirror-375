<div align="center">
  <img src="https://i.imgur.com/bwBBG4X.jpg"><br>
</div>


# tetsu: a Python toolkit containing helper scripts

**tetsu** (short for *tetsudai* in Japanese, meaning helper) is a Python package that consolidates all of the DS&E's helper scripts into one package for easy use across projects. The broader goal is to remove blockers and turnaround time for spinning up projects.

## Background

## Installation
To install from your terminal:
```
pip install tetsu
```


## Getting Started
tetsu currently supports helpers for the following services: Cloudant, Box, Cloud Object Storage (COS), Mime, DB2, TM1 cubes, and logger.
These helpers currently fall under two umbrellas: 
1. Class-based helpers (Box, COS, DB2)
2. Class-less helpers (Cloudant, Mime, logger, TM1)

Each service has a different helper to go along with it. There will be specific examples for each helper
in the usage section

# Usage 
You'll only need to call the cloudant helper **once** in your project. 
By default, the document you call will be stored as an environment variable and will be used for all functions in Tetsu moving forward. 
In the event you would like to use credentials from a different document, you can pass the new cloudant document as an argument in any of the Tetsu functions. 

## Class-less helpers

### cloudant_helper
```python
import os 
import tetsu as ts 

doc = ts.cloudant_helper.get_document(document_id='dsc-finds2',
                                      cloudant_api_key=os.getenv('CLOUDANT_IAM_API_KEY'))
```
### mime_helper
```python
import tetsu as ts

ts.mime_helper.send_message(sender_email='john.doe@ibm.com',
                            receiver_email='jane.doe@ibm.com',
                            subject='MIME Example',
                            message_body='This is how you send an email using tetsu')
```
### log_helper
```python
import tetsu as ts

logger = ts.log_helper.logger(name=__name__,
                              handler='console')
```
### tm1_helper
```python
import tetsu as ts 

# pull data using an MDX query
example_mdx = open("config/incur_expense.txt", 'r').read()

df = ts.tm1_helper.tm1_pull(mdx_query=example_mdx, 
                            environment='prod', 
                            cube='ibmpsend')

# push data to a TM1 cube
ts.tm1_helper.tm1_push(df=df, 
                       environment='uat', 
                       cube='ibmplanning')
```

## Class-based helpers

### db2_helper

```python 
import tetsu as ts

# In this example, Db2Helper will use the previously pulled FINDS2 credentials and the deployment environment used here is staging
db2_conn = ts.DB2Helper(environment='staging',
                        driver='ODBC')  # default is ODBC 

df = db2_conn.db2_pull("SELECT * from EPM.DIM_GEOGRAPHY LIMIT 10")
```
### Overriding the default arguments
Let's say you want to override the cloudant document and the specific parameters pulled from Cloudant. In this example, we want to specifically create a db2 connection using FINDS1 credentials. 
For the `creds` argument you need to construct a dictionary that references the path of your credentials within the cloudant document. 

For example, to search for a parameter called username, we know to find that in our document under `staging`, `db2`, `username`. Our search list will then become `['staging', 'db2','username']`.

```python 
import tetsu as ts

# in this example, we'll use csgm-finds1 and the deployment environment used here is staging
# the creds argument is a dictionary that contains each of the parameters you need to successfully initiate a Db2 connection
# in this example, the assumption is you need an additional parameter (trustpass) from your db2 credentials in cloudant
doc = ts.cloudant_helper.get_document(document_id='csgm-finds1',
                                      cloudant_api_key=os.getenv('CLOUDANT_IAM_API_KEY'),
                                      save_env=False # If you want the doc in the environment to be updated set to True)

db2_conn = ts.DB2Helper(cloudant_doc='csgm-finds1',
                        environment='staging',
                        driver='ODBC',
                        creds = {"username": ['staging', 'db2', 'username'],
                                "password": ['staging', 'db2', 'password'],
                                "hostname": ['staging', 'db2', 'hostname'],
                                "port": ['staging', 'db2', 'port'],
                                "database": ['staging', 'db2', 'database'],
                                "trustpass": ['staging', 'db2', 'trustpass']})  

df = db2_conn.db2_pull("SELECT * from EPM.DIM_GEOGRAPHY LIMIT 10")
```
### cos_helper
```python
import tetsu as ts 

cos_conn = ts.COSHelper(environment='COS_FINDS', 
                        cos_bucket='ces-expense-forecasting')

cos_conn.upload_file(files_list=['data/test.csv','data/test2.csv'])
```
### box_helper

```python
import tetsu as ts
import pandas as pd

doc = ts.cloudant_helper.get_document(document_id='csgm-finds1',
                                      cloudant_api_key=os.getenv('CLOUDANT_IAM_API_KEY'),
                                      save_env=False # If you want the doc in the environment to be updated set to True)

db2_conn = ts.DB2Helper(cloudant_doc='csgm-finds1',
                        environment='staging',
                        driver='ODBC',
                        creds = {"username": ['staging', 'db2', 'username'],
                                "password": ['staging', 'db2', 'password'],
                                "hostname": ['staging', 'db2', 'hostname'],
                                "port": ['staging', 'db2', 'port'],
                                "database": ['staging', 'db2', 'database'],
                                "trustpass": ['staging', 'db2', 'trustpass']})  
# Standard method to connect 
box_conn = ts.BoxHelper(doc)

# Using a local JWTAuth JSON file
box_conn = ts.BoxHelper(path='local/path/to/JWTAuth/Json/file')

# Upload a box file 
df = pd.DataFrame([[1,2,3], [4,5,6]])
box_conn.upload_df(data=df,
                      path='path/to/local-dir/where/df/should/be/saved',
                      folder_id='box_folder_id',
                      file_type='csv')

```

# Contributing to tetsu

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome through pull requests.
To submit a PR, just create your own branch with a naming convention of `issue_being_fixed-initialsdev`. For example, if Hassan
was trying to add methods to the cloudant helper, the branch could be named `upgrade_cloudant_helper-hkdev`. Once you have updated the code,
create a PR into main and assign both Rahul and Hassan as reviewers. 

**Please consider creating a github issue to go along with any formal development.**
