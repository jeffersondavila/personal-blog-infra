output "provider_ownership" {
  value = var.provider_mode == "create" ? "managed-A" : "reference-B"
}

output "trust_phase" {
  value = var.trust_phase
}
