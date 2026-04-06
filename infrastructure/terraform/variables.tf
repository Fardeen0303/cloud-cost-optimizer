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
  default = "dbadmin"
}

variable "db_password" {
  sensitive = true
}

variable "ssh_public_key_path" {
  description = "Path to your SSH public key, e.g. ~/.ssh/id_rsa.pub"
  default     = "~/.ssh/id_rsa.pub"
}
