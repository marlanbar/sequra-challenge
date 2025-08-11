output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "ID of the private subnet used by Redshift/ECS"
  value       = aws_subnet.private.id
}

# Redshift
output "redshift_endpoint" {
  description = "JDBC endpoint of the Redshift cluster"
  value       = aws_redshift_cluster.redshift_cluster.endpoint
}

output "redshift_cluster_id" {
  description = "Identifier of the Redshift cluster"
  value       = aws_redshift_cluster.redshift_cluster.cluster_identifier
}

output "redshift_database" {
  description = "Default database name created in the cluster"
  value       = aws_redshift_cluster.redshift_cluster.database_name
}

# S3 (raw)
output "raw_bucket_name" {
  description = "Name of the S3 bucket for raw/staging data"
  value       = aws_s3_bucket.raw.bucket
}