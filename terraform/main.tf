terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "rag_bucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.rag_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_object" "pdf" {

  bucket = aws_s3_bucket.rag_bucket.id

  key = "documents/company.pdf"

  source = var.pdf_file

  etag = filemd5(var.pdf_file)

  content_type = "application/pdf"
}