provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false
}

data "aws_availability_zones" "available" {}

resource "aws_security_group" "redshift_sg" {
  name        = "redshift-sg"
  description = "Allow Redshift access"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# S3 Bucket for raw data
resource "aws_s3_bucket" "raw" {
  bucket = var.raw_bucket_name
}

# IAM Role for Redshift with S3 access
resource "aws_iam_role" "redshift_s3_role" {
  name = "redshift-s3-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "redshift.amazonaws.com" },
      Action   = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "redshift_s3_read_attach" {
  role       = aws_iam_role.redshift_s3_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_redshift_subnet_group" "redshift_subnet_group" {
  name       = "redshift-subnet-group"
  subnet_ids = [aws_subnet.private.id]
}

resource "aws_redshift_cluster" "redshift_cluster" {
  cluster_identifier = "spaceX-redshift-cluster"
  database_name      = "spacex"
  master_username    = var.redshift_username
  master_password    = var.redshift_password
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  port               = 5439
  publicly_accessible = false

  vpc_security_group_ids = [aws_security_group.redshift_sg.id]
  subnet_group_name      = aws_redshift_subnet_group.redshift_subnet_group.name
  iam_roles              = [aws_iam_role.redshift_s3_role.arn]
}

variable "aws_region" {
  default = "us-east-1"
}

variable "redshift_username" {
  default     = "adminuser"
}

variable "redshift_password" {
  default     = "SuperSecret123!"
}

variable "allowed_ip_cidr" {
  default     = "0.0.0.0/0"
}

variable "raw_bucket_name" {
  default = "my-spacex-raw-bucket-1234"
}