variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "cost-optimizer"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "db_username" {
  default = "admin"
}

variable "db_password" {
  sensitive = true
}


variable "eks_public_access_cidrs" {
  description = "CIDRs allowed to access EKS public endpoint"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}
