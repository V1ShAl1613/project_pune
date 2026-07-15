variable "kubeconfig_path" {
  type        = string
  description = "Path to the kubeconfig file for the target cluster"
  default     = "~/.kube/config"
}
