variable "gh_action_role" {
  description = "AWS IAM ARN for Terraform GitHub Actions"
  type        = string
}

variable "repository" {
  description = "Source respository"
  type        = string
}

variable "domain_name" {
  description = "The domain name to host site"
  type        = string
}

variable "comment" {
  description = "AWS Route53 Hosted Zone comment"
  type        = string
}

variable "aliases" {
  description = "Additional aliases for Cloudfront"
  type        = list(string)
  default     = []
}

variable "amplify_redeploy_schedule_expression" {
  description = "The schedule expression for the Amplify redeploy event rule (default: every day at 6am UTC)"
  type        = string
  default     = "cron(0 6 * * ? *)"
}
