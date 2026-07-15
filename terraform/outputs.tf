output "release_suffix" {
  value       = random_id.suffix.hex
  description = "Unique suffix for release tracking"
}
