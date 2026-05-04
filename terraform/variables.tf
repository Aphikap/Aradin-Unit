variable "namespace" {
  description = "Kubernetes namespace for the Aradin Converter app"
  type        = string
  default     = "aradin"
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig used by the kubernetes provider"
  type        = string
  default     = "~/.kube/config"
}
