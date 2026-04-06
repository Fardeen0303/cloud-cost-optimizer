resource "aws_iam_role" "cost_scanner" {
  name = "${var.project_name}-cost-scanner-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "cost_scanner" {
  name = "${var.project_name}-cost-scanner-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "rds:Describe*",
          "s3:List*",
          "cloudwatch:GetMetricStatistics",
          "ce:GetCostAndUsage"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cost_scanner" {
  role       = aws_iam_role.cost_scanner.name
  policy_arn = aws_iam_policy.cost_scanner.arn
}

resource "aws_iam_instance_profile" "cost_scanner" {
  name = "${var.project_name}-cost-scanner-profile"
  role = aws_iam_role.cost_scanner.name
}
