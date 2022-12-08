# S3 bucket for website.

# resource "aws_iam_policy" "example" {
#   name   = "example_policy"
#   path   = "/"
#   policy = "${data.aws_iam_policy_document.example.json}"
# }

resource "aws_s3_bucket" "www_bucket" {
  bucket = var.bucket_name
  acl    = "public-read"
  #policy = data.aws_iam_policy_document.website_policy.json
  policy = data.aws_iam_policy_document.allow_public_s3_read.json
  #policy = templatefile("templates/s3-policy.json", { bucket = var.bucket_name })

  cors_rule {
    allowed_headers = ["Authorization", "Content-Length"]
    allowed_methods = ["GET", "POST"]
    allowed_origins = ["https://www.${var.domain_name}"]
    max_age_seconds = 3000
  }

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags = var.common_tags
}

resource "aws_s3_bucket_object" "index" {
  bucket       = aws_s3_bucket.www_bucket.id
  acl          = "public-read" # or can be “public-read”
  key          = "index.html"
  source       = "./index.html"
  etag         = filemd5("./error.html")
  content_type = "text/html"
}

resource "aws_s3_bucket_object" "error" {
  bucket       = aws_s3_bucket.www_bucket.id
  acl          = "public-read" # or can be “public-read”
  key          = "error.html"
  source       = "./error.html"
  etag         = filemd5("./error.html")
  content_type = "text/html"
}

# S3 Allow Public read access as data object
data "aws_iam_policy_document" "allow_public_s3_read" {
  statement {
    sid    = "PublicReadGetObject"
    effect = "Allow"

    actions = [
      "s3:GetObject",
    ]

    principals {
      identifiers = ["*"]
      type        = "AWS"
    }

    resources = [
      "arn:aws:s3:::${var.bucket_name}/*"
      #  "arn:aws:s3:::www.${var.bucket_name}/*"
    ]
  }
}

# S3 bucket for redirecting non-www to www.
# resource "aws_s3_bucket" "root_bucket" {
#   bucket = "www.${var.bucket_name}"
#   acl = "public-read"
#   policy = templatefile("templates/s3-policy.json", { bucket = "www.${var.bucket_name}" })

#   website {
#     redirect_all_requests_to = "https://www.${var.domain_name}"
#   }

#   tags = var.common_tags
# }