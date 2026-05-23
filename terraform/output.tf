output "bucket_name" {
  value = aws_s3_bucket.rag_bucket.bucket
}

output "pdf_key" {
  value = aws_s3_object.pdf.key
}