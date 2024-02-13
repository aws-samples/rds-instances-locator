import boto3
import sys


# Since AZ Names are randomly mapped to AZ Ids per account, this maps the AZ Id to the AZ Name
def map_az_id_to_name(az_id, region):
    ec2 = boto3.client('ec2', region_name=region)
    az_name = ec2.describe_availability_zones(ZoneIds=[az_id])['AvailabilityZones'][0]['ZoneName']
    return az_name


# This function finds all the RDS Subnet Groups with at least 1 subnet in the specified AZ Id and returns a list of the Subnet Groups and the AZ Name
def find_subnet_groups_by_az_id(az_id, region):
    az_name = map_az_id_to_name(az_id, region)

    rds = boto3.client('rds', region_name=region)
    subnet_groups = rds.describe_db_subnet_groups()
    subnet_groups_by_az = []
    for sg in subnet_groups['DBSubnetGroups']:
        for subnet in sg['Subnets']:
            if az_name in subnet['SubnetAvailabilityZone']['Name']:
                subnet_groups_by_az.append(sg['DBSubnetGroupName'])
                break

    return subnet_groups_by_az, az_name



def main():
    azId = sys.argv[1]
    region_name = sys.argv[2]

    try:
        subnet_groups_in_az, az_name = find_subnet_groups_by_az_id(azId, region_name)
    except:
        print('Error finding the specified AZ '+ azId + ' in ' + region_name) 
        return
    
    dbs_csv = open('rds_instances_in_az.csv', 'w')
    row = 'DBSubnetGroupName, DBInstanceIdentifier,DBInstanceClass,Engine,DBInstanceStatus,AvailabilityZone,MultiAZ,SecondaryAvailabilityZone\n'
    dbs_csv.write(row)

    rds = boto3.client('rds', region_name=region_name)

    instance_list = rds.describe_db_instances()['DBInstances']
    for instance in instance_list:
        row = '' 

        if instance['DBSubnetGroup']['DBSubnetGroupName'] in subnet_groups_in_az:
            
            # Single-AZ DB Instance in the specified AZ
            if instance['AvailabilityZone'] == az_name and instance['MultiAZ'] == False:
                row = instance['DBSubnetGroup']['DBSubnetGroupName']+ ',' + instance['DBInstanceIdentifier'] + ',' + instance['DBInstanceClass'] + ',' + instance['Engine'] + ',' + instance['DBInstanceStatus'] + ',' + instance['AvailabilityZone'] + ',' + str(instance['MultiAZ']) + ',' + 'None' + '\n'
            
            # Multi-AZ DB Instance with primary node in the specified AZ
            if instance['AvailabilityZone'] == az_name and instance['MultiAZ'] == True:
                if instance['AvailabilityZone'] == az_name:
                    row = instance['DBSubnetGroup']['DBSubnetGroupName']+ ',' + instance['DBInstanceIdentifier'] + ',' + instance['DBInstanceClass'] + ',' + instance['Engine'] + ',' + instance['DBInstanceStatus'] + ',' + instance['AvailabilityZone'] + ',' + str(instance['MultiAZ']) + ',' + instance['SecondaryAvailabilityZone'] + '\n'
            
            # Multi-AZ DB Instance with secondary node in the specified AZ
            if instance['AvailabilityZone'] != az_name and instance['MultiAZ'] == True:
                if instance['SecondaryAvailabilityZone'] == az_name:
                    row = instance['DBSubnetGroup']['DBSubnetGroupName']+ ',' + instance['DBInstanceIdentifier'] + ',' + instance['DBInstanceClass'] + ',' + instance['Engine'] + ',' + instance['DBInstanceStatus'] + ',' + instance['AvailabilityZone'] + ',' + str(instance['MultiAZ']) + ',' + instance['SecondaryAvailabilityZone'] + '\n'

        dbs_csv.write(row)
    dbs_csv.close()      

if __name__ == "__main__":
    main()