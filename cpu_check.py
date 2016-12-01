import boto3
import datetime
'''Making a comment to test AWS CodeBuild. '''
print('Loading function')

now = datetime.datetime.utcnow()


def lambda_handler(event, context):

    def RegionList():
        regionList = []
        client = boto3.client('ec2')
        getRegions = client.describe_regions()
        for region in getRegions['Regions']:
            if region['RegionName'] not in regionList:
                regionList.append(region['RegionName'])
        return regionList

    regions = RegionList()

    def getInstances(regions):
        instanceList = []
        for region in regions:
            client = boto3.client('ec2', region_name=region)
            get_instances = client.describe_instances()
            for instance in get_instances['Reservations']:
                for instanceid in instance['Instances']:
                    if instanceid['InstanceId'] not in instanceList:
                        instanceList.append(instanceid['InstanceId'])
        return instanceList

    things = getInstances(regions)

    def cw_metrics(instance_list):
        client = boto3.client('cloudwatch')
        s3_client = boto3.client('s3')
        timer = now - datetime.timedelta(minutes=30)
        for instance in instance_list:
            get_cw = client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                StartTime=timer,
                EndTime=now,
                Period=300,
                Statistics=['Average'],
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance
                        }
                    ]
                )

            with open('/tmp/%s%s.json' % (now, instance), 'w+') as f:
                f.write(str(get_cw['Datapoints']))

            with open('/tmp/%s%s.json' % (now, instance), 'r') as data_f:
                json_stuff = data_f.read()
                s3_client.put_object(Bucket='examplebucket', Body=json_stuff,
                                     Key='%s%s.json' % (now, instance))
    cw_metrics(things)
