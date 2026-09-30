output "state_bucket_name" {
  description = "Dedicated state bucket; contains no media or application backups."
  value       = aws_s3_bucket.state.bucket
}

output "state_bucket_region" {
  value = local.region
}

output "future_state_keys" {
  description = "Reserved destinations; no objects or remote backend are created by this plan."
  value = {
    bootstrap   = local.state_key
    github_oidc = local.oidc_key
  }
}

output "future_s3_backend" {
  description = "Configuration for H-030-2; not the active backend during bootstrap."
  value = {
    bucket       = local.bucket_name
    key          = local.state_key
    region       = local.region
    encrypt      = true
    use_lockfile = true
  }
}
