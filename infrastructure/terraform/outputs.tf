output "vpc_id" {
  value = aws_vpc.main.id
}

output "ec2_public_ip" {
  value       = aws_instance.app.public_ip
  description = "SSH: ssh ec2-user@<ip> | Dashboard: http://<ip>:3000 | API: http://<ip>:8000"
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}
