resource "aws_route53_zone" "this" {
  name          = var.domain_name
  comment       = var.comment
  force_destroy = false

  lifecycle {
    ignore_changes = [vpc]
  }
}
