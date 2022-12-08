#certificate

resource "aws_acm_certificate" "api_cert" {
  domain_name       = "api.asadcheema.de"
  validation_method = "DNS"
}

data "aws_route53_zone" "public" {
  name         = "asadcheema.de"
  #zone_id      = "asadcheema.de"
  private_zone = false
}

resource "aws_route53_record" "api_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.public.zone_id
}

resource "aws_acm_certificate_validation" "api_cert_validation" {
  certificate_arn         = aws_acm_certificate.api_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.api_validation : record.fqdn]
}

#custom domain

resource "aws_apigatewayv2_domain_name" "api_domain_name" {
  domain_name = "api.asadcheema.de"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.api_cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }

  depends_on = [aws_acm_certificate_validation.api_cert_validation]
}

resource "aws_route53_record" "api" {
  name    = aws_apigatewayv2_domain_name.api_domain_name.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.public.zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.api_domain_name.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.api_domain_name.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

#api mapping

resource "aws_apigatewayv2_api_mapping" "api" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  domain_name = aws_apigatewayv2_domain_name.api_domain_name.id
  stage       = aws_apigatewayv2_stage.lambda_stage.id
}

resource "aws_apigatewayv2_api_mapping" "api_v1" {
  api_id          = aws_apigatewayv2_api.lambda_api.id
  domain_name     = aws_apigatewayv2_domain_name.api_domain_name.id
  stage           = aws_apigatewayv2_stage.lambda_stage.id
  api_mapping_key = "v1"
}

output "custom_domain_api" {
  value = "https://${aws_apigatewayv2_api_mapping.api.domain_name}"
}

output "custom_domain_api_v1" {
  value = "https://${aws_apigatewayv2_api_mapping.api_v1.domain_name}/${aws_apigatewayv2_api_mapping.api_v1.api_mapping_key}"
}