from queue import Empty
import boto3
import json

import datetime
from datetime import date
import pandas as pd

# key = "AKIA3QOP2IUL5VZGRDKL"
# access = "O2WPw+aZ4jRUYsaDq2K7szEPzI5tk2Ud2G/qjcna"
# region = "ap-southeast-1"


usage_queue_url = "https://sqs.ap-southeast-1.amazonaws.com/791246685463/dra-infra-UsageRequestQueue-0CpzhgZvmYmj"
aggregate_queue_url = "https://sqs.ap-southeast-1.amazonaws.com/791246685463/dra-infra-AggregateRequestQueue-ApQgk1EaeSaD"

usage_data_bucket="dra-client-usage-data"
aggregate_data_bucket="dra-client-aggregate-data"

class DRAClient:  

    
    def __init__(self):
        self.sqs_client= boto3.client('sqs')
        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3') 
        self.allclients = ['CBI','BRI','BNI','CBQ']   
        self.df_usage = None
        self.df_aggregate = None


    def buildUsageData(self,client, month, year):
        req={'client_id':client, 'month':month, 'year':year}
        jsonReq = json.dumps(req)
        ret = self.sqs_client.send_message( QueueUrl=usage_queue_url, 
                                MessageBody=jsonReq)
    
    def buildAggregateData(self,client, month, year):
        req={'client_id':client, 'month':month, 'year':year}
        jsonReq = json.dumps(req)
        ret = self.sqs_client.send_message( QueueUrl=aggregate_queue_url, 
                                    MessageBody=jsonReq)

    def buildUsageDataAllClients(self,month,year):
        for c in self.allclients:
            self.buildUsageData(c, month, year)
            
    def buildAggregateDataAllClients(self,month,year):
        for c in self.allclients:
            self.buildAggregateData(c, month, year)

    def updateUsageAndAggregateExecutionStatus(self):

        self.df_usage = self._getPipelineExecutionStatusAsDataFrame(usage_data_bucket)
        self.df_aggregate = self._getPipelineExecutionStatusAsDataFrame(aggregate_data_bucket)

    def _getPipelineExecutionStatusAsDataFrame(self, bucket):

        data={}
        usage_files = self.s3_client.list_objects_v2(Bucket=bucket)
        print(usage_files)
        if (usage_files['KeyCount']>0):
            files_json = usage_files['Contents']
            for fi in files_json:
                tok = fi['Key'].split('@')
                period=tok[1]+'/'+ (tok[2].split('.'))[0]
                if tok[0] not in data.keys():

                    data[tok[0]]=[{period: fi['LastModified']}]        
                else:

                    data[tok[0]].append({period: fi['LastModified']})     
            index=[]
            dd=[]
            for client in data.keys():
                index.append(client)
                cd={}
                for v in data[client]:            
                    for k in v:
                        cd[k]=v[k]
                dd.append(cd)
            df = pd.DataFrame(dd, index=index)
            return df
        else:
            return {}


    def loadAggregateData(self, clientId, month, year):
        s3 = boto3.client('s3')
        key = clientId+"@"+str(month)+"@"+str(year)+".json"
        

        data = s3.get_object(Bucket=aggregate_data_bucket, Key=key)
        contents = data['Body'].read()
        return contents