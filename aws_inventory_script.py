#!/usr/bin/env python3
"""
AWS Resource Inventory Script for Account Migration Planning
Discovers and categorizes AWS resources by application ownership using tags.
"""

import boto3
import json
import csv
from collections import defaultdict
from datetime import datetime
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AWSResourceInventory:
    def __init__(self, region='us-east-1', profile=None):
        """Initialize AWS session and clients"""
        try:
            if profile:
                session = boto3.Session(profile_name=profile)
            else:
                session = boto3.Session()
            
            self.region = region
            self.session = session
            self.clients = {}
            self.inventory = defaultdict(list)
            
            # Tag keys to check for application ownership (customize these)
            self.app_tag_keys = ['Application', 'App', 'application', 'app', 'Project', 'project']
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS session: {e}")
            raise

    def get_client(self, service):
        """Get or create boto3 client for a service"""
        if service not in self.clients:
            self.clients[service] = self.session.client(service, region_name=self.region)
        return self.clients[service]

    def extract_app_name(self, tags):
        """Extract application name from resource tags"""
        if not tags:
            return 'untagged'
        
        for tag in tags:
            if isinstance(tag, dict):
                key = tag.get('Key', '')
                value = tag.get('Value', '')
            else:
                # Handle different tag formats
                continue
                
            if key in self.app_tag_keys and value:
                return value.lower().replace(' ', '-')
        
        return 'untagged'

    def inventory_lambda_functions(self):
        """Inventory Lambda functions"""
        logger.info("Inventorying Lambda functions...")
        try:
            lambda_client = self.get_client('lambda')
            paginator = lambda_client.get_paginator('list_functions')
            
            for page in paginator.paginate():
                for func in page['Functions']:
                    try:
                        # Get function tags
                        tags_response = lambda_client.list_tags(Resource=func['FunctionArn'])
                        tags = [{'Key': k, 'Value': v} for k, v in tags_response.get('Tags', {}).items()]
                        
                        app_name = self.extract_app_name(tags)
                        
                        resource_info = {
                            'service': 'Lambda',
                            'resource_type': 'Function',
                            'name': func['FunctionName'],
                            'arn': func['FunctionArn'],
                            'app_name': app_name,
                            'runtime': func.get('Runtime', 'Unknown'),
                            'memory': func.get('MemorySize', 0),
                            'timeout': func.get('Timeout', 0),
                            'last_modified': func.get('LastModified', ''),
                            'tags': tags
                        }
                        
                        self.inventory[app_name].append(resource_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing Lambda function {func['FunctionName']}: {e}")
                        
        except Exception as e:
            logger.error(f"Error inventorying Lambda functions: {e}")

    def inventory_rds_instances(self):
        """Inventory RDS instances and clusters"""
        logger.info("Inventorying RDS instances...")
        try:
            rds_client = self.get_client('rds')
            
            # RDS Instances
            paginator = rds_client.get_paginator('describe_db_instances')
            for page in paginator.paginate():
                for db in page['DBInstances']:
                    try:
                        # Get DB tags
                        tags_response = rds_client.list_tags_for_resource(ResourceName=db['DBInstanceArn'])
                        tags = tags_response.get('TagList', [])
                        
                        app_name = self.extract_app_name(tags)
                        
                        resource_info = {
                            'service': 'RDS',
                            'resource_type': 'DB Instance',
                            'name': db['DBInstanceIdentifier'],
                            'arn': db['DBInstanceArn'],
                            'app_name': app_name,
                            'engine': db.get('Engine', 'Unknown'),
                            'instance_class': db.get('DBInstanceClass', 'Unknown'),
                            'status': db.get('DBInstanceStatus', 'Unknown'),
                            'allocated_storage': db.get('AllocatedStorage', 0),
                            'tags': tags
                        }
                        
                        self.inventory[app_name].append(resource_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing RDS instance {db['DBInstanceIdentifier']}: {e}")
            
            # RDS Clusters
            paginator = rds_client.get_paginator('describe_db_clusters')
            for page in paginator.paginate():
                for cluster in page['DBClusters']:
                    try:
                        tags_response = rds_client.list_tags_for_resource(ResourceName=cluster['DBClusterArn'])
                        tags = tags_response.get('TagList', [])
                        
                        app_name = self.extract_app_name(tags)
                        
                        resource_info = {
                            'service': 'RDS',
                            'resource_type': 'DB Cluster',
                            'name': cluster['DBClusterIdentifier'],
                            'arn': cluster['DBClusterArn'],
                            'app_name': app_name,
                            'engine': cluster.get('Engine', 'Unknown'),
                            'status': cluster.get('Status', 'Unknown'),
                            'tags': tags
                        }
                        
                        self.inventory[app_name].append(resource_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing RDS cluster {cluster['DBClusterIdentifier']}: {e}")
                        
        except Exception as e:
            logger.error(f"Error inventorying RDS resources: {e}")

    def inventory_dynamodb_tables(self):
        """Inventory DynamoDB tables"""
        logger.info("Inventorying DynamoDB tables...")
        try:
            dynamodb_client = self.get_client('dynamodb')
            paginator = dynamodb_client.get_paginator('list_tables')
            
            for page in paginator.paginate():
                for table_name in page['TableNames']:
                    try:
                        # Get table details
                        table_response = dynamodb_client.describe_table(TableName=table_name)
                        table = table_response['Table']
                        
                        # Get table tags
                        tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=table['TableArn'])
                        tags = tags_response.get('Tags', [])
                        
                        app_name = self.extract_app_name(tags)
                        
                        resource_info = {
                            'service': 'DynamoDB',
                            'resource_type': 'Table',
                            'name': table_name,
                            'arn': table['TableArn'],
                            'app_name': app_name,
                            'status': table.get('TableStatus', 'Unknown'),
                            'item_count': table.get('ItemCount', 0),
                            'table_size_bytes': table.get('TableSizeBytes', 0),
                            'tags': tags
                        }
                        
                        self.inventory[app_name].append(resource_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing DynamoDB table {table_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Error inventorying DynamoDB tables: {e}")

    def inventory_s3_buckets(self):
        """Inventory S3 buckets"""
        logger.info("Inventorying S3 buckets...")
        try:
            s3_client = self.get_client('s3')
            response = s3_client.list_buckets()
            
            for bucket in response['Buckets']:
                try:
                    bucket_name = bucket['Name']
                    
                    # Get bucket tags
                    try:
                        tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
                        tags = tags_response.get('TagSet', [])
                    except s3_client.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == 'NoSuchTagSet':
                            tags = []
                        else:
                            raise
                    
                    app_name = self.extract_app_name(tags)
                    
                    # Get bucket location
                    try:
                        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                        location = location_response.get('LocationConstraint', 'us-east-1')
                        if location is None:
                            location = 'us-east-1'
                    except:
                        location = 'Unknown'
                    
                    resource_info = {
                        'service': 'S3',
                        'resource_type': 'Bucket',
                        'name': bucket_name,
                        'arn': f"arn:aws:s3:::{bucket_name}",
                        'app_name': app_name,
                        'creation_date': bucket['CreationDate'].isoformat(),
                        'region': location,
                        'tags': tags
                    }
                    
                    self.inventory[app_name].append(resource_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing S3 bucket {bucket_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error inventorying S3 buckets: {e}")

    def inventory_ec2_instances(self):
        """Inventory EC2 instances"""
        logger.info("Inventorying EC2 instances...")
        try:
            ec2_client = self.get_client('ec2')
            paginator = ec2_client.get_paginator('describe_instances')
            
            for page in paginator.paginate():
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        try:
                            tags = instance.get('Tags', [])
                            app_name = self.extract_app_name(tags)
                            
                            resource_info = {
                                'service': 'EC2',
                                'resource_type': 'Instance',
                                'name': instance['InstanceId'],
                                'arn': f"arn:aws:ec2:{self.region}:{instance.get('OwnerId', 'unknown')}:instance/{instance['InstanceId']}",
                                'app_name': app_name,
                                'instance_type': instance.get('InstanceType', 'Unknown'),
                                'state': instance.get('State', {}).get('Name', 'Unknown'),
                                'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else '',
                                'tags': tags
                            }
                            
                            self.inventory[app_name].append(resource_info)
                            
                        except Exception as e:
                            logger.warning(f"Error processing EC2 instance {instance.get('InstanceId', 'unknown')}: {e}")
                            
        except Exception as e:
            logger.error(f"Error inventorying EC2 instances: {e}")

    def inventory_apigateway_apis(self):
        """Inventory API Gateway APIs"""
        logger.info("Inventorying API Gateway APIs...")
        try:
            # REST APIs
            apigw_client = self.get_client('apigateway')
            paginator = apigw_client.get_paginator('get_rest_apis')
            
            for page in paginator.paginate():
                for api in page['items']:
                    try:
                        # Get API tags
                        tags_response = apigw_client.get_tags(resourceArn=f"arn:aws:apigateway:{self.region}::/restapis/{api['id']}")
                        tags = [{'Key': k, 'Value': v} for k, v in tags_response.get('tags', {}).items()]
                        
                        app_name = self.extract_app_name(tags)
                        
                        resource_info = {
                            'service': 'API Gateway',
                            'resource_type': 'REST API',
                            'name': api['name'],
                            'arn': f"arn:aws:apigateway:{self.region}::/restapis/{api['id']}",
                            'app_name': app_name,
                            'api_id': api['id'],
                            'created_date': api.get('createdDate', '').isoformat() if api.get('createdDate') else '',
                            'tags': tags
                        }
                        
                        self.inventory[app_name].append(resource_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing API Gateway API {api.get('name', 'unknown')}: {e}")
            
            # HTTP APIs (API Gateway v2)
            apigwv2_client = self.get_client('apigatewayv2')
            paginator = apigwv2_client.get_paginator('get_apis')
            
            for page in paginator.paginate():
                for api in page['Items']:
                    try:
                        app_name = self.extract_app_name(api.get('Tags', {}))
                        
                        resource_info = {
                            'service': 'API Gateway v2',
                            'resource_type': 'HTTP API',
                            'name': api['Name'],
                            'arn': f"arn:aws:apigateway:{self.region}::/apis/{api['ApiId']}",
                            'app_name': app_name,
                            'api_id': api['ApiId'],
                            'protocol_type': api.get('ProtocolType', 'Unknown'),
                            'created_date': api.get('CreatedDate', '').isoformat() if api.get('CreatedDate') else '',
                            'tags': [{'Key': k, 'Value': v} for k, v in api.get('Tags', {}).items()]
                        }
                        
                        self.inventory[app_name].append(resource_info)
                        
                    except Exception as e:
                        logger.warning(f"Error processing API Gateway v2 API {api.get('Name', 'unknown')}: {e}")
                        
        except Exception as e:
            logger.error(f"Error inventorying API Gateway APIs: {e}")

    def run_inventory(self):
        """Run complete inventory of AWS resources"""
        logger.info(f"Starting AWS resource inventory for region: {self.region}")
        
        # Run inventory for each service
        self.inventory_lambda_functions()
        self.inventory_rds_instances()
        self.inventory_dynamodb_tables()
        self.inventory_s3_buckets()
        self.inventory_ec2_instances()
        self.inventory_apigateway_apis()
        
        logger.info("Inventory complete!")
        return dict(self.inventory)

    def generate_reports(self, output_dir='./'):
        """Generate inventory reports in multiple formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON Report
        json_file = f"{output_dir}/aws_inventory_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(dict(self.inventory), f, indent=2, default=str)
        logger.info(f"JSON report saved to: {json_file}")
        
        # CSV Report
        csv_file = f"{output_dir}/aws_inventory_{timestamp}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['App Name', 'Service', 'Resource Type', 'Resource Name', 'ARN', 'Additional Info'])
            
            for app_name, resources in self.inventory.items():
                for resource in resources:
                    additional_info = {k: v for k, v in resource.items() 
                                     if k not in ['service', 'resource_type', 'name', 'arn', 'app_name', 'tags']}
                    writer.writerow([
                        app_name,
                        resource['service'],
                        resource['resource_type'],
                        resource['name'],
                        resource['arn'],
                        json.dumps(additional_info, default=str)
                    ])
        logger.info(f"CSV report saved to: {csv_file}")
        
        # Summary Report
        summary_file = f"{output_dir}/aws_inventory_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("AWS Resource Inventory Summary\n")
            f.write("=" * 40 + "\n\n")
            
            total_resources = 0
            for app_name, resources in sorted(self.inventory.items()):
                f.write(f"Application: {app_name}\n")
                f.write("-" * 30 + "\n")
                
                service_counts = defaultdict(int)
                for resource in resources:
                    service_counts[resource['service']] += 1
                    total_resources += 1
                
                for service, count in sorted(service_counts.items()):
                    f.write(f"  {service}: {count} resources\n")
                f.write(f"  Total: {len(resources)} resources\n\n")
            
            f.write(f"OVERALL TOTAL: {total_resources} resources across {len(self.inventory)} applications\n")
        
        logger.info(f"Summary report saved to: {summary_file}")
        
        return {
            'json_file': json_file,
            'csv_file': csv_file,
            'summary_file': summary_file
        }

def main():
    parser = argparse.ArgumentParser(description='AWS Resource Inventory Tool')
    parser.add_argument('--region', default='us-east-1', help='AWS region to scan')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--output-dir', default='./', help='Output directory for reports')
    
    args = parser.parse_args()
    
    try:
        # Create inventory instance
        inventory = AWSResourceInventory(region=args.region, profile=args.profile)
        
        # Run inventory
        results = inventory.run_inventory()
        
        # Generate reports
        files = inventory.generate_reports(args.output_dir)
        
        # Print summary
        print(f"\nInventory completed successfully!")
        print(f"Found {sum(len(resources) for resources in results.values())} resources across {len(results)} applications")
        print(f"\nReports generated:")
        for report_type, filepath in files.items():
            print(f"  {report_type}: {filepath}")
            
    except Exception as e:
        logger.error(f"Inventory failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
