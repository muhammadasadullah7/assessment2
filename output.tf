output "bucket_domain_name" {
  value = aws_s3_bucket.www_bucket.website_endpoint
}

#value = aws_s3_bucket_website_configuration.bucket_website_configuration.website_endpoint
