resource "aws_amplify_app" "website" {
  name       = var.domain_name
  repository = var.repository

  platform = "WEB"

  environment_variables = {
    BASEURL = var.domain_name
  }

  custom_rule {
    source = "/.well-known/atproto-did"
    status = "200"
    target = "/well-known/atproto-did.txt"
  }

  custom_rule {
    source = "/.well-known/<*>"
    status = "200"
    target = "/well-known/<*>"
  }

  custom_rule {
    source = "/<*>"
    status = "404"
    target = "/404.html"
  }
}

resource "aws_amplify_branch" "main" {
  app_id                      = aws_amplify_app.website.id
  branch_name                 = "main"
  stage                       = "PRODUCTION"
  enable_pull_request_preview = true
  framework                   = "Web"
}

resource "aws_amplify_domain_association" "website" {
  app_id                 = aws_amplify_app.website.id
  domain_name            = var.domain_name
  enable_auto_sub_domain = true

  certificate_settings {
    custom_certificate_arn = module.acm_certificate.arn
    type                   = "CUSTOM"
  }

  sub_domain {
    branch_name = aws_amplify_branch.main.branch_name
    prefix      = ""
  }

  lifecycle {
    ignore_changes = [sub_domain]
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "amplify-redeploy-lambda-exec-${aws_amplify_app.website.id}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_amplify" {
  name = "amplify-redeploy-lambda-policy-${aws_amplify_app.website.id}"
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "amplify:StartJob"
        ],
        Effect   = "Allow",
        Resource = "${aws_amplify_app.website.arn}/*"
      },
      {
        Action = [
          "amplify:ListJobs"
        ],
        Effect   = "Allow",
        Resource = "${aws_amplify_app.website.arn}/branches/${aws_amplify_branch.main.branch_name}/jobs/*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "archive_file" "amplify_redeploy_lambda" {
  type        = "zip"
  source_file = "${path.module}/lambda/amplify_redeploy.py"
  output_path = "${path.root}/.terraform/tmp/amplify_redeploy.zip"
}

resource "aws_lambda_function" "amplify_redeploy" {
  filename         = archive_file.amplify_redeploy_lambda.output_path
  function_name    = "amplify-redeploy-${aws_amplify_app.website.id}"
  handler          = "amplify_redeploy.lambda_handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_exec.arn
  source_code_hash = archive_file.amplify_redeploy_lambda.output_base64sha256
  timeout          = 150 # 2 minutes 30 seconds
  description      = "Scheduled redeployment of the Amplify app ${aws_amplify_app.website.name}:${aws_amplify_branch.main.branch_name}"
  environment {
    variables = {
      AMPLIFY_APP_ID      = aws_amplify_app.website.id
      AMPLIFY_BRANCH_NAME = aws_amplify_branch.main.branch_name
    }
  }
}

resource "aws_cloudwatch_event_rule" "amplify_redeploy_schedule" {
  name                = "amplify-redeploy-schedule-${aws_amplify_app.website.id}"
  schedule_expression = var.amplify_redeploy_schedule_expression
}

resource "aws_cloudwatch_event_target" "amplify_redeploy_lambda" {
  rule      = aws_cloudwatch_event_rule.amplify_redeploy_schedule.name
  target_id = "amplify-redeploy-${aws_amplify_app.website.id}"
  arn       = aws_lambda_function.amplify_redeploy.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.amplify_redeploy.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.amplify_redeploy_schedule.arn
}
