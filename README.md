# RDS Instances locator

There are times when you want to know exactly in which physical AZ your RDS instances are running.

### Single Account
When you want to identify RDS instances by AZ Id in a single account, you might want to use some of the following approaches:
- locally run a script that calls the RDS API to describe your resources, such as the one provided under `/local python script`

- apply a [Custom Config Rule](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules.html) which evaluates if your RDS instances run in an [Availiability Zone](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) specified by its [ID](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html). 


### Multiple Accounts
AWS [maps](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html) the physical Availability Zones randomly to the Availability Zone names for each AWS account.
You might want to know which RDS Instances run in a specified AZ across different accounts. In this case the CloudFormation template provided can be deployed across accounts using [CloudFormation StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html) with no modifications.
The [Custom Config Rule](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules.html) will evaluate if your RDS instances run in the [Availiability Zone](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) specified by its [ID](https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html). 

---

### Local python script

#### Prerequisites:
- [AWS SDK for Python](https://aws.amazon.com/sdk-for-python/)

```
pip install boto3
```

- AWS credentials with permissions to call:
```
- rds:DescribeDBSubnetGroups
- rds:DescribeDBInstances
- ec2:DescribeAvailabilityZones
```

#### Usage
1. Execute the script with the following command:
```
python3 path/to/find_rds_instances_in_subnet.py <az-id> <region-code>
```

for example if you want to check which instances run in AZ `use1-az1` you will run:
```
python3 path/to/find_rds_instances_in_subnet.py use1-az1 us-east-1
```
the script will output a CSV file in the current working directory

### Custom Config Rule
The CloudFormation template provided under `/custom config rule cloudformation` creates the rule for you.

#### Prerequisites:
1. AWS Config enabled in the region and accounts you want to deploy the rule to

#### Deployment:
1. Open the [CloudFormation Stacks console](https://console.aws.amazon.com/cloudformation/home) in the region in which you want to check the location of RDS Instances
2. Select **Create Stack** -> "With new resources (standard)"
3. Select **Template is ready** under **Prerequisite - Prepare template**
4. Select **Upload a template file** under **Specify template**
5. Click **Next**
6. Enter a Stack name under **Stack name**
7. Enter the Id of the Availability Zone you want to specify under **AZId** and click **Next**
8. Keep everything as default on the next page
9. Review settings and select the checkbox **I aknowledge  that AWS CloudFormation might create IAM resources with custom names.**
10. Click **Submit**

The Custom Config Rule `RDSAZConfigRule` will be created and will start evaluating resources

**Note**: RDS instances running in the specified AZ will be marked as NON_COMPLIANT. 

### Deploy the Custom Config Rule across multiple accounts
#### Prerequisites
Review prerequisites on the [CloudFormation user documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs.html)

#### Deployment

1. Open the [CloudFormation StackSet console](https://console.aws.amazon.com/cloudformation/home/stacksets)
2. Select **Create new StackSet**
3. Depending on the permission model you might need to change the default permissions
4. Select **Template is ready** under **Prerequisite - Prepare template**
5. Select **Upload a template file** under **Specify template**
6. Click **Next**
7. Enter a StackSet name under **StackSet name**
8. Optionally enter a description for the StackSet under **StackSet description**
9. Enter the Id of the Availability Zone you want to specify under **AZId** and click **Next**
10. Keep StackSet Options defaults on this page and click **Next**
11. Under **Deployment options** select **Deploy new stacks**
12. Specify the accounts you want to deploy the stacks to or the OU IDs in your AWS Organization
13. Under **Specify regions** select the region that contains the AZ you specified on Step 9
14. Select the **Deployment options** that best fit your needs and click **Next**
15. Review settings and select the checkbox **I aknowledge  that AWS CloudFormation might create IAM resources with custom names.**
16. Click **Submit**

The Custom Config Rule `RDSAZConfigRule` will be created in all accounts specified and will start evaluating resources. You can use an [AWS Config Aggregator](https://docs.aws.amazon.com/config/latest/developerguide/aggregate-data.html) to aggregate results in a single account for review.

**Note**: RDS instances running in the specified AZ will be marked as NON_COMPLIANT. 